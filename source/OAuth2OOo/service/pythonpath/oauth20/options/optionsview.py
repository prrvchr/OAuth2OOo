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

import traceback


class OptionsView():
    def __init__(self, dialog):
        self._dialog = dialog

# OptionsView public setter methods
    def initView(self, restart, connect, read, handler, urls):
        self._getConnectTimeout().setValue(connect)
        self._getReadTimeout().setValue(read)
        self._getHandlerTimeout().setValue(handler)
        self._getUrls().Model.StringItemList = urls
        self.setRestart(restart)

    def setRestart(self, enabled):
        self._getRestart().setVisible(enabled)

# OptionsView public getter methods
    def getParent(self):
        return self._dialog.getPeer()

    def getUrl(self):
        return self._getUrls().SelectedText

    def getAutoClose(self):
        return bool(self._getAutoClose().State)

    def getViewData(self):
        return self._getConnect(), self._getRead(), self._getHandler()

# OptionsView private getter methods
    def _getConnect(self):
        return int(self._getConnectTimeout().getValue())

    def _getRead(self):
        return int(self._getReadTimeout().getValue())

    def _getHandler(self):
        return int(self._getHandlerTimeout().getValue())

# OptionsView private getter control methods
    def _getUrls(self):
        return self._dialog.getControl('ComboBox1')

    def _getAutoClose(self):
        return self._dialog.getControl('CheckBox1')

    def _getConnectTimeout(self):
        return self._dialog.getControl('NumericField1')

    def _getReadTimeout(self):
        return self._dialog.getControl('NumericField2')

    def _getHandlerTimeout(self):
        return self._dialog.getControl('NumericField3')

    def _getRestart(self):
        return self._dialog.getControl('Label5')

