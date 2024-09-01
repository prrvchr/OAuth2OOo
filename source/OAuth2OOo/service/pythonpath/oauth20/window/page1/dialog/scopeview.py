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

import uno
import unohelper

from ....unotool import getDialog

from ....configuration import g_identifier

import traceback

class ScopeView(unohelper.Base):
    def __init__(self, ctx, handler, parent, title, scopes):
        self._dialog = getDialog(ctx, g_identifier, 'ScopeDialog', handler, parent)
        self._dialog.setTitle(title)
        self._getScopes().Model.StringItemList = scopes
        self._updateOk()

# ProviderView getter methods
    def execute(self):
        return self._dialog.execute()

    def getScope(self):
        return self._getScope().Text.strip()

    def hasScopes(self):
        return self._getScopes().ItemCount > 0

    def getScopeValues(self):
        control = self._getScopes()
        return control.Model.StringItemList if control.ItemCount else ()

# ProviderView setter methods
    def dispose(self):
        self._dialog.dispose()

    def updateAdd(self, enabled):
        self._getAddButton().Model.Enabled = enabled

    def updateRemove(self, enabled):
        self._getRemoveButton().Model.Enabled = enabled

    def addScope(self):
        scope = self._getScope()
        scopes = self._getScopes()
        scopes.addItem(scope.Text.strip(), scopes.ItemCount)
        scope.Text = ''
        self._updateOk()

    def removeScope(self):
        control = self._getScopes()
        control.removeItems(control.getSelectedItemPos(), 1)
        self.updateRemove(False)
        self._updateOk()

# ScopeView private setter methods
    def _updateOk(self):
        self._getOkButton().Model.Enabled = self._getScopes().ItemCount > 0

# ScopeView private getter control methods
    def _getScopes(self):
        return self._dialog.getControl('ListBox1')

    def _getScope(self):
        return self._dialog.getControl('TextField1')

    def _getAddButton(self):
        return self._dialog.getControl('CommandButton1')

    def _getRemoveButton(self):
        return self._dialog.getControl('CommandButton2')

    def _getOkButton(self):
        return self._dialog.getControl('CommandButton4')

