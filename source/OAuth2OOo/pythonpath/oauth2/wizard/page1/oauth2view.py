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

from oauth2 import getContainerWindow
from oauth2 import g_extension

import traceback


class OAuth2View(unohelper.Base):
    def __init__(self, ctx, handler, parent):
        self._window = getContainerWindow(ctx, parent, handler, g_extension, 'PageWizard1')

# OAuth2View getter methods
    def getWindow(self):
        return self._window

    def getUser(self):
        return self._getUser().Text.strip()

    def getUrl(self):
        return self._getUrls().Text.strip()

    def getProvider(self):
        return self._getProviders().Text.strip()

    def getScope(self):
        return self._getScopes().Text.strip()

# OAuth2View setter methods
    def initView(self, user, url, urls):
        self._getUser().Text = user
        self._getUrls().Model.StringItemList = urls
        self._getUrls().Text = url

    def enableAddUrl(self, enabled):
        self._getAddUrl().Model.Enabled = enabled

    def enableRemoveUrl(self, enabled):
        self._getRemoveUrl().Model.Enabled = enabled


    def enableAddProvider(self, enabled):
        self._getAddProvider().Model.Enabled = enabled

    def enableEditProvider(self, enabled):
        self._getEditProvider().Model.Enabled = enabled

    def enableRemoveProvider(self, enabled):
        self._getRemoveProvider().Model.Enabled = enabled

    def enableAddScope(self, enabled):
        self._getAddScope().Model.Enabled = enabled

    def enableEditScope(self, enabled):
        self._getEditScope().Model.Enabled = enabled

    def enableRemoveScope(self, enabled):
        self._getRemoveScope().Model.Enabled = enabled

    def setUrl(self, scope, scopes, provider, providers):
        control = self._getProviders()
        control.Model.StringItemList = providers
        control.Text = provider
        control = self._getScopes()
        control.Model.StringItemList = scopes
        control.Text = scope

    def setUrlLabel(self, label):
        self._getUrlLabel().Text = label

    def setUserFocus(self):
        self._getUser().setFocus()

    def setUrlFocus(self):
        self._getUrls().setFocus()

    def setProviderFocus(self):
        self._getProviders().setFocus()

    def setScopeFocus(self):
        self._getScopes().setFocus()

# OAuth2View private getter control methods
    def _getUser(self):
        return self._window.getControl('TextField1')

    def _getUrls(self):
        return self._window.getControl('ComboBox1')

    def _getProviders(self):
        return self._window.getControl('ComboBox2')

    def _getScopes(self):
        return self._window.getControl('ComboBox3')

    def _getAddUrl(self):
        return self._window.getControl('CommandButton1')

    def _getRemoveUrl(self):
        return self._window.getControl('CommandButton2')

    def _getAddProvider(self):
        return self._window.getControl('CommandButton3')

    def _getEditProvider(self):
        return self._window.getControl('CommandButton4')

    def _getRemoveProvider(self):
        return self._window.getControl('CommandButton5')

    def _getAddScope(self):
        return self._window.getControl('CommandButton6')

    def _getEditScope(self):
        return self._window.getControl('CommandButton7')

    def _getRemoveScope(self):
        return self._window.getControl('CommandButton8')

    def _getUrlLabel(self):
        return self._window.getControl('Label4')
