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
    def __init__(self, window, update, links):
        self._window = window
        self._getSetup().Model.Enabled = update
        for i, link in enumerate(links, start=1):
            self._getLink(i).URL = link

# OptionsView public setter methods
    def dispose(self):
        self._window.dispose()

    def initView(self, connect, read, handler, urls, setup, state):
        self._getConnectTimeout().setValue(connect)
        self._getReadTimeout().setValue(read)
        self._getHandlerTimeout().setValue(handler)
        self._getUrls().Model.StringItemList = urls
        self._setSetup(setup)
        self.refreshView(state)

    def refreshView(self, state):
        self._window.Model.Step = state.step
        self._enableButtons(state)

# OptionsView public getter methods
    def getWindow(self):
        return self._window

    def getUrl(self):
        return self._getUrls().getSelectedItem()

    def getAutoClose(self):
        return bool(self._getAutoClose().State)

    def getSetup(self):
        return self._getSetup().getSelectedItemPos()

    def getViewData(self):
        return self._getConnect(), self._getRead(), self._getHandler(), self.getSetup()

# OptionsView private methods
    def _setSetup(self, setup):
        control = self._getSetup()
        if control.Model.Enabled:
            control.selectItemPos(setup, True)

    def _enableButtons(self, state):
        enabled = state.python and not state.restart
        self._getWizardButton().Model.Enabled = enabled

# OptionsView private getter methods
    def _getConnect(self):
        return int(self._getConnectTimeout().getValue())

    def _getRead(self):
        return int(self._getReadTimeout().getValue())

    def _getHandler(self):
        return int(self._getHandlerTimeout().getValue())

# OptionsView private getter control methods
    def _getUrls(self):
        return self._window.getControl('ListBox1')

    def _getAutoClose(self):
        return self._window.getControl('CheckBox1')

    def _getConnectTimeout(self):
        return self._window.getControl('NumericField1')

    def _getReadTimeout(self):
        return self._window.getControl('NumericField2')

    def _getHandlerTimeout(self):
        return self._window.getControl('NumericField3')

    def _getWizardButton(self):
        return self._window.getControl('CommandButton1')

    def _getSetup(self):
        return self._window.getControl('ListBox2')

    def _getLink(self, index):
        return self._window.getControl(f'Hyperlink{index}')

