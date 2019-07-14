#!
# -*- coding: utf-8 -*-

import uno
import unohelper

from com.sun.star.io import XInputStream
from com.sun.star.io import XOutputStream
from com.sun.star.io import XStreamListener

from com.sun.star.io import IOException
from com.sun.star.container import XEnumeration
from com.sun.star.container import NoSuchElementException

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.connection import NoConnectException

from com.sun.star.auth import XRestUploader
from com.sun.star.auth.RestRequestTokenType import TOKEN_NONE
from com.sun.star.auth.RestRequestTokenType import TOKEN_URL
from com.sun.star.auth.RestRequestTokenType import TOKEN_REDIRECT
from com.sun.star.auth.RestRequestTokenType import TOKEN_QUERY
from com.sun.star.auth.RestRequestTokenType import TOKEN_JSON

from .keymap import KeyMap

import traceback
import sys
import json

# Request / OAuth2 configuration
g_auth = 'com.gmail.prrvchr.extensions.OAuth2OOo'


def getSessionMode(ctx, host, port=80):
    connector = ctx.ServiceManager.createInstance('com.sun.star.connection.Connector')
    try:
        connection = connector.connect('socket,host=%s,port=%s' % (host, port))
    except NoConnectException:
        mode = OFFLINE
    else:
        connection.close()
        mode = ONLINE
    return mode

def execute(session, parameter, timeout, logger):
    response = uno.createUnoStruct('com.sun.star.beans.Optional<com.sun.star.auth.XRestKeyMap>')
    kwargs = _getKeyWordArguments(parameter)
    with session as s:
        with s.request(parameter.Method, parameter.Url, timeout=timeout, **kwargs) as r:
            if r.status_code in (s.codes.ok, s.codes.found, s.codes.created, s.codes.accepted):
                response.IsPresent = True
                response.Value = _parseResponse(r)
            else:
                msg = "Request: %s - ERROR: %s - %s" % (parameter.Name, r.status_code, r.text)
                logger.logp(SEVERE, "OAuth2Service", "execute()", msg)
    return response


class Enumerator(unohelper.Base,
                 XEnumeration):
    def __init__(self, session, parameter, timeout, logger):
        self.session = session
        self.parameter = parameter
        self.timeout = timeout
        self.logger = logger
        self.chunked = self.parameter.Enumerator.Token.Type != TOKEN_NONE
        self.elements, self.token = self._getElements()

    # XEnumeration
    def hasMoreElements(self):
        return len(self.elements) > 0 or self.token is not None
    def nextElement(self):
        if self.elements:
            return self.elements.pop(0)
        elif self.token:
            self.elements, self.token = self._getElements(self.token)
            return self.nextElement()
        raise NoSuchElementException()

    def _getElements(self, token=None):
        if token:
            if self.parameter.Enumerator.Token.Type & TOKEN_URL:
                self.parameter.Url = self.parameter.Enumerator.Token.Value
            if self.parameter.Enumerator.Token.Type & TOKEN_QUERY:
                query = json.loads(self.parameter.Query)
                query.update({self.parameter.Enumerator.Token.Value: token})
                self.parameter.Query = json.dumps(query)
            if self.parameter.Enumerator.Token.Type & TOKEN_REDIRECT:
                self.parameter.Url = token
            if self.parameter.Enumerator.Token.Type & TOKEN_JSON:
                name = self.parameter.Enumerator.Token.Field
                self.parameter.Json = '{"%s": "%s"}' % (name, token)
            token = None
        elements = []
        response = execute(self.session, self.parameter, self.timeout, self.logger)
        if response.IsPresent:
            r = response.Value
            elements = list(r.getDefaultValue(self.parameter.Enumerator.Field, ()))
            if self.chunked:
                if self.parameter.Enumerator.Token.IsConditional:
                    field = self.parameter.Enumerator.Token.ConditionField
                    value = self.parameter.Enumerator.Token.ConditionValue
                    if r.getDefaultValue(field, None) == value:
                        token = r.getDefaultValue(self.parameter.Enumerator.Token.Field, None)
                else:
                    token = r.getDefaultValue(self.parameter.Enumerator.Token.Field, None)
        return elements, token


