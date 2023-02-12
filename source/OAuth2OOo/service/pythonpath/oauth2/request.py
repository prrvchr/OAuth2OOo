#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import uno
import unohelper

from com.sun.star.io import XInputStream
from com.sun.star.io import XOutputStream
from com.sun.star.io import XStreamListener

from com.sun.star.io import IOException
from com.sun.star.container import NoSuchElementException

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.connection import NoConnectException

from com.sun.star.auth import XRestUploader
from com.sun.star.auth import XRestEnumeration
from com.sun.star.auth import XRestRequest

from com.sun.star.auth.RestRequestTokenType import TOKEN_NONE
from com.sun.star.auth.RestRequestTokenType import TOKEN_URL
from com.sun.star.auth.RestRequestTokenType import TOKEN_REDIRECT
from com.sun.star.auth.RestRequestTokenType import TOKEN_QUERY
from com.sun.star.auth.RestRequestTokenType import TOKEN_JSON
from com.sun.star.auth.RestRequestTokenType import TOKEN_SYNC

from com.sun.star.rest import ConnectionException
from com.sun.star.rest import ConnectTimeoutException
from com.sun.star.rest import HTTPException
from com.sun.star.rest import JSONDecodeException
from com.sun.star.rest import ReadTimeoutException
from com.sun.star.rest import RequestException
from com.sun.star.rest import TooManyRedirectsException
from com.sun.star.rest import URLRequiredException

from com.sun.star.rest import XRequestResponse

from .unolib import KeyMap

from .oauth2lib import NoOAuth2

from .logger import getMessage
from .logger import logMessage
g_message = 'request'

import requests
import sys
import json


def getConnectionMode(ctx, host):
    return getSessionMode(ctx, host)

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


class Response(unohelper.Base,
               XRequestResponse):
    def __init__(self, session, parameter, timeout, parser=None):
        self._parser = parser
        self._name = parameter.Name
        kwargs = _getKeyWordArguments(parameter)
        self._response = session.request(parameter.Method, parameter.Url, timeout=timeout, **kwargs)
        print("Response.__init__() 1 \n%s\n%s" % (self._response.request.headers, self._response.request.body))
        print("Response.__init__() 2 \n%s\n%s" % (self._response.headers, self._response.content))
        self._closed = False

    def __del__(self):
        self.close()

    @property
    def Name(self):
        return self._name
    @property
    def Method(self):
        return self._response.request.method
    @property
    def StatusCode(self):
        return self._response.status_code
    @property
    def ApparentEncoding(self):
        return self._response.apparent_encoding
    @property
    def Encoding(self):
        encoding = self._response.encoding
        return '' if encoding is None else encoding
    @Encoding.setter
    def Encoding(self, encoding):
        self._response.encoding = encoding
    @property
    def Text(self):
        return self._response.text
    @property
    def Content(self):
        return uno.ByteSequence(self._response.content)
    @property
    def Data(self):
        result = None
        if self._parser is not None and self._parser.DataType.lower() != 'json':
            result = self._parser.parseResponse(self._response.content)
        return result
    @property
    def Json(self):
        if self._parser is not None and self._parser.DataType.lower() == 'json':
            keymap = KeyMap(self._response.json(object_pairs_hook=self._parser.parseResponse))
        else:
            keymap = KeyMap(self._response.json())
        return keymap
    @property
    def Ok(self):
        return self._response.ok
    @property
    def IsPermanentRedirect(self):
        return self._response.is_permanent_redirect
    @property
    def IsRedirect(self):
        return self._response.is_redirect
    @property
    def Elapsed(self):
        return self._response.elapsed

    def getHeader(self, header):
        return self._response.headers.get(header, '')

    def close(self):
        if not self._closed:
            self._response.close()
            self._closed = True


