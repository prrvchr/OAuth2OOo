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

from ..model import BaseModel

from ..oauth2helper import getProviderName

import traceback


class OptionsModel(BaseModel):
    def __init__(self, ctx):
        super(OptionsModel, self).__init__(ctx)

    @property
    def ConnectTimeout(self):
        return self._config.getByName('ConnectTimeout')
    @ConnectTimeout.setter
    def ConnectTimeout(self, timeout):
        self._config.replaceByName('ConnectTimeout', timeout)

    @property
    def ReadTimeout(self):
        return self._config.getByName('ReadTimeout')
    @ReadTimeout.setter
    def ReadTimeout(self, timeout):
        self._config.replaceByName('ReadTimeout', timeout)

    @property
    def HandlerTimeout(self):
        return self._config.getByName('HandlerTimeout')
    @HandlerTimeout.setter
    def HandlerTimeout(self, timeout):
        self._config.replaceByName('HandlerTimeout', timeout)

    def getOptionsDialogData(self):
        return self.ConnectTimeout, self.ReadTimeout, self.HandlerTimeout, self.UrlList

    def getProviderName(self, url):
        return getProviderName(self._config, url)

