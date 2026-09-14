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

from ..model import BaseModel

from ..model import getProviderName

from ..unotool import getStringResource

from ..configuration import g_identifier


class OptionsModel(BaseModel):
    def __init__(self, ctx):
        super(OptionsModel, self).__init__(ctx)
        self._resolver = getStringResource(ctx, g_identifier, 'dialogs', 'OptionsDialog')
        self._resources = {'Link': 'OptionsDialog.Label5.Url.%s'}

    @property
    def _connect(self):
        return self._config.getByName('ConnectTimeout')

    @_connect.setter
    def _connect(self, connect):
        self._config.replaceByName('ConnectTimeout', connect)

    @property
    def _read(self):
        return self._config.getByName('ReadTimeout')

    @_read.setter
    def _read(self, read):
        self._config.replaceByName('ReadTimeout', read)

    @property
    def _handler(self):
        return self._config.getByName('HandlerTimeout')

    @_handler.setter
    def _handler(self, handler):
        self._config.replaceByName('HandlerTimeout', handler)

    def getConfig(self):
        return self._config

    def getInitData(self, state):
        return self._connect, self._read, self._handler, self.UrlList, *self.getRefreshData(state)

    def getRefreshData(self, state):
        return state, state.getMessage(self._ctx), self._getLink(state.code)

    def getProviderName(self, url):
        return getProviderName(self._config, url)

    def setOptionsData(self, connect, read, handler):
        if connect != self._connect:
            self._connect = connect
        if read != self._read:
            self._read = read
        if handler != self._handler:
            self._handler = handler

    def _getLink(self, code):
        resource = self._resources.get('Link') % code
        return self._resolver.resolveString(resource)