class InputStream(unohelper.Base,
                  XInputStream):
    def __init__(self, session, parameter, chunk, buffer, timeout, logger):
        self.downloader = Downloader(session, parameter, chunk, buffer, timeout, logger)
        self.chunks = self.downloader.getChunks()
        self.buffers = b''

    #XInputStream
    def readBytes(self, sequence, length):
        i = length - len(self.buffers)
        if i < 0:
            j = abs(i)
            sequence = uno.ByteSequence(self.buffers[:j])
            self.buffers = self.buffers[j:]
            return len(sequence), sequence
        sequence = uno.ByteSequence(self.buffers)
        self.buffers = b''
        while i > 0:
            chunk = next(self.chunks, b'')
            j = len(chunk)
            if j == 0:
                break
            elif j > i:
                sequence += chunk[:i]
                self.buffers = chunk[i:]
                break
            sequence += chunk
            i = length - len(sequence)
        return len(sequence), sequence
    def readSomeBytes(self, sequence, length):
        return self.readBytes(sequence, length)
    def skipBytes(self, length):
        self.downloader.skip(length)
    def available(self):
        return self.downloader.available()
    def closeInput(self):
        self.downloader.close()


class Downloader():
    def __init__(self, session, parameter, chunk, buffer, timeout, logger):
        self.session = session
        self.method = parameter.Method
        self.url = parameter.Url
        kwargs = _getKeyWordArguments(parameter)
        kwargs.update({'stream': True})
        # We need to use a "Range" Header... but it's not shure that parameter has Headers...
        if 'headers' not in kwargs:
            kwargs.update({'headers': {}})
        self.kwargs = kwargs
        self.chunk = chunk
        self.buffer = buffer
        self.timeout = timeout
        self.logger = logger
        self.start = 0
        self.size = 0
        self.closed = False
    def _getSize(self, range):
        if range:
            return int(range.split('/').pop())
        return 0
    def _closed(self):
        return self.start == self.size if self.size else self.closed
    def getChunks(self):
        with self.session as s:
            while not self._closed():
                end = self.start + self.chunk
                if self.size:
                    end = min(end, self.size)
                self.kwargs['headers'].update({'Range': 'bytes=%s-%s' % (self.start, end -1)})
                with s.request(self.method, self.url, timeout=self.timeout, **self.kwargs) as r:
                    if r.status_code == s.codes.ok:
                        self.closed = True
                    elif r.status_code == s.codes.partial_content:
                        if self.size == 0:
                            self.size = self._getSize(r.headers.get('Content-Range'))
                    else:
                        self.closed = True
                        msg = "getChunks() ERROR: %s" % (r.status_code, r.text)
                        self.logger.logp(SEVERE, "OAuth2Service", "Downloader()", msg)
                        break
                    for c in r.iter_content(self.buffer):
                        self.start += len(c)
                        yield c
    def close(self):
        self.session.close()
        self.closed = True
    def available(self):
        return 0 if self.closed else self.chunk
    def skip(self, length):
        self.start += length


class OutputStream(unohelper.Base,
                   XOutputStream):
    def __init__(self, session, parameter, size, chunk, response, timeout, logger):
        self.session = session
        self.method = parameter.Method
        self.url = parameter.Url
        self.size = size
        self.chunk = chunk
        self.chunked = size > chunk
        self.buffers = b''
        self.response = response
        self.timeout = timeout
        self.logger = logger
        kwargs = _getKeyWordArguments(parameter)
        # If Chunked we need to use a "Content-Range" Header...
        # but it's not shure that parameter has Headers...
        if self.chunked and 'headers' not in kwargs:
            kwargs.update({'headers': {}})
        self.kwargs = kwargs
        self.start = 0
        self.closed = False
        self.error = ''

    @property
    def length(self):
        return len(self.buffers)

    # XOutputStream
    def writeBytes(self, sequence):
        if self.closed:
            raise IOException('OutputStream is closed...', self)
        self.buffers += sequence.value
        if self._flushable():
            self._flush()
    def flush(self):
        if self.closed:
            raise IOException('OutputStream is closed...', self)
        if self._flushable(True):
            self._flush()
    def closeOutput(self):
        self.closed = True
        if self._flushable(True):
            self._flush()
        self.session.close()
        if self.error:
            raise IOException('Error Uploading file...', self)
    def _flushable(self, last=False):
        if last:
            return self.length > 0
        elif self.chunked:
            return self.length >= self.chunk
        return False
    def _flush(self):
        end = self.start + self.length -1
        header = {}
        if self.chunked:
            header = {'Content-Range': 'bytes %s-%s/%s' % (self.start, end, self.size)}
            self.kwargs['headers'].update(header)
        self.kwargs.update({'data': self.buffers})
        with self.session.request(self.method, self.url, timeout=self.timeout, **self.kwargs) as r:
            if r.status_code == self.session.codes.ok:
                self.response.IsPresent = True
                self.response.Value = _parseResponse(r)
                self.start = end
                self.buffers = b''
            elif r.status_code == self.session.codes.created:
                self.response.IsPresent = True
                self.response.Value = _parseResponse(r)
                self.start = end
                self.buffers = b''
            elif r.status_code == self.session.codes.permanent_redirect:
                if 'Range' in r.headers:
                    self.start += int(r.headers['Range'].split('-')[-1]) +1
                    self.buffers = b''
            else:
                msg = 'ERROR: %s - %s' % (r.status_code, r.text)
                self.logger.logp(SEVERE, "OAuth2Service","OutputStream()", msg)
        return


