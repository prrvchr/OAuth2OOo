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

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.auth import RefreshTokenException

from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import XInitialization
from com.sun.star.task import XInteractionHandler2

from oauth20 import UserView
from oauth20 import UserHandler
from oauth20 import HandlerModel

from oauth20 import g_identifier

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Handler' % g_identifier


class OAuth2Handler(unohelper.Base,
                    XServiceInfo,
                    XInitialization,
                    XInteractionHandler2):
    def __init__(self, ctx):
        self._ctx = ctx
        self._model = HandlerModel(ctx)
        self._parent = None
        self._dialog = None

    # XInitialization
    def initialize(self, properties):
        for property in properties:
            if property.Name == 'Parent':
                self._parent = property.Value

    # XInteractionHandler2, XInteractionHandler
    def handle(self, interaction):
        self.handleInteractionRequest(interaction)
    def handleInteractionRequest(self, interaction):
        # TODO: interaction.getRequest() does not seem to be functional under LibreOffice !!!
        # TODO: throw error AttributeError: "args"
        # TODO: on File "/usr/lib/python3/dist-packages/uno.py"
        # TODO: at line 525 in "_uno_struct__setattr__"
        # TODO: as a workaround we must set an "args" attribute of type "sequence<any>" to
        # TODO: IDL file of com.sun.star.auth.OAuth2Request Exception who is normally returned...
        request = interaction.getRequest()
        url = request.ResourceUrl
        user = request.UserName
        if user != '':
            approved = self._getToken(interaction, url, user, request.Format)
        else:
            approved = self._showUserDialog(interaction, url, request.Message)
        return approved

    def _getToken(self, interaction, url, user, format):
        token = ''
        status = 0
        self._model.initialize(url, user)
        try:
            if self._isAuthorized():
                token = self._model.getAccessToken(self)
                status = 1
        except RefreshTokenException:
            status = 0
        continuation = interaction.getContinuations()[status]
        if status:
            if format:
                token = format % token
            continuation.setToken(token)
        continuation.select()
        return status == 1

    def _isAuthorized(self):
        if self._model.isOAuth2():
            return self._model.isAuthorized()
        return False

    def _showUserDialog(self, interaction, url, message):
        title, label = self._model.getUserData(url, message)
        self._dialog = UserView(self._ctx, UserHandler(self), self._parent, title, label)
        status = self._dialog.execute()
        approved = status == OK
        continuation = interaction.getContinuations()[status]
        if approved:
            continuation.setUserName(self._dialog.getUser())
        continuation.select()
        self._dialog.dispose()
        self._dialog = None
        return approved

    def setUserName(self, email):
        self._dialog.enableOkButton(self._model.isEmailValid(email))

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OAuth2Handler,
                                         g_ImplementationName,
                                        (g_ImplementationName,))

