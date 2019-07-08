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
g_timeout = (15, 60)


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

def execute(session, parameter):
    response = uno.createUnoStruct('com.sun.star.beans.Optional<com.sun.star.auth.XRestKeyMap>')
    kwargs = _getKeyWordArguments(parameter)
    kwargs.update({'timeout': g_timeout})
    print("Request.execute(): Url: %s \n%s" % (parameter.Url, kwargs))
    with session as s:
        with s.request(parameter.Method, parameter.Url, **kwargs) as r:
            print("Request.execute(): %s\n%s" % (r.status_code, r.headers))
            if r.status_code in (s.codes.ok, s.codes.found, s.codes.created, s.codes.accepted):
                response.IsPresent = True
                content = r.headers.get('Content-Type', '')
                if content.startswith('application/json'):
                    print("Request.execute(): \n%s" % (r.json(), ))
                response.Value = _parseResponse(r)
                print("Request.execute(): **********************")
            else:
                print("Request.execute(): ERROR: %s\n%s" % (r.status_code, r.text))
    return response


class Enumerator(unohelper.Base,
                 XEnumeration):
    def __init__(self, session, parameter, logger):
        self.session = session
        self.parameter = parameter
        self.logger = logger
        self.chunked = self.parameter.Enumerator.Token.Type != TOKEN_NONE
        self.elements, self.token = self._getElements()
        msg = "Loading ... Done"
        self.logger.logp(INFO, "OAuth2Service", "getEnumerator()", msg)

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
        msg = "_getElements() 1"
        self.logger.logp(INFO, "OAuth2Service", "getEnumerator()", msg)
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
        msg = "_getElements() 2"
        self.logger.logp(INFO, "OAuth2Service", "getEnumerator()", msg)
        response = execute(self.session, self.parameter)
        msg = "_getElements() 3"
        self.logger.logp(INFO, "OAuth2Service", "getEnumerator()", msg)
        if response.IsPresent:
            msg = "_getElements() 4"
            self.logger.logp(INFO, "OAuth2Service", "getEnumerator()", msg)
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
        msg = "_getElements() 5"
        self.logger.logp(INFO, "OAuth2Service", "getEnumerator()", msg)
        return elements, token


class InputStream(unohelper.Base,
                  XInputStream):
    def __init__(self, session, parameter, chunk, buffer):
        self.downloader = Downloader(session, parameter, chunk, buffer)
        self.chunks = self.downloader.getChunks()
        self.buffers = b''
        print("Request.InputStream.__init__()")

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
            print("Request.InputStream.readBytes()1: %s - %s" % (j, length))
            if j == 0:
                break
            elif j > i:
                sequence += chunk[:i]
                self.buffers = chunk[i:]
                break
            sequence += chunk
            i = length - len(sequence)
        print("Request.InputStream.readBytes()2: %s - %s" % (length, len(sequence)))
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
    def __init__(self, session, parameter, chunk, buffer):
        print("Request.Downloader.__init__() 1")
        self.session = session
        self.method = parameter.Method
        self.url = parameter.Url
        kwargs = _getKeyWordArguments(parameter)
        kwargs.update({'timeout': g_timeout, 'stream': True})
        # We need to use a "Range" Header... but it's not shure that parameter has Headers...
        if 'headers' not in kwargs:
            kwargs.update({'headers': {}})
        self.kwargs = kwargs
        self.chunk = chunk
        self.buffer = buffer
        self.start = 0
        self.size = 0
        self.closed = False
        print("Request.Downloader.__init__() 2 - %s" % self.size)
    def _getSize(self, range):
        if range:
            return int(range.split('/').pop())
        return 0
    def _closed(self):
        return self.start == self.size if self.size else self.closed
    def getChunks(self):
        print("Request.Downloader.__next__() 1")
        with self.session as s:
            while not self._closed():
                end = self.start + self.chunk
                if self.size:
                    end = min(end, self.size)
                self.kwargs['headers'].update({'Range': 'bytes=%s-%s' % (self.start, end -1)})
                print("Request.Downloader.__next__() 3: %s" % (self.kwargs['headers'], ))
                with s.request(self.method, self.url, **self.kwargs) as r:
                    print("Request.Downloader.__next__() 4: %s \n%s\n%s" % (r.status_code, r.request.headers, r.headers))
                    if r.status_code == s.codes.ok:
                        self.closed = True
                    elif r.status_code == s.codes.partial_content:
                        if self.size == 0:
                            self.size = self._getSize(r.headers.get('Content-Range'))
                    else:
                        self.closed = True
                        print("Request.Downloader.__next__() 5 %s - %s" % (self.closed, self.start))
                        print("Request.Downloader ERROR %s \n%s" % (r.status_code, r.text))
                        break
                    for c in r.iter_content(self.buffer):
                        self.start += len(c)
                        print("Request.Downloader.__next__() 6 %s - %s" % (len(c), self.start))
                        yield c
        print("Request.Downloader.__next__() 6")
    def close(self):
        self.session.close()
        self.closed = True
    def available(self):
        return 0 if self.closed else self.chunk
    def skip(self, length):
        self.start += length


