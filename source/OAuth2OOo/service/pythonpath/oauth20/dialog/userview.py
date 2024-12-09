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

from ..unotool import getDialog

from ..configuration import g_identifier

import traceback

class UserView():
    def __init__(self, ctx, handler, parent, title, label):
        self._dialog = getDialog(ctx, g_identifier, 'UserDialog', handler, parent)
        self._dialog.setTitle(title)
        self._getLabel().Text = label

# UserView getter methods
    def execute(self):
        return self._dialog.execute()

    def getUser(self):
        return self._getUser().Text.strip()

# UserView setter methods
    def dispose(self):
        self._dialog.dispose()

    def enableOkButton(self, enabled):
        self._getOkButton().Model.Enabled = enabled

# UserView private getter control methods
    def _getUser(self):
        return self._dialog.getControl('TextField1')

    def _getLabel(self):
        return self._dialog.getControl('Label1')

    def _getOkButton(self):
        return self._dialog.getControl('CommandButton2')
