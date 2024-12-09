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

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.ui.dialogs.WizardTravelType import FORWARD

from com.sun.star.ui.dialogs import XWizardPage

from .oauth2handler import WindowHandler

from .oauth2view import OAuth2View

from .dialog import ProviderHandler
from .dialog import ProviderView
from .dialog import ScopeHandler
from .dialog import ScopeView

from ...unolib import PropertySet

from ...unotool import createMessageBox
from ...unotool import getProperty
from ...unotool import getStringResource

from ...configuration import g_identifier

import traceback


class OAuth2Manager(unohelper.Base,
                    XWizardPage,
                    PropertySet):
    def __init__(self, ctx, wizard, model, pageid, parent):
        self._ctx = ctx
        self._dialog = None
        self._wizard = wizard
        self._model = model
        self._pageid = pageid
        self._view = OAuth2View(ctx, WindowHandler(self), parent)
        self._resolver = getStringResource(ctx, g_identifier, 'dialogs', 'PageWizard1')
        self._view.initView(*self._model.getInitData())

# XWizardPage
    @property
    def PageId(self):
        return self._pageid
    @property
    def Window(self):
        return self._view.getWindow()

    def activatePage(self):
        self._setActivePath()
        self._view.setUserFocus()

    def commitPage(self, reason):
        if reason == FORWARD:
            self._model.initialize(self._view.getUrl(), self._view.getUser())
        return True

    def canAdvance(self):
        return not self._view.canAddItem() and self._model.isConfigurationValid(*self._view.getConfiguration())

# XComponent
    def dispose(self):
        pass
    def addEventListener(self, listener):
        pass
    def removeEventListener(self, listener):
        pass

# OAuth2Manager setter methods called by WindowHandler
    def setUser(self, user):
        self._setActivePath()
        self._view.setUserFocus()

    def setUrl(self, url, inlist):
        self._view.enableRemoveUrl(inlist)
        # TODO: Add URL button must be enabled after setting the Scope
        self._view.enableAddUrl(False)
        self._view.setProviders(*self._model.getUrlData(url))
        self._view.setUrlLabel(self._model.getUrlLabel(self._resolver, url))
        self._setActivePath()
        self._view.setUrlFocus()

    def addUrl(self):
        url = self._view.getUrl()
        scope = self._view.getScope()
        self._model.addUrl(url, scope)
        self._view.addUrl(url)

    def saveUrl(self):
        url = self._view.getUrl()
        scope = self._view.getScope()
        self._model.saveUrl(url, scope)
        self._view.enableSaveUrl(False)
        self._wizard.updateTravelUI()

    def removeUrl(self):
        dialog = self._getMessageBox()
        if dialog.execute() == OK:
            url = self._view.getUrl()
            self._model.removeUrl(url)
            self._view.removeUrl(url)
        dialog.dispose()

    def setProvider(self, provider, inlist):
        url = self._view.getUrl()
        self._view.enableAddProvider(False if inlist else self._model.isValueValid(provider))
        self._view.enableEditProvider(inlist)
        self._view.enableRemoveProvider(inlist and self._model.canRemoveProvider(provider))
        self._view.setScopes(self._model.getScopeList(provider))
        self._view.toggleAddUrl(inlist)
        self._setActivePath()
        self._view.setProviderFocus()

    def addProvider(self):
        self._showProvider(True)

    def editProvider(self):
        self._showProvider(False)

    def removeProvider(self):
        dialog = self._getMessageBox()
        if dialog.execute() == OK:
            provider = self._view.getProvider()
            self._model.removeProvider(provider)
            self._view.removeProvider(provider)
        dialog.dispose()

    def setScope(self, scope, inlist):
        url = self._view.getUrl()
        self._view.enableAddScope(False if inlist else self._model.isValueValid(scope))
        self._view.enableEditScope(inlist)
        self._view.enableRemoveScope(inlist and self._model.canRemoveScope(scope))
        self._view.toggleUrlButtons(inlist, inlist and self._model.isScopeChanged(url, scope))
        self._setActivePath()
        self._view.setScopeFocus()

    def addScope(self):
        self._showScope(True)

    def editScope(self):
        self._showScope(False)

    def removeScope(self):
        dialog = self._getMessageBox()
        if dialog.execute() == OK:
            scope = self._view.getScope()
            self._model.removeScope(scope)
            self._view.removeScope(scope, self._model.canRemoveProvider(self._view.getProvider()))
        dialog.dispose()

# OAuth2Manager setter methods called by ProviderHandler
    def setValue(self):
        enabled = self._model.isDialogValid(*self._dialog.getDialogValues())
        self._dialog.updateOk(enabled)

    def setChallenge(self, enabled):
        self._dialog.enableChallengeMethod(enabled)

    def setHttpHandler(self, enabled):
        self._dialog.enableHttpHandler(enabled)

    def setSignIn(self, enabled):
        self._dialog.enableSignIn(enabled)
        self.setValue()

# OAuth2Manager setter methods called by ScopeHandler
    def selectScopeValue(self, selected):
        self._dialog.updateRemove(selected)

    def setScopeValue(self, scope):
        if scope in self._dialog.getScopeValues():
            self._dialog.updateAdd(False)
        else:
            self._dialog.updateAdd(scope != '')

    def addScopeValue(self):
        self._dialog.addScope()

    def removeScopeValue(self):
        self._dialog.removeScope()

# OAuth2Manager private getter methods
    def _getMessageBox(self):
        return createMessageBox(self._view.getWindow().Peer, *self._model.getMessageBoxData())

# OAuth2Manager private setter methods
    def _setActivePath(self):
        path = self._model.getActivePath(*self._view.getConfiguration())
        self._wizard.activatePath(path, True)
        self._wizard.updateTravelUI()

    def _showProvider(self, new):
        return
        provider = self._view.getProvider()
        title, data = self._model.getProviderData(self._resolver, provider)
        self._dialog = ProviderView(self._ctx, ProviderHandler(self), self._view.getWindow().Peer, title)
        self._dialog.initDialog(*data)
        if self._dialog.execute() == OK:
            self._model.saveProviderData(provider, *self._dialog.getDialogData())
            if new:
                self._view.addProvider(provider)
                self._view.toggleProviderButtons()
            self._setActivePath()
        self._dialog.dispose()
        self._dialog = None

    def _showScope(self, new):
        scope = self._view.getScope()
        provider = self._view.getProvider()
        data = self._model.getScopeData(self._resolver, scope)
        self._dialog = ScopeView(self._ctx, ScopeHandler(self), self._view.getWindow().Peer, *data)
        if self._dialog.execute() == OK:
            self._model.saveScopeData(scope, provider, self._dialog.getScopeValues())
            if new:
                self._view.addScope(scope)
                self._view.toggleScopeButtons()
            self._setActivePath()
        self._dialog.dispose()
        self._dialog = None

    def _getPropertySetInfo(self):
        properties = {}
        ro = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        properties['PageId'] = getProperty('PageId', 'short', ro)
        properties['Window'] = getProperty('Window', 'com.sun.star.awt.XWindow', ro)
        return properties