class OutputStream(unohelper.Base,
                   XOutputStream):
    def __init__(self, session, parameter, size, chunk, response):
        self.session = session
        self.method = parameter.Method
        self.url = parameter.Url
        self.size = size
        self.chunk = chunk
        self.chunked = size > chunk
        self.buffers = b''
        self.response = response
        print("OutputStream.__init__() *******************************\n%s" % self.response)

        kwargs = _getKeyWordArguments(parameter)
        kwargs.update({'timeout': g_timeout})
        # If Chunked we need to use a "Content-Range" Header...
        # but it's not shure that parameter has Headers...
        if self.chunked and 'headers' not in kwargs:
            kwargs.update({'headers': {}})
        self.kwargs = kwargs
        self.start = 0
        self.closed = False
        self.error = ''
        print("Request.OutputStream.__init__() %s" % size)

    @property
    def length(self):
        return len(self.buffers)

    # XOutputStream
    def writeBytes(self, sequence):
        if self.closed:
            print("gdrive.OutputStream.writeBytes(): ERROR %s" % self.length)
            raise IOException('OutputStream is closed...', self)
        self.buffers += sequence.value
        if self._flushable():
            self._flush()
            print("gdrive.OutputStream.writeBytes(): %s" % self.length)
            #raise IOException('Error Uploading file...', self)
        else:
            print("gdrive.OutputStream.writeBytes() Bufferize: %s - %s" % (self.start, self.length))
    def flush(self):
        print("gdrive.OutputStream.flush() 1")
        if self.closed:
            print("gdrive.OutputStream.flush() ERROR")
            raise IOException('OutputStream is closed...', self)
        if self._flushable(True):
            self._flush()
            print("gdrive.OutputStream.flush() 2")
            #raise IOException('Error Uploading file...', self)
    def closeOutput(self):
        print("gdrive.OutputStream.closeOutput() 1")
        self.closed = True
        if self._flushable(True):
            print("gdrive.OutputStream.closeOutput() 2")
            self._flush()
            print("gdrive.OutputStream.closeOutput() 3")
        self.session.close()
        if self.error:
            print("gdrive.OutputStream.closeOutput() ERROR")
            raise IOException('Error Uploading file...', self)
    def _flushable(self, last=False):
        if last:
            return self.length > 0
        elif self.chunked:
            return self.length >= self.chunk
        return False
    def _flush(self):
        print("gdrive.OutputStream._write() 1: %s" % (self.start, ))
        end = self.start + self.length -1
        #end = 100
        header = {}
        if self.chunked:
            header = {'Content-Range': 'bytes %s-%s/%s' % (self.start, end, self.size)}
            self.kwargs['headers'].update(header)
        self.kwargs.update({'data': self.buffers})
        print("gdrive.OutputStream._write() 2: %s - %s - %s\n%s" % \
            (self.chunked, self.length, self.size, header))
        with self.session.request(self.method, self.url, **self.kwargs) as r:
            print("gdrive.OutputStream._write() 3: %s" % (r.request.headers, ))
            print("gdrive.OutputStream._write() 4: %s - %s" % (r.status_code, r.headers))
            if r.status_code == self.session.codes.ok:
                print("gdrive.OutputStream._write() 5: %s" % (r.json(), ))
                self.response.IsPresent = True
                self.response.Value = _parseResponse(r)
                self.start = end
                self.buffers = b''
                print("gdrive.OutputStream._write() 6: %s" % (self.response, ))
            elif r.status_code == self.session.codes.created:
                print("gdrive.OutputStream._write() 7: %s" % (r.json(), ))
                self.response.IsPresent = True
                self.response.Value = _parseResponse(r)
                self.start = end
                self.buffers = b''
                print("gdrive.OutputStream._write() 8: %s" % (self.response, ))
            elif r.status_code == self.session.codes.permanent_redirect:
                print("gdrive.OutputStream._write() 9: %s" % (r.json(), ))
                if 'Range' in r.headers:
                    self.start += int(r.headers['Range'].split('-')[-1]) +1
                    self.buffers = b''
            else:
                error = 'Error : %s' % r.text
                self.response.Value = KeyMap()
                self.response.Value.insertValue('Error', error)
                print("gdrive.OutputStream._write() 10 ERROR: \n%s" % error)
                #raise IOException
        return


