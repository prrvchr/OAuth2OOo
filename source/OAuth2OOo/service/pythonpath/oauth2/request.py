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

from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.ucb.ConnectionMode import OFFLINE

from com.sun.star.connection import NoConnectException

from com.sun.star.rest.ParameterType import QUERY
from com.sun.star.rest.ParameterType import JSON
from com.sun.star.rest.ParameterType import HEADER

from com.sun.star.rest import ConnectionException
from com.sun.star.rest import ConnectTimeoutException
from com.sun.star.rest import HTTPException
from com.sun.star.rest import JSONDecodeException
from com.sun.star.rest import ReadTimeoutException
from com.sun.star.rest import RequestException
from com.sun.star.rest import TooManyRedirectsException
from com.sun.star.rest import URLRequiredException

from .oauth2 import NoOAuth2

from .requestresponse import RequestResponse
from .requestresponse import getExceptionMessage

import requests
import json
import traceback


class InputStream(unohelper.Base,
                  XInputStream):
    def __init__(self, session, parameter, timeout, chunk, decode):
        kwargs = _getKeyWordArguments(parameter)
        kwargs['stream'] = True
        self._response = session.request(parameter.Method, parameter.Url, timeout=timeout, **kwargs)
        self._iterator = self._response.iter_content(chunk, decode)
        self._chunk = chunk
        self._buffer = b''

    #XInputStream
    def readBytes(self, sequence, length):
        sequence = uno.ByteSequence(self._readBytes(length))
        return len(sequence), sequence

    def readSomeBytes(self, sequence, length):
        return self.readBytes(sequence, length)

    def skipBytes(self, length):
        self._readBytes(length)

    def available(self):
        return self._chunk

    def closeInput(self):
        self._response.close()

    def _readBytes(self, length):
        buffer = self._buffer
        size = len(buffer)
        if size < length:
            try:
                while size < length:
                    chunk = next(self._iterator)
                    buffer += chunk
                    size += len(chunk)
            except StopIteration:
                pass
        self._buffer = buffer[length:]
        return buffer[:length]


class FileLike():
    def __init__(self, input):
        self._input = input

    # Python FileLike Object
    def read(self, length):
        length, sequence = self._input.readBytes(None, length)
        return sequence.value

    def close(self):
        self._input.closeInput()

    def seek(self, offset, whence=0):
        if whence == 1:
            offset = self._input.getPosition() + offset
        elif whence == 2:
            offset = self._input.getLength() - offset
        self._input.seek(offset)

    def tell(self):
        return self._input.getPosition()


def execute(ctx, session, parameter, timeout):
    try:
        print("Request.executeRequest() 1")
        kwargs = _getKeyWordArguments(parameter)
        print("Request.executeRequest() 2")
        with session.request(parameter.Method, parameter.Url, timeout=timeout, **kwargs) as r:
            print("Request.executeRequest() 3")
            response = RequestResponse(ctx, parameter, r)
        print("Request.executeRequest() 4")
    except requests.exceptions.URLRequired as e:
        error = URLRequiredException()
        error.Url = parameter.Url
        error.Message = getExceptionMessage(ctx, 'OAuth2Service', 'execute()', 101, error.Url)
        raise error
    except requests.exceptions.ConnectTimeout as e:
        error = ConnectTimeoutException()
        error.Url = e.response.url
        connect, read = timeout
        error.ConnectTimeout = connect
        error.Message = getExceptionMessage(ctx, 'OAuth2Service', 'execute()', 102, error.ConnectTimeout, error.Url)
        raise error
    except requests.exceptions.ReadTimeout as e:
        error = ReadTimeoutException()
        error.Url = e.response.url
        connect, read = timeout
        error.ReadTimeout = read
        error.Message = getExceptionMessage(ctx, 'OAuth2Service', 'execute()', 103, error.ReadTimeout, error.Url)
        raise error
    except requests.exceptions.ConnectionError as e:
        error = ConnectionException()
        error.Url = e.response.url
        error.Message = getExceptionMessage(ctx, 'OAuth2Service', 'execute()', 104, error.Url)
        raise error
    except requests.exceptions.TooManyRedirects as e:
        error = TooManyRedirectsException()
        error.Url = e.response.url
        error.Message = getExceptionMessage(ctx, 'OAuth2Service', 'execute()', 106, error.Url)
        raise error
    except requests.exceptions.RequestException as e:
        error = RequestException()
        error.Url = e.response.url
        error.Message = getExceptionMessage(ctx, 'OAuth2Service', 'execute()', 108, error.Url)
        raise error
    return response


def upload(session, parameter, stream, timeout):
    kwargs = _getKeyWordArguments(parameter)
    kwargs['data'] = FileLike(stream)
    response = session.request(parameter.Method, parameter.Url, timeout=timeout, **kwargs)
    response.close()


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


# Private method
def _getKeyWordArguments(parameter):
    kwargs = {}
    if parameter.Headers:
        data = json.loads(parameter.Headers)
        if parameter.PageType == HEADER:
            data.update({parameter.PageKey: parameter.PageValue})
        kwargs['headers'] = data
    if parameter.Query:
        data = json.loads(parameter.Query)
        if parameter.PageType == QUERY:
            data.update({parameter.PageKey: parameter.PageValue})
        kwargs['params'] = data
    if parameter.Data:
        kwargs['data'] = parameter.Data
    elif parameter.Json:
        data = json.loads(parameter.Json)
        if parameter.PageType == JSON:
            data.update({parameter.PageKey: parameter.PageValue})
        kwargs['json'] = data
    elif parameter.DataSink:
        kwargs['data'] = FileLike(parameter.DataSink)
    if parameter.NoAuth:
        kwargs['auth'] = NoOAuth2()
    elif parameter.Auth:
        kwargs['auth'] = parameter.Auth
    if parameter.NoRedirect:
        kwargs['allow_redirects'] = False
    if parameter.NoVerify:
        kwargs['verify'] = False
    if parameter.Stream:
        kwargs['stream'] = True
    return kwargs

