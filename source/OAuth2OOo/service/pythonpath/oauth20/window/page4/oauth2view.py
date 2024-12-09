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

import unohelper

from ...unotool import getContainerWindow

from ...configuration import g_identifier

import traceback


class OAuth2View(unohelper.Base):
    def __init__(self, ctx, handler, parent):
        self._window = getContainerWindow(ctx, parent, handler, g_identifier, 'PageWizard4')

# OAuth2View getter methods
    def getWindow(self):
        return self._window

    def hasError(self):
        return self._window.Model.Step == 2

# OAuth2View setter methods
    def initView(self, title, never, scopes, access, refresh, expires):
        self._getTitle().Text = title
        self._getUpdateButton().Model.Enabled = not never
        self._getDeleteButton().Model.Enabled = True
        self._getRefreshButton().Model.Enabled = not never
        self.setToken(never, scopes, access, refresh, expires)

    def setToken(self, never, scopes, access, refresh, expires):
        control = self._getScopes()
        control.Model.StringItemList = scopes
        if control.ItemCount > 0:
            control.selectItemPos(0, True)
        self._getAccess().Text = access
        self._getRefresh().Text = refresh
        self._getExpires().Text = expires
        self._window.Model.Step = 1

    def showError(self, message):
        self._getErrorText().Text = message
        self._getUpdateButton().Model.Enabled = False
        self._getDeleteButton().Model.Enabled = False
        self._window.Model.Step = 2

# OAuth2View private getter control methods
    def _getTitle(self):
        return self._window.getControl('Label1')

    def _getScopes(self):
        return self._window.getControl('ListBox1')

    def _getRefresh(self):
        return self._window.getControl('Label4')

    def _getAccess(self):
        return self._window.getControl('Label6')

    def _getExpires(self):
        return self._window.getControl('Label8')

    def _getErrorText(self):
        return self._window.getControl('TextField1')

    def _getUpdateButton(self):
        return self._window.getControl('CommandButton1')

    def _getDeleteButton(self):
        return self._window.getControl('CommandButton2')

    def _getRefreshButton(self):
        return self._window.getControl('CommandButton3')