class Iterator(unohelper.Base,
               XRestEnumeration):
    def __init__(self, ctx, session, timeout, parameter, parser=None):
        self._ctx = ctx
        self.session = session
        self.timeout = timeout
        self.parameter = parameter
        self.parser = parser
        self.pagetoken = None
        self.synctoken = ''
        self.error = None
        self.row = 0
        self.page = 0
        self.next = None
        self.end = object()
        self.iterator = self._getIterator()

    @property
    def SyncToken(self):
        return self.synctoken
    @property
    def PageCount(self):
        return self.page
    @property
    def RowCount(self):
        return self.row

    # XRestEnumeration
    def hasMoreElements(self):
        self.next = next(self.iterator, self.end)
        return self.next is not self.end

    def nextElement(self):
        if self.next is not self.end:
            return self.next
        raise NoSuchElementException('no more elements exist', self)

    def _setParameter(self):
        token = self.parameter.Enumerator.Token.Type
        if token & TOKEN_URL:
            self.parameter.Url = self.parameter.Enumerator.Token.Value
        if token & TOKEN_QUERY:
            query = json.loads(self.parameter.Query)
            query.update({self.parameter.Enumerator.Token.Value: self.pagetoken})
            self.parameter.Query = json.dumps(query)
        if token & TOKEN_REDIRECT:
            self.parameter.Url = self.pagetoken
        if token & TOKEN_JSON:
            data = '{"%s": "%s"}' % (self.parameter.Enumerator.Token.Field, self.pagetoken)
            self.parameter.Json = data
        self.pagetoken = None

    def _setToken(self, response):
        token = self.parameter.Enumerator.Token
        if token.Type != TOKEN_NONE:
            if not token.IsConditional:
                if response.hasValue(token.Field):
                    self.pagetoken = response.getValue(token.Field)
            elif response.hasValue(token.ConditionField):
                if response.getValue(token.ConditionField) == token.ConditionValue:
                    self.pagetoken = response.getDefaultValue(token.Field, False)
        if token.Type & TOKEN_SYNC and response.hasValue(token.SyncField):
            self.synctoken = response.getValue(token.SyncField)
        return self.pagetoken is None

    def _getIterator(self):
        lastpage = False
        with self.session as s:
            while not lastpage:
                if self.page:
                    self._setParameter()
                self.page += 1
                lastpage = True
                response = execute(self._ctx, s, self.parameter, self.timeout, self.parser)
                if response.IsPresent:
                    result = response.Value
                    lastpage = self._setToken(result)
                    field = self.parameter.Enumerator.Field
                    if result.hasValue(field):
                        chunks = result.getValue(field)
                        self.row += len(chunks)
                        for item in chunks:
                            yield item


class Request(unohelper.Base,
              XRestRequest):
    def __init__(self, ctx, session, parameter, timeout, parser=None):
        self._ctx = ctx
        self._session = session
        self._parameter = parameter
        self._timeout = timeout
        self._parser = parser

    # XRestRequest
    def getWarnings(self):
        return None
    def clearWarnings(self):
        pass
    def execute(self):
        with self._session as s:
            response = execute(self._ctx, s, self._parameter, self._timeout, self._parser)
        return response


class Enumeration(unohelper.Base,
                  XRestEnumeration):
    def __init__(self, ctx, session, parameter, timeout, parser=None):
        self._ctx = ctx
        self._session = session
        self._parameter = parameter
        self._timeout = timeout
        self._parser = parser
        token = parameter.Enumerator.Token
        self._chunked = token.Type != TOKEN_NONE
        self._synchro = token.Type & TOKEN_SYNC
        self._token = None
        self._sync = ''
        self._PageCount = 0

    @property
    def SyncToken(self):
        return self._sync

    # XRestEnumeration
    def hasMoreElements(self):
        return self._token is None or bool(self._token)
    def nextElement(self):
        if self.hasMoreElements():
            return self._getResponse()
        raise NoSuchElementException()

    def _getResponse(self):
        token = self._parameter.Enumerator.Token
        if self._token:
            if token.Type & TOKEN_URL:
                self._parameter.Url = token.Value
            if token.Type & TOKEN_QUERY:
                query = json.loads(self._parameter.Query)
                query.update({token.Value: self._token})
                self._parameter.Query = json.dumps(query)
            if token.Type & TOKEN_REDIRECT:
                self._parameter.Url = self._token
            if token.Type & TOKEN_JSON:
                self._parameter.Json = '{"%s": "%s"}' % (token.Field, self._token)
        self._token = False
        self._sync = ''
        response = execute(self._ctx, self._session, self._parameter, self._timeout, self._parser)
        if response.IsPresent:
            r = response.Value
            #rows = list(r.getDefaultValue(self.parameter.Enumerator.Field, ()))
            if self._chunked:
                if token.IsConditional:
                    if r.getDefaultValue(token.ConditionField, None) == token.ConditionValue:
                        self._token = r.getDefaultValue(token.Field, False)
                else:
                    self._token = r.getDefaultValue(token.Field, False)
            if self._synchro:
                self._sync = r.getDefaultValue(token.SyncField, '')
        return response