class StreamListener(unohelper.Base,
                     XStreamListener):
    def __init__(self, datasource, item, response):
        self.datasource = datasource
        self.item = item
        self.response = response
        print("StreamListener.__init__() *******************************\n%s" % self.response)

    # XStreamListener
    def started(self):
        print("StreamListener.started() *****************************************************")
    def closed(self):
        print("StreamListener.closed() *****************************************************")
        try:
            print("StreamListener.closed() 1 %s\n%s" % (self.response, self.response.IsPresent))
            for i in range(self.response.Value.Count):
                key = self.response.Value.getKeyByIndex(i)
                value = self.response.Value.getValue(key)
                print("Response: Name: %s - Value: %s" % (key, value))
            print("StreamListener.closed() 2")
            self.datasource.callBack(self.item, self.response)
            print("StreamListener.closed(): ***********************************************")
        except Exception as e:
            print("ProviderBase.closed().Error: %s - %s" % (e, traceback.print_exc()))

    def terminated(self):
        pass
    def error(self, error):
        print("StreamListener.error() *****************************************************")
    def disposing(self, event):
        pass


class Uploader(unohelper.Base,
               XRestUploader):
    def __init__(self, ctx, session, datasource):
        print("Uploader.__init__() 1")
        self.ctx = ctx
        self.session = session
        self.datasource = datasource
        self.chunk = datasource.Provider.Chunk
        self.url = datasource.Provider.SourceURL
        print("Uploader.__init__() FIN")

    def start(self, item, parameter):
        try:
            print("Uploader.start() 1")
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
                print("Uploader.start() 1")
                return True
            print("Uploader.start() FIN")
            return False
        except Exception as e:
            print("Uploader.start().Error: %s - %s" % (e, traceback.print_exc()))

    def _getInputStream(self, item):
        url = '%s/%s' % (self.url, item.getValue('Id'))
        sf = self.ctx.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')
        if sf.exists(url):
            return sf.openFileRead(url), sf.getSize(url)
        return None, None

    def _getOutputStream(self, parameter, size, response):
        return OutputStream(self.session, parameter, size, self.chunk, response)

    def _getStreamListener(self, item, response):
        return StreamListener(self.datasource, item, response)


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
