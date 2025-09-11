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

import unohelper

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.uno import Exception as UnoException

from com.sun.star.ui.dialogs import XWizardPage

from .oauth2handler import WindowHandler

from .oauth2view import OAuth2View

from ...unotool import createMessageBox
from ...unotool import getStringResource

from ...configuration import g_identifier

import traceback


class OAuth2Manager(unohelper.Base,
                    XWizardPage):
    def __init__(self, ctx, wizard, model, pageid, parent):
        self._ctx = ctx
        self._wizard = wizard
        self._model = model
        self._pageid = pageid
        self._view = OAuth2View(ctx, WindowHandler(self), parent)
        self._resolver = getStringResource(ctx, g_identifier, 'dialogs', 'PageWizard4')

# XWizardPage
    @property
    def PageId(self):
        return self._pageid
    @property
    def Window(self):
        return self._view.getWindow()

    def activatePage(self):
        self._view.initView(*self._model.getTokenData(self._resolver))
        self._wizard.activatePath(1, True)

    def commitPage(self, reason):
        return True

    def canAdvance(self):
        return not self._view.hasError()

# XComponent
    def dispose(self):
        pass
    def addEventListener(self, listener):
        pass
    def removeEventListener(self, listener):
        pass

# OAuth2Manager setter methods
    def updateToken(self):
        self._view.setToken(*self._model.getUserTokenData(self._resolver))

    def deleteUser(self):
        dialog = createMessageBox(self._view.getWindow().Peer, *self._model.getMessageBoxData())
        if dialog.execute() == OK:
            self._model.deleteUser()
            self._wizard.travelPrevious()
        dialog.dispose()

    def refreshToken(self):
        try:
            self._model.refreshToken(self._wizard)
        except UnoException as e:
            self._view.showError(e.Message)
            self._wizard.updateTravelUI()
        else:
            self._view.setToken(*self._model.getUserTokenData(self._resolver))

