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

import unohelper

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.ui.dialogs.WizardTravelType import FORWARD

from .oauth2handler import WindowHandler

from .oauth2view import OAuth2View

from .dialog import ProviderHandler
from .dialog import ProviderView
from .dialog import ScopeHandler
from .dialog import ScopeView

from oauth2 import createMessageBox

import traceback


class OAuth2Manager(unohelper.Base):
    def __init__(self, ctx, wizard, model, pageid, parent):
        self._ctx = ctx
        self._dialog = None
        self._wizard = wizard
        self._model = model
        self._pageid = pageid
        self._view = OAuth2View(ctx, WindowHandler(self), parent)
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
        print("OAuth2Manager.commitPage() 1")
        if reason == FORWARD:
            self._model.User = self._view.getUser()
            self._model.Url = self._view.getUrl()
            print("OAuth2Manager.commitPage() %s - %s" % (self._view.getUser(), self._view.getUrl()))
        return True

    def canAdvance(self):
        return not self._view.canAddItem() and self._model.isConfigurationValid(*self._view.getConfiguration())

# IspdbManager setter methods
    def setUser(self, user):
        self._setActivePath()
        self._view.setUserFocus()

    def setUrl(self, url, inlist):
        self._view.enableRemoveUrl(inlist)
        # TODO: The Add URL button must be activated after defining the Provider and/or Scope
        self._view.enableAddUrl(False)
        self._view.setUrl(*self._model.getUrl(url))
        self._view.setUrlLabel(self._model.getUrlLabel(url))
        self._setActivePath()
        self._view.setUrlFocus()

    def addUrl(self):
        pass

    def removeUrl(self):
        pass

    def setProvider(self, provider, inlist):
        url = self._view.getUrl()
        self._view.enableAddProvider(False if inlist else self._model.isValueValid(provider))
        self._view.enableEditProvider(inlist)
        self._view.enableRemoveProvider(inlist)
        self._view.setScopes(self._model.getScopeList(provider))
        self._view.toggleAddUrl(inlist)
        self._setActivePath()
        self._view.setProviderFocus()

    def addProvider(self):
        self._showProvider(True)

    def editProvider(self):
        self._showProvider(False)

    def setValue(self):
        enabled = self._model.isDialogValid(*self._dialog.getDialogValues())
        self._dialog.updateOk(enabled)

    def setChallenge(self, enabled):
        self._dialog.enableChallengeMethod(enabled)

    def setHttpHandler(self, enabled):
        self._dialog.enableHttpHandler(enabled)

    def _showProvider(self, new):
        provider = self._view.getProvider()
        self._dialog = ProviderView(self._ctx, ProviderHandler(self), self._view.getWindow().Peer, self._model.getProviderTitle(provider))
        self._dialog.initDialog(*self._model.getProviderData(provider))
        if self._dialog.execute() == OK:
            httphandler, data = self._dialog.getDialogData()
            self._model.saveProviderData(provider, httphandler, *data)
            if new:
                self._view.addProvider(provider)
                self._view.toggleProviderButtons()
        self._dialog.dispose()
        self._dialog = None

    def removeProvider(self):
        dialog = self._getMessageBox()
        if dialog.execute() == OK:
            pass
        dialog.dispose()

    def _getMessageBox(self):
        return createMessageBox(self._view.getWindow().Peer, *self._model.getMessageBoxData())

    def setUrlScope(self, scope, inlist):
        self._view.enableAddScope(False if inlist else self._model.isValueValid(scope))
        self._view.enableEditScope(inlist)
        self._view.enableRemoveScope(inlist)
        self._view.toggleAddUrl(inlist)
        self._setActivePath()
        self._view.setScopeFocus()

    def addUrlScope(self):
        self._showScope(True)

    def editUrlScope(self):
        self._showScope(False)

    def _showScope(self, new):
        scope = self._view.getScope()
        provider = self._view.getProvider()
        self._dialog = ScopeView(self._ctx, ScopeHandler(self), self._view.getWindow().Peer, *self._model.getScopeData(scope))
        if self._dialog.execute() == OK:
            self._model.saveScopeData(scope, provider, self._dialog.getScopeValues())
            if new:
                self._view.addScope(scope)
                self._view.toggleScopeButtons()
            self._setActivePath()
        self._dialog.dispose()
        self._dialog = None

    def removeUrlScope(self):
        dialog = self._getMessageBox()
        if dialog.execute() == OK:
            pass
        dialog.dispose()

    def selectScope(self, selected):
        self._dialog.updateRemove(selected)

    def setScope(self, scope):
        if scope in self._dialog.getScopeValues():
            self._dialog.updateAdd(False)
        else:
            self._dialog.updateAdd(scope != '')

    def addScope(self):
        self._dialog.addScope()

    def removeScope(self):
        self._dialog.removeScope()

    def _setActivePath(self):
        path = self._model.getActivePath(*self._view.getConfiguration())
        self._wizard.activatePath(path, True)
        self._wizard.updateTravelUI()

