#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-24 https://prrvchr.github.io                                  ║
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

from ..model import BaseModel

from ..oauth2helper import getProviderName

import traceback


class OptionsModel(BaseModel):
    def __init__(self, ctx):
        super(OptionsModel, self).__init__(ctx)

    @property
    def _ConnectTimeout(self):
        return self._config.getByName('ConnectTimeout')
    @property
    def _ReadTimeout(self):
        return self._config.getByName('ReadTimeout')
    @property
    def _HandlerTimeout(self):
        return self._config.getByName('HandlerTimeout')

    def getOptionsData(self):
        return self._ConnectTimeout, self._ReadTimeout, self._HandlerTimeout, self.UrlList

    def getProviderName(self, url):
        return getProviderName(self._config, url)

    def setOptionsData(self, connect, read, handler):
        if connect != self._ConnectTimeout:
            self._config.replaceByName('ConnectTimeout', connect)
        if read != self._ReadTimeout:
            self._config.replaceByName('ReadTimeout', read)
        if handler != self._HandlerTimeout:
            self._config.replaceByName('HandlerTimeout', handler)