class StreamListener(unohelper.Base,
                     XStreamListener):
    def __init__(self, callback, item, response, logger):
        self.callback = callback
        self.item = item
        self.response = response
        self.logger = logger

    # XStreamListener
    def started(self):
        pass
    def closed(self):
        if self.response.IsPresent:
            self.callback(self.item, self.response)
        else:
            msg = "ERROR ..."
            self.logger.logp(SEVERE, "OAuth2Service","StreamListener()", msg)
    def terminated(self):
        pass
    def error(self, error):
        msg = "ERROR ..."
        self.logger.logp(SEVERE, "OAuth2Service","StreamListener()", msg)
    def disposing(self, event):
        pass


class Uploader(unohelper.Base,
               XRestUploader):
    def __init__(self, ctx, session, datasource, timeout):
        self.ctx = ctx
        self.session = session
        self.chunk = datasource.Provider.Chunk
        self.url = datasource.Provider.SourceURL
        self.callback = datasource.callBack
        self.logger = datasource.Logger
        self.timeout = timeout

    def start(self, item, parameter):
        input, size = self._getInputStream(item)
        if size:
            optional = 'com.sun.star.beans.Optional<com.sun.star.auth.XRestKeyMap>'
            response = uno.createUnoStruct(optional)
            output = self._getOutputStream(parameter, size, response)
            listener = self._getStreamListener(item, response)
            pump = self.ctx.ServiceManager.createInstance('com.sun.star.io.Pump')
            pump.setInputStream(input)
            pump.setOutputStream(output)
            pump.addListener(listener)
            pump.start()
            return True
        return False

    def _getInputStream(self, item):
        url = '%s/%s' % (self.url, item.getValue('Id'))
        sf = self.ctx.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')
        if sf.exists(url):
            return sf.openFileRead(url), sf.getSize(url)
        return None, None

    def _getOutputStream(self, param, size, resp):
        return OutputStream(self.session, param, size, self.chunk, resp, self.timeout, self.logger)

    def _getStreamListener(self, item, response):
        return StreamListener(self.callback, item, response, self.logger)


# Private method

def _getKeyWordArguments(parameter):
    kwargs = {}
    if parameter.Header:
        kwargs['headers'] = json.loads(parameter.Header)
    if parameter.Query:
        kwargs['params'] = json.loads(parameter.Query)
    if parameter.Data:
        kwargs['data'] = json.loads(parameter.Data)
    if parameter.Json:
        kwargs['json'] = json.loads(parameter.Json)
    if parameter.NoAuth:
        kwargs['auth'] = NoOAuth2()
    if parameter.NoRedirect:
        kwargs['allow_redirects'] = False
    return kwargs

def _parseResponse(response):
    content = response.headers.get('Content-Type', '')
    if content.startswith('application/json'):
        result = response.json(object_pairs_hook=_jsonParser)
    else:
        result = KeyMap(**response.headers)
    return result

def _jsonParser(data):
    keymap = KeyMap()
    for key, value in data:
        if isinstance(value, list):
            value = tuple(value)
        keymap.insertValue(key, value)
    return keymap


class NoOAuth2(object):
    def __call__(self, request):
        return request


# Wrapper to make callable OAuth2Service
class OAuth2OOo(NoOAuth2):
    def __init__(self, oauth2):
        self.oauth2 = oauth2

    def __call__(self, request):
        request.headers['Authorization'] = self.oauth2.getToken('Bearer %s')
        return request
