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

from com.sun.star.container import XEnumeration
from com.sun.star.container import NoSuchElementException

from com.sun.star.io import XInputStream
from com.sun.star.io import XSeekableInputStream

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.rest.ParameterType import URL
from com.sun.star.rest.ParameterType import JSON
from com.sun.star.rest.ParameterType import QUERY
from com.sun.star.rest.ParameterType import HEADER
from com.sun.star.rest.ParameterType import REDIRECT

from com.sun.star.rest import ConnectionException
from com.sun.star.rest import ConnectTimeoutException
from com.sun.star.rest import HTTPException
from com.sun.star.rest import InvalidURLException
from com.sun.star.rest import JSONDecodeException
from com.sun.star.rest import ReadTimeoutException
from com.sun.star.rest import RequestException
from com.sun.star.rest import TooManyRedirectsException
from com.sun.star.rest import URLRequiredException

from com.sun.star.rest import XRequestResponse

from .oauth2 import NoOAuth2

from .logger import getLogger

from .json import getJsonStructure

from .configuration import g_errorlog
from .configuration import g_basename

from requests.exceptions import ConnectionError
from requests.exceptions import ConnectTimeout
from requests.exceptions import HTTPError
from requests.exceptions import InvalidURL
from requests.exceptions import ReadTimeout
from requests.exceptions import RequestException as RequestError
from requests.exceptions import TooManyRedirects
from requests.exceptions import URLRequired
import json
# FIXME: If you have Python Requests installed and its version is lower than 2.27.0
# FIXME: then we cannot import JSONDecoderError it is not yet available
# from requests.exceptions import JSONDecodeError
from json.decoder import JSONDecodeError
from urllib.parse import parse_qs
import traceback


def getDuration(delta):
    days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds % 3600 // 60
    seconds = delta.seconds - hours * 3600 - minutes * 60
    duration = uno.createUnoStruct('io.github.prrvchr.css.util.Duration')
    duration.Days = days
    duration.Hours = hours
    duration.Minutes = minutes
    duration.Seconds = seconds
    duration.NanoSeconds = delta.microseconds * 1000
    return duration


def execute(ctx, source, session, cls, mtd, parameter, timeout, stream=False):
    kwargs = getKwArgs(parameter, stream)
    return getResponse(ctx, source, session, cls, mtd, parameter.Name, parameter.Method, parameter.Url, timeout, kwargs)


def getKwArgs(parameter, stream=False):
    args = parameter.toJson(stream)
    print("Request.getKWArgs() Args: %s" % args)
    kwargs = json.loads(args)
    if parameter.NoAuth:
        print("Request.getKWArgs() NoAuth")
        kwargs['auth'] = NoOAuth2()
    elif parameter.Auth:
        print("Request.getKWArgs() Auth")
        kwargs['auth'] = parameter.Auth
    if parameter.DataSink:
        print("Request.getKWArgs() DataSink")
        kwargs['data'] = FileLike(parameter.DataSink)
    elif parameter.Data:
        print("Request.getKWArgs() Data")
        kwargs['data'] = parameter.Data.value
    elif parameter.Text:
        print("Request.getKWArgs() Text")
        kwargs['data'] = parameter.Text
    return kwargs


def getResponse(ctx, source, session, cls, mtd, name, method, url, timeout, kwargs):
    response = None
    cls, mtd = 'OAuth2Service', 'executeRequest()'
    print("Request.executeRequest() 1")
    try:
        response = session.request(method, url, timeout=timeout, **kwargs)
        print("Request.executeRequest() 2")
    except URLRequired as e:
        error = URLRequiredException()
        error.Context = source
        error.Url = url
        error.Message = getExceptionMessage(ctx, cls, mtd, 101, name, error.Url)
        raise error
    except InvalidURL as e:
        error = InvalidURLException()
        error.Context = source
        error.Url = url
        error.Message = getExceptionMessage(ctx, cls, mtd, 101, name, error.Url)
        raise error
    except ConnectTimeout as e:
        error = ConnectTimeoutException()
        error.Context = source
        error.Url = url
        connect, read = timeout
        error.ConnectTimeout = connect
        error.Message = getExceptionMessage(ctx, cls, mtd, 102, error.ConnectTimeout, name, error.Url)
        raise error
    except ReadTimeout as e:
        error = ReadTimeoutException()
        error.Context = source
        error.Url = url
        connect, read = timeout
        error.ReadTimeout = read
        error.Message = getExceptionMessage(ctx, cls, mtd, 103, error.ReadTimeout, name, error.Url)
        raise error
    except ConnectionError as e:
        error = ConnectionException()
        error.Context = source
        error.Url = url
        error.Message = getExceptionMessage(ctx, cls, mtd, 104, name, error.Url)
        raise error
    except TooManyRedirects as e:
        error = TooManyRedirectsException()
        error.Context = source
        error.Url = url
        error.Message = getExceptionMessage(ctx, cls, mtd, 106, name, error.Url)
        raise error
    except RequestError as e:
        error = RequestException()
        error.Context = source
        error.Url = url
        text = '' if response is None else response.text
        error.Message = getExceptionMessage(ctx, cls, mtd, 107, name, error.Url, text)
        raise error
    print("Request.executeRequest() 3")
    return response


def getRequestResponse(ctx, source, session, cls, mtd, parameter, timeout):
    response = execute(ctx, source, session, cls, mtd, parameter, timeout)
    return RequestResponse(ctx, parameter, response)


