#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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

from .tokenmodel import TokenModel

from ..unotool import getStringResource

from ..oauth2helper import getProviderName
from ..oauth2helper import isEmailValid

from ..configuration import g_identifier

import traceback


class HandlerModel(TokenModel):
    def __init__(self, ctx):
        super(TokenModel, self).__init__(ctx)
        self._resolver = getStringResource(ctx, g_identifier, 'dialogs', 'UserDialog')
        self._resources = {'UserTitle': 'UserDialog.Title',
                           'UserLabel': 'UserDialog.Label1.Label'}

    def getUserData(self, url, msg):
        provider = getProviderName(self._config, url)
        title = self._getUserTitle(provider)
        label = self._getUserLabel(msg)
        return title, label

    def isEmailValid(self, email):
        return isEmailValid(email)

    def _getUserTitle(self, provider):
        resource = self._resources.get('UserTitle')
        return self._resolver.resolveString(resource) % provider

    def _getUserLabel(self, msg):
        resource = self._resources.get('UserLabel')
        return self._resolver.resolveString(resource) % msg

