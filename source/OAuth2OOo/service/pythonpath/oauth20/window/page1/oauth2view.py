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
    def __init__(self, ctx, handler, parent):
        self._window = getContainerWindow(ctx, parent, handler, g_identifier, 'PageWizard1')

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

    def canAddItem(self):
        return any((self._canAddUrl(),
                    self._getSaveUrl().Model.Enabled,
                    self._getAddProvider().Model.Enabled,
                    self._getAddScope().Model.Enabled))

    def getConfiguration(self):
        return self.getUser(), self.getUrl(), self.getProvider(), self.getScope()

# OAuth2View setter methods
    def initView(self, user, url, urls, enabled):
        control = self._getUser()
        control.Text = user
        control.Model.Enabled = enabled
        control = self._getUrls()
        control.Model.StringItemList = urls
        control.Text = url
        control.Model.Enabled = enabled

    def enableAddUrl(self, enabled):
        self._getAddUrl().Model.Enabled = enabled

    def enableSaveUrl(self, enabled):
        self._getSaveUrl().Model.Enabled = enabled

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

    def setProviders(self, providers, provider, scope):
        control = self._getProviders()
        control.Model.StringItemList = providers
        control.Text = provider
        self._getScopes().Text = scope

    def addUrl(self, url):
        control = self._getUrls()
        control.addItem(url, control.getItemCount())
        self.enableAddUrl(False)
        self.enableRemoveUrl(True)

    def removeUrl(self, url):
        self._removeItem(self._getUrls(), url)

    def removeProvider(self, provider):
        self._removeItem(self._getProviders(), provider)

    def removeScope(self, scope, enabled):
        self._removeItem(self._getScopes(), scope)
        self.enableRemoveProvider(enabled)

    def setScopes(self, scopes):
        control = self._getScopes()
        control.Model.StringItemList = scopes
        scope = control.getItem(0) if control.getItemCount() else ''
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

    def addProvider(self, provider):
        control = self._getProviders()
        control.addItem(provider, control.getItemCount())

    def addScope(self, scope):
        control = self._getScopes()
        control.addItem(scope, control.getItemCount())

    def toggleAddUrl(self, inlist):
        state = inlist and self._canAddUrl()
        self._getAddUrl().Model.Enabled = state

    def toggleUrlButtons(self, inlist, enabled):
        state = inlist and self._canAddUrl()
        self._getAddUrl().Model.Enabled = state
        self._getSaveUrl().Model.Enabled = not state and enabled

    def toggleProviderButtons(self):
        self._getAddProvider().Model.Enabled = False
        self._getEditProvider().Model.Enabled = True
        self._getRemoveProvider().Model.Enabled = True

    def toggleScopeButtons(self):
        self._getAddScope().Model.Enabled = False
        self._getEditScope().Model.Enabled = True
        self._getRemoveScope().Model.Enabled = True

# OAuth2View private getter methods
    def _canAddUrl(self):
        control = self._getUrls()
        return control.Text not in self._getControlItems(control)

    def _getControlItems(self, control):
        # TODO: OpenOffice has strange behavior if StringItemList is empty
        return control.getItems() if control.getItemCount() > 0 else ()

    def _removeItem(self, control, item):
        items = self._getControlItems(control)
        if item in items:
            control.Model.removeItem(items.index(item))
            control.Text = ''

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

    def _getSaveUrl(self):
        return self._window.getControl('CommandButton2')

    def _getRemoveUrl(self):
        return self._window.getControl('CommandButton3')

    def _getAddProvider(self):
        return self._window.getControl('CommandButton4')

    def _getEditProvider(self):
        return self._window.getControl('CommandButton5')

    def _getRemoveProvider(self):
        return self._window.getControl('CommandButton6')

    def _getAddScope(self):
        return self._window.getControl('CommandButton7')

    def _getEditScope(self):
        return self._window.getControl('CommandButton8')

    def _getRemoveScope(self):
        return self._window.getControl('CommandButton9')

    def _getUrlLabel(self):
        return self._window.getControl('Label4')
