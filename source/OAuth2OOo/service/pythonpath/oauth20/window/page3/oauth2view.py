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

from ...unotool import getContainerWindow

from ...configuration import g_identifier

import traceback


class OAuth2View():
    def __init__(self, ctx, parent, timeout):
        self._window = getContainerWindow(ctx, parent, None, g_identifier, 'PageWizard3')
        self._getProgessBar().setRange(0, timeout)

# OAuth2View getter methods
    def getWindow(self):
        return self._window

# OAuth2View setter methods
    def setStep(self, step):
        self._window.Model.Step = step

    def setProgress(self, value):
        self._getProgessBar().Value = value

    def showError(self, title, message):
        self._window.Model.Step = 2
        self._getErrorTitle().Text = title
        self._getErrorText().Text = message

# OAuth2View private getter control methods
    def _getProgessBar(self):
        return self._window.getControl('ProgressBar1')

    def _getErrorTitle(self):
        return self._window.getControl('Label2')

    def _getErrorText(self):
        return self._window.getControl('TextField1')