class Enumerator(unohelper.Base,
                 XRestEnumeration):
    def __init__(self, ctx, session, parameter, timeout):
        self._ctx = ctx
        self._session = session
        self._parameter = parameter
        self._timeout = timeout
        token = parameter.Enumerator.Token
        self._chunked = token.Type != TOKEN_NONE
        self._synchro = token.Type & TOKEN_SYNC
        self._rows, self._token, self._sync, error = self._getRows()
        self._PageCount = 0
        if error:
            logMessage(self._ctx, SEVERE, error, "OAuth2Service","Enumerator()")

    @property
    def SyncToken(self):
        return self._sync

    # XRestEnumeration
    def hasMoreElements(self):
        return len(self._rows) > 0 or self._token is not None
    def nextElement(self):
        if self._rows:
            return self._rows.pop(0)
        elif self._token:
            self._rows, self._token, self._sync, error = self._getRows(self._token)
            if not error:
                return self.nextElement()
            logMessage(self._ctx, SEVERE, error, "OAuth2Service","Enumerator()")
        raise NoSuchElementException()

    def _getRows(self, token=None):
        try:
            token = self._parameter.Enumerator.Token
            if token:
                if token.Type & TOKEN_URL:
                    self._parameter.Url = token.Value
                if token.Type & TOKEN_QUERY:
                    query = json.loads(self._parameter.Query)
                    query.update({token.Value: token})
                    self._parameter.Query = json.dumps(query)
                if token.Type & TOKEN_REDIRECT:
                    self._parameter.Url = token
                if token.Type & TOKEN_JSON:
                    self._parameter.Json = '{"%s": "%s"}' % (token.Field, token)
                token = None
            rows = []
            sync = ''
            response = execute(self._ctx, self._session, self._parameter, self._timeout)
            if response.IsPresent:
                r = response.Value
                rows = list(r.getDefaultValue(self._parameter.Enumerator.Field, ()))
                if self._chunked:
                    if token.IsConditional:
                        if r.getDefaultValue(token.ConditionField, None) == token.ConditionValue:
                            token = r.getDefaultValue(token.Field, None)
                    else:
                        token = r.getDefaultValue(token.Field, None)
                if self._synchro:
                    sync = r.getDefaultValue(token.SyncField, '')
            return rows, token, sync, ''
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, 'OAuth2Service', 'Enumerator()')


class InputStream(unohelper.Base,
                  XInputStream):
    def __init__(self, ctx, session, parameter, chunk, buffer, timeout):
        self.downloader = Downloader(ctx, session, parameter, chunk, buffer, timeout)
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
    def __init__(self, ctx, session, parameter, chunk, buffer, timeout):
        self.ctx = ctx
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
                        msg = "getChunks() ERROR: %s - %s" % (r.status_code, r.text)
                        logMessage(self.ctx, SEVERE, msg, "OAuth2Service", "Downloader()")
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
    def __init__(self, ctx, session, parameter, size, chunk, response, timeout):
        self.ctx = ctx
        self.session = session
        self.method = parameter.Method
        self.url = parameter.Url
        self.size = size
        self.chunk = chunk
        self.chunked = size > chunk
        self.buffers = b''
        self.response = response
        self.timeout = timeout
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
                logMessage(self.ctx, SEVERE, msg, "OAuth2Service","OutputStream()")
        return


class StreamListener(unohelper.Base,
                     XStreamListener):
    def __init__(self, ctx, callback, username, itemid, response):
        self.ctx = ctx
        self.callback = callback
        self.username = username
        self.itemid = itemid
        self.response = response

    # XStreamListener
    def started(self):
        pass
    def closed(self):
        if self.response.IsPresent:
            self.callback(self.username, self.itemid, self.response)
        else:
            msg = "ERROR ..."
            logMessage(self.ctx, SEVERE, msg, "OAuth2Service","StreamListener()")
    def terminated(self):
        pass
    def error(self, error):
        msg = "ERROR ..."
        logMessage(self.ctx, SEVERE, msg, "OAuth2Service","StreamListener()")
    def disposing(self, event):
        pass


