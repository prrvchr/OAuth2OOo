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

from ..unotool import getContainerWindow

from ..configuration import g_extension

import traceback


class OptionsView(unohelper.Base):
    def __init__(self, ctx, handler, parent):
        self._window = getContainerWindow(ctx, parent, handler, g_extension, 'OptionsWindow')
        self._window.setVisible(True)

    def getParent(self):
        return self._window.getPeer()

    def initView(self, connect, read, handler, urls):
        self._getConnectTimeout().setValue(connect)
        self._getReadTimeout().setValue(read)
        self._getHandlerTimeout().setValue(handler)
        self._getUrls().Model.StringItemList = urls

    def getConnectTimeout(self):
        return int(self._getConnectTimeout().getValue())

    def getReadTimeout(self):
        return int(self._getReadTimeout().getValue())

    def getHandlerTimeout(self):
        return int(self._getHandlerTimeout().getValue())

    def getUrl(self):
        return self._getUrls().SelectedText

    def getAutoClose(self):
        return bool(self._getAutoClose().State)

# OptionsView private getter control methods
    def _getUrls(self):
        return self._window.getControl('ComboBox1')

    def _getAutoClose(self):
        return self._window.getControl('CheckBox1')

    def _getConnectTimeout(self):
        return self._window.getControl('NumericField1')

    def _getReadTimeout(self):
        return self._window.getControl('NumericField2')

    def _getHandlerTimeout(self):
        return self._window.getControl('NumericField3')


