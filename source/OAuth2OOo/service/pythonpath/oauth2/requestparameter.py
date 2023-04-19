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


from com.sun.star.rest.ParameterType import NONE
from com.sun.star.rest.ParameterType import URL
from com.sun.star.rest.ParameterType import QUERY
from com.sun.star.rest.ParameterType import JSON
from com.sun.star.rest.ParameterType import HEADER

from com.sun.star.rest import XRequestParameter

from .oauth2 import NoOAuth2

import json
import traceback


class RequestParameter(unohelper.Base,
                       XRequestParameter):
    def __init__(self, ctx, name):
        self._ctx = ctx
        self._name = name
        self._method = 'GET'
        self._url = ''
        self._headers = {}
        self._query = {}
        self._json = {}
        self._data = ''
        self._datasink = None
        self._noauth = False
        self._auth = ()
        self._noredirect = False
        self._noverify = False
        self._stream = False
        self._token = ''
        self._count = 0
        self._key = None
        self._value = None
        self._type = NONE

    @property
    def Name(self):
        return self._name
    @property
    def Method(self):
        return self._method
    @Method.setter
    def Method(self, method):
        self._method = method
    @property
    def Url(self):
        if self._type == URL or self._type == REDIRECT:
            return self._value
        return self._url
    @Url.setter
    def Url(self, url):
        self._url = url
    @property
    def Headers(self):
        return json.dump(self._headers)
    @Headers.setter
    def Headers(self, headers):
        self._headers = json.loads(headers)
    @property
    def Query(self):
        return json.dump(self._query)
    @Query.setter
    def Query(self, query):
        self._query = json.loads(query)
    @property
    def Json(self):
        return json.dump(self._json)
    @Json.setter
    def Json(self, data):
        self._json = json.loads(data)
    @property
    def Data(self):
        return self._data
    @Data.setter
    def Data(self, data):
        self._data = data
    @property
    def DataSink(self):
        return self._datasink
    @DataSink.setter
    def DataSink(self, datasink):
        self._datasink = datasink
    @property
    def NoAuth(self):
        return self._noauth
    @NoAuth.setter
    def NoAuth(self, state):
        self._noauth = state
    @property
    def Auth(self):
        return self._auth
    @Auth.setter
    def Auth(self, auth):
        self._auth = auth
    @property
    def NoRedirect(self):
        return self._noredirect
    @NoRedirect.setter
    def NoRedirect(self, state):
        self._noredirect = state
    @property
    def NoVerify(self):
        return self._noverify
    @NoVerify.setter
    def NoVerify(self, state):
        self._noverify = state
    @property
    def Stream(self):
        return self._stream
    @Stream.setter
    def Stream(self, state):
        self._stream = state
    @property
    def SyncToken(self):
        return self._token
    @SyncToken.setter
    def SyncToken(self, token):
        self._token = token
    @property
    def PageCount(self):
        return self._count
    @property
    def PageKey(self):
        if self._key is None:
            return ''
        key = self._key
        self._key = None
        return key
    @property
    def PageValue(self):
        if self._value is None:
            return ''
        value = self._value
        self._value = None
        return value
    @property
    def PageType(self):
        return self._type

    def hasNextPage(self):
        hasnext = self._hasNextPage()
        if hasnext:
            self._count += 1
        return hasnext

    def setNextPage(self, key, value, parameter):
        self._key = key
        self._value = value
        self._type = parameter

    def setHeader(self, key, value):
        self._headers[key] = value

    def toJson(self, stream):
        # FIXME: It is necessary to be able to manage nextPage
        # FIXME: tokens and sync token present in various XML/JSON APIs
        kwargs = {}
        nextdata = {self._key: self._value}
        if self._headers:
            data = self._headers
            if self._type == HEADER:
                data.update(nextdata)
            kwargs['headers'] = data
        if self._query and self._type != REDIRECT:
            data = self._query
            if self._type == QUERY:
                data.update(nextdata)
            kwargs['params'] = data
        if self._data:
            kwargs['data'] = self._data
        elif self._json:
            data = self._json
            if self._type == JSON:
                data.update(nextdata)
            kwargs['json'] = data
        elif self._datasink:
            kwargs['data'] = FileLike(self._datasink)
        if self._noauth:
            kwargs['auth'] = NoOAuth2()
        elif self._auth:
            kwargs['auth'] = self._auth
        if self._noredirect:
            kwargs['allow_redirects'] = False
        if self._noverify:
            kwargs['verify'] = False
        if self._stream or stream:
            kwargs['stream'] = True
        return json.dump(kwargs)

    def _hasNextPage(self):
        if self._type != NONE:
            return self._value is not None and self._key is not None
        else:
            return self._count == 0


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