def raiseForStatus(ctx, source, cls, mtd, name, response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        raiseHTTPException(ctx, source, cls, mtd, name, 105, e)
    except RequestException as e:
        raiseRequestException(ctx, source, cls, mtd, name, 105, e)

def raiseHTTPException(ctx, source, cls, mtd, name, code, error):
    e = HTTPException()
    e.Context = source
    e.Url = error.response.url
    e.StatusCode = error.response.status_code
    e.Content = error.response.text
    e.Message = getExceptionMessage(ctx, cls, mtd, code, name, e.Url, e.StatusCode, e.Content)
    raise e

def raiseJSONDecodeException(ctx, source, cls, mtd, name, code, response):
    e = JSONDecodeException()
    e.Context = source
    e.Url = response.url
    e.StatusCode = response.status_code
    e.Content = response.text
    e.Message = getExceptionMessage(ctx, cls, mtd, code, name, e.Url, e.StatusCode, e.Content)
    raise e

def raiseRequestException(ctx, source, cls, mtd, name, code, error):
    e = RequestException()
    e.Context = source
    e.Url = error.response.url
    e.Message = getExceptionMessage(ctx, cls, mtd, code, name, e.Url, error.response.status_code, error.response.text)
    raise e


def getExceptionMessage(ctx, cls, method, resource, *args):
    logger = getLogger(ctx, g_errorlog, g_basename)
    message = logger.resolveString(resource, *args)
    logger.logp(SEVERE, cls, method, message)
    return message


class RequestResponse(unohelper.Base,
                      XRequestResponse):
    def __init__(self, ctx, parameter, response):
        self._ctx = ctx
        self._parameter = parameter
        self._response = response

    @property
    def Parameter(self):
        return self._parameter
    @property
    def Url(self):
        return self._response.url
    @property
    def FullUrl(self):
        return self._response.fullurl
    @property
    def StatusCode(self):
        return self._response.status_code
    @property
    def Reason(self):
        return self._response.reason
    @property
    def Links(self):
        return self._response.links
    @property
    def ApparentEncoding(self):
        return self._response.apparent_encoding
    @property
    def Encoding(self):
        return self._response.encoding
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
    def Headers(self):
        return json.dump(self._response.headers)
    @property
    def History(self):
        return tuple(ResquestResponse(self._ctx, self._parameter, r) for r in self._response.history)
    @property
    def Ok(self):
        return self._response.ok
    @property
    def Error(self):
        return self._getHTTPException(self._response.error)
    @property
    def IsPermanentRedirect(self):
        return self._response.is_permanent_redirect
    @property
    def IsRedirect(self):
        return self._response.is_redirect
    @property
    def Elapsed(self):
        return getDuration(self._response.elapsed)
    @property
    def DataSink(self):
        return InputStream(self._response)

    def close(self):
        self._response.close()

    def hasHeader(self, key):
        return key in self._response.headers

    def getHeader(self, key):
        return self._response.headers.get(key, '')

    def getForm(self):
        try:
            data = parse_qs(self._response.content, encoding=self._response.encoding)
        except ValueError as e:
            raiseJSONDecodeException(self._ctx, self, 'RequestResponse', 'getForm()', self._parameter.Name, 105, self._response)
        else:
            return getJsonStructure(data)

    def getJson(self):
        try:
            data = self._response.json()
        except JSONDecodeError as e:
            raiseJSONDecodeException(self._ctx, self, 'RequestResponse', 'getJson()', self._parameter.Name, 105, self._response)
        else:
            return getJsonStructure(data)

    def raiseForStatus(self):
        raiseForStatus(self._ctx, self, 'RequestResponse', 'raiseForStatus()', self._parameter.Name, self._response)

    def iterContent(self, length, decode):
        chunk = length if length > 0 else None
        return Enumerator(self._response.iter_content(chunk, decode), decode)

    def iterLines(self, length, decode, separator):
        chunk = length if length > 0 else None
        delimiter = separator if separator != '' else None
        return Enumerator(self._response.iter_lines(chunk, decode, delimiter), decode)


class InputStream(unohelper.Base,
                  XInputStream):
    def __init__(self, response):
        self._response = response
        self._input = response.raw
        self._input.seek(0, 2)
        self._length = self._input.tell()
        self._input.seek(0)

    #XInputStream
    def readBytes(self, sequence, length):
        sequence = uno.ByteSequence(self._input.read(length))
        return len(sequence), sequence
    def readSomeBytes(self, sequence, length):
        return self.readBytes(sequence, length)
    def skipBytes(self, length):
        self._input.seek(length, 1)
    def available(self):
        available = self._length - self._input.tell()
        return max(available, 0)
    def closeInput(self):
        self._input.close()
        self._response.close

    #XSeekable
    def seek(self, location):
        self._input.seek(location)
    def getPosition(self):
        return self._input.tell()
    def getLength(self):
        return self._length


class Enumerator(unohelper.Base,
                 XEnumeration):
    def __init__(self, iterator, decode):
        self._iterator = iterator
        self._decode = decode
        self._stopped = False
        # FIXME: In order to be able to respond to the hasMoreElements()
        # FIXME: method, I need to be one element ahead...
        self._buffer = self._nextElement()

    #XEnumeration
    def hasMoreElements(self):
        return not self._stopped
    def nextElement(self):
        if self._stopped:
            raise NoSuchElementException('Error: no more elements exist', self)
        buffer = self._buffer if self._decode else uno.ByteSequence(self._buffer)
        self._buffer = self._nextElement()
        return buffer

    # Private methods
    def _nextElement(self):
        try:
            return next(self._iterator)
        except StopIteration:
            self._stopped = True
            return None


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

