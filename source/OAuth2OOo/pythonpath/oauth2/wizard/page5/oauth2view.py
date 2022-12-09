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

from ...unotool import getContainerWindow
from ...configuration import g_extension

import traceback


class OAuth2View(unohelper.Base):
    def __init__(self, ctx, handler, parent):
        print("OAuth2View.__init__() 1")
        self._window = getContainerWindow(ctx, parent, handler, g_extension, 'PageWizard5')
        print("OAuth2View.__init__() 2")

# OAuth2View getter methods
    def getWindow(self):
        return self._window

# OAuth2View setter methods
    def initView(self, label, scopes, access, refresh, expires):
        self._getLabel().Text = label
        self.setToken(scopes, access, refresh, expires)

    def setToken(self, scopes, access, refresh, expires):
        control = self._getScopes()
        control.Model.StringItemList = scopes
        if control.ItemCount > 0:
            control.selectItemPos(0, True)
        self._getAccess().Text = access
        self._getRefresh().Text = refresh
        self._getExpires().Text = expires

# OAuth2View private getter control methods
    def _getLabel(self):
        return self._window.getControl('Label1')

    def _getScopes(self):
        return self._window.getControl('ListBox1')

    def _getRefresh(self):
        return self._window.getControl('Label4')

    def _getAccess(self):
        return self._window.getControl('Label6')

    def _getExpires(self):
        return self._window.getControl('Label8')

