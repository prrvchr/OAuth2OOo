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

from com.sun.star.rest import HTTPException
from com.sun.star.rest import JSONDecodeException

from com.sun.star.rest import XRequestResponse

from .unolib import KeyMap

from .logger import getLogger

from .configuration import g_errorlog
g_basename = 'request'

from requests.exceptions import HTTPError
from requests.exceptions import JSONDecodeError
import traceback


class RequestResponse(unohelper.Base,
                      XRequestResponse):
    def __init__(self, ctx, parameter, response):
        self._ctx = ctx
        self._parameter = parameter
        self._response = response
        print("RequestResponse.__init__() 1")

    @property
    def Parameter(self):
        return self._parameter
    @property
    def Url(self):
        return self._response.url
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
        return KeyMap(self._response.headers)
    @property
    def History(self):
        return tuple(ResquestResponse(self._parameter, r) for r in self._response.history)
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
    @property
    def Raw(self):
        return RequestInputStream(self._response)

    def close(self):
        self._response.close()

    def hasHeader(self, key):
        return key in self._response.headers

    def getHeader(self, key):
        return self._response.headers.get(key, '')

    def json(self):
        try:
            return KeyMap(**self._response.json())
        except JSONDecodeError as e:
            error = JSONDecodeException()
            error.Url = e.response.url
            error.Content = e.response.text
            error.Message = getExceptionMessage(self._ctx, 'OAuth2Service', 'execute()', 107, error.Url)
            raise error

    def jsonWithParser(self, parser):
        try:
            return self._response.json(object_pairs_hook=parser.parse)
        except JSONDecodeError as e:
            error = JSONDecodeException()
            error.Url = e.response.url
            error.Content = e.response.text
            error.Message = getExceptionMessage(self._ctx, 'OAuth2Service', 'execute()', 107, error.Url)
            raise error

    def raiseForStatus(self):
        try:
            self._response.raise_for_status()
        except HTTPError as e:
            error = HTTPException()
            error.Url = e.response.url
            error.StatusCode = e.response.status_code
            error.Content = e.response.text
            error.Message = getExceptionMessage(self._ctx, 'OAuth2Service', 'execute()', 105, error.Url, error.StatusCode)
            raise error

    def iterContent(self, length, decode):
        chunk = length if length > 0 else None
        return RequestIterator(self._response.iter_content(chunk, decode), decode)

    def iterLines(self, length, decode, separator):
        chunk = length if length > 0 else None
        delimiter = separator if separator != '' else None
        return RequestIterator(self._response.iter_lines(chunk, decode, delimiter), decode)


class RequestInputStream(unohelper.Base,
                         XInputStream):
    def __init__(self, response):
        self._input = response.raw
        self._length = int(response.header.get('ContentLength', 0))

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

    #XSeekable
    def seek(self, location):
        self._input.seek(location)
    def getPosition(self):
        return self._input.tell()
    def getLength(self):
        return self._length


class RequestIterator(unohelper.Base,
                      XEnumeration):
    def __init__(self, iterator, decode):
        self._iterator = iterator
        self._decode = decode
        self._end = object()
        # FIXME: In order to be able to respond to the hasMoreElements()
        # FIXME: method, I need to be one element ahead...
        self._next = self._nextElement()

    #XEnumeration
    def hasMoreElements(self):
        return self._next != self._end
    def nextElement(self):
        if not self.hasMoreElements():
            raise NoSuchElementException('Error: no more elements exist', self)
        element = self._next if self._decode else uno.ByteSequence(self._next)
        self._next = self._nextElement()
        return element

    # Private methods
    def _nextElement(self):
        try:
            return next(self._iterator)
        except StopIteration:
            return self._end


def getExceptionMessage(ctx, clazz, method, resource, *args):
    logger = getLogger(ctx, g_errorlog, g_basename)
    message = logger.resolveString(resource, *args)
    logger.logp(SEVERE, clazz, method, message)
    return message

