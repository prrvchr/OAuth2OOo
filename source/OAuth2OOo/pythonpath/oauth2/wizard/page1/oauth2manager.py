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
        self._setActivePath(self._view.getUser(), self._view.getUrl())
        self._view.setUserFocus()

    def commitPage(self, reason):
        print("OAuth2Manager.commitPage() 1")
        if reason == FORWARD:
            self._model.User = self._view.getUser()
            self._model.Url = self._view.getUrl()
            print("OAuth2Manager.commitPage() %s - %s" % (self._view.getUser(), self._view.getUrl()))
        return True

    def canAdvance(self):
        return self._model.isEmailValid(self._view.getUser())

# IspdbManager setter methods
    def setUser(self, user):
        self._setActivePath(user, self._view.getUrl())
        self._view.setUserFocus()

    def setUrl(self, url, urls):
        if url in urls:
            self._view.enableAddUrl(False)
            self._view.enableRemoveUrl(True)
            self._view.setUrl(*self._model.getUrlData(url))
        else:
            self._view.enableAddUrl(url != '')
            self._view.enableRemoveUrl(False)
        self._view.setUrlLabel(self._model.getUrlLabel(url))
        self._setActivePath(self._view.getUser(), url)
        self._view.setUrlFocus()

    def addUrl(self):
        pass

    def removeUrl(self):
        pass

    def setProvider(self, provider, providers):
        if provider in providers:
            self._view.enableAddProvider(False)
            self._view.enableEditProvider(True)
            self._view.enableRemoveProvider(True)
        else:
            self._view.enableAddProvider(provider != '')
            self._view.enableEditProvider(False)
            self._view.enableRemoveProvider(False)
        self._setActivePath(self._view.getUser(), self._view.getUrl())

    def addProvider(self):
        self._showProvider()

    def editProvider(self):
        self._showProvider()

    def setValue(self):
        enabled = self._model.isDialogValid(*self._dialog.getDialogValues())
        self._dialog.updateOk(enabled)

    def setChallenge(self, enabled):
        self._dialog.enableChallengeMethod(enabled)

    def setHttpHandler(self, enabled):
        self._dialog.enableHttpHandler(enabled)

    def _showProvider(self):
        provider = self._view.getProvider()
        self._dialog = ProviderView(self._ctx, ProviderHandler(self), self._view.getWindow().Peer, self._model.getProviderTitle(provider))
        self._dialog.initDialog(*self._model.getProviderData(provider))
        if self._dialog.execute() == OK:
            httphandler, data = self._dialog.getDialogData()
            self._model.saveProviderData(provider, httphandler, *data)
            self._wizard.activatePath(0 if httphandler else 1, True)
            self._wizard.updateTravelUI()
        self._dialog.dispose()
        self._dialog = None

    def removeProvider(self):
        dialog = self._getMessageBox()
        if dialog.execute() == OK:
            pass
        dialog.dispose()

    def _getMessageBox(self):
        return createMessageBox(self._view.getWindow().Peer, *self._model.getMessageBoxData())

    def setUrlScope(self, scope, scopes):
        if scope in scopes:
            self._view.enableAddScope(False)
            self._view.enableEditScope(True)
            self._view.enableRemoveScope(True)
        else:
            self._view.enableAddScope(scope != '')
            self._view.enableEditScope(False)
            self._view.enableRemoveScope(False)
        self._setActivePath(self._view.getUser(), self._view.getUrl())

    def addUrlScope(self):
        self._showScope()

    def editUrlScope(self):
        self._showScope()

    def _showScope(self):
        scope = self._view.getScope()
        provider = self._view.getProvider()
        self._dialog = ScopeView(self._ctx, ScopeHandler(self), self._view.getWindow().Peer, *self._model.getScopeData(scope))
        if self._dialog.execute() == OK:
            self._model.saveScopeData(scope, provider, self._dialog.getScopeValues())
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

    def _setActivePath(self, user, url):
        self._wizard.activatePath(self._model.getActivePath(user, url), True)
        self._wizard.updateTravelUI()