class Uploader(unohelper.Base,
               XRestUploader):
    def __init__(self, ctx, session, chunk, url, callBack, timeout):
        self.ctx = ctx
        self.session = session
        self.chunk = chunk
        self.url = url
        self.callback = callBack
        self.timeout = timeout

    def start(self, username, itemid, parameter):
        input, size = self._getInputStream(itemid)
        if size:
            optional = 'com.sun.star.beans.Optional<com.sun.star.auth.XRestKeyMap>'
            response = uno.createUnoStruct(optional)
            output = self._getOutputStream(parameter, size, response)
            listener = self._getStreamListener(username, itemid, response)
            pump = self.ctx.ServiceManager.createInstance('com.sun.star.io.Pump')
            pump.setInputStream(input)
            pump.setOutputStream(output)
            pump.addListener(listener)
            pump.start()
            return True
        return False

    def _getInputStream(self, itemid):
        url = '%s/%s' % (self.url, itemid)
        sf = self.ctx.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')
        if sf.exists(url):
            return sf.openFileRead(url), sf.getSize(url)
        return None, None

    def _getOutputStream(self, param, size, resp):
        return OutputStream(self.ctx, self.session, param, size, self.chunk, resp, self.timeout)

    def _getStreamListener(self, username, itemid, response):
        return StreamListener(self.ctx, self.callback, username, itemid, response)


def execute(ctx, session, parameter, timeout, parser=None):
    try:
        response = uno.createUnoStruct('com.sun.star.beans.Optional<com.sun.star.auth.XRestKeyMap>')
        kwargs = _getKeyWordArguments(parameter)
        with session.request(parameter.Method, parameter.Url, timeout=timeout, **kwargs) as r:
            print("request.execute() 1 \n%s" % r.text)
            r.raise_for_status()
            print("request.execute() 2 \n%s\n%s" % (r.request.headers, r.request.body))
            print("request.execute() 3 \n%s\n%s" % (r.headers, r.content))
            if parser is None:
                response.Value = _parseResponse(r)
                response.IsPresent = True
            elif parser.DataType == 'Json':
                response.Value = r.json(object_pairs_hook=parser.parseResponse)
                response.IsPresent = True
            elif parser.DataType == 'Xml':
                response.Value = parser.parseResponse(r.content)
                response.IsPresent = True
    except requests.exceptions.URLRequired as e:
        error = URLRequiredException()
        error.Url = parameter.Url
        error.Message = getMessage(ctx, g_message, 101, error.Url)
        raise error
    except requests.exceptions.ConnectTimeout as e:
        error = ConnectTimeoutException()
        error.Url = e.response.url
        connect, read = timeout
        error.ConnectTimeout = connect
        error.Message = getMessage(ctx, g_message, 102, error.ConnectTimeout, error.Url)
        raise error
    except requests.exceptions.ReadTimeout as e:
        error = ReadTimeoutException()
        error.Url = e.response.url
        connect, read = timeout
        error.ReadTimeout = read
        error.Message = getMessage(ctx, g_message, 103, error.ReadTimeout, error.Url)
        raise error
    except requests.exceptions.ConnectionError as e:
        error = ConnectionException()
        error.Url = e.response.url
        error.Message = getMessage(ctx, g_message, 104, error.Url)
        raise error
    except requests.exceptions.HTTPError as e:
        error = HTTPException()
        error.Url = e.response.url
        error.StatusCode = e.response.status_code
        error.Content = e.response.text
        error.Message = getMessage(ctx, g_message, 105, error.Url, error.StatusCode)
        raise error
    except requests.exceptions.TooManyRedirects as e:
        error = TooManyRedirectsException()
        error.Url = e.response.url
        error.Message = getMessage(ctx, g_message, 106, error.Url)
        raise error
    except requests.exceptions.JSONDecodeError as e:
        error = JSONDecodeException()
        error.Url = e.response.url
        error.Content = e.response.text
        error.Message = getMessage(ctx, g_message, 107, error.Url)
        raise error
    except requests.exceptions.RequestException as e:
        error = RequestException()
        error.Url = e.response.url
        error.Message = getMessage(ctx, g_message, 108, error.Url)
        raise error
    return response

# Private method
def _getKeyWordArguments(parameter):
    kwargs = {}
    if parameter.Header:
        kwargs['headers'] = json.loads(parameter.Header)
    if parameter.Query:
        kwargs['params'] = json.loads(parameter.Query)
    if parameter.Data:
        kwargs['data'] = parameter.Data
    elif parameter.Json:
        kwargs['json'] = json.loads(parameter.Json)
    if parameter.NoAuth:
        kwargs['auth'] = NoOAuth2()
    elif parameter.Auth:
        kwargs['auth'] = parameter.Auth
    if parameter.NoRedirect:
        kwargs['allow_redirects'] = False
    if parameter.NoVerify:
        kwargs['verify'] = False
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
        keymap.setValue(key, value)
    return keymap
