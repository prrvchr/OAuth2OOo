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

from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import XInitialization
from com.sun.star.task import XInteractionHandler2

from oauth2 import getDialog
from oauth2 import getStringResource

from oauth2 import UserView
from oauth2 import UserHandler
from oauth2 import OAuth2Model
from oauth2 import showOAuth2Wizard

from oauth2 import g_extension
from oauth2 import g_identifier

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
        self._model = OAuth2Model(ctx, True)
        self._parent = None
        self._dialog = None
        self._resources = getStringResource(ctx, g_identifier, g_extension)

    # XInitialization
    def initialize(self, properties):
        print("OAuth2Handler.initialize() 1")
        for property in properties:
            print("OAuth2Handler.initialize() 2 %s" % property.Name)
            if property.Name == 'Parent':
                self._parent = property.Value
                print("OAuth2Handler.initialize() 3 %s" % self._parent)

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
        print("OAuth2Handler.handleInteractionRequest() 1")
        request = interaction.getRequest()
        url = request.ResourceUrl
        user = request.UserName
        if user != '':
            approved = self._getToken(interaction, url, user, request.Format)
        else:
            approved = self._showUserDialog(interaction, url, request.Message)
        return approved

    def _getToken(self, interaction, url, user, format):
        self._model.initialize(url, user)
        if not self._model.isAuthorized():
            token = self._getTokenFromWizard()
        elif self._model.isAccessTokenExpired():
            token = self._model.getRefreshedToken()
        else:
            token = self._model.getToken()
        status = 1 if token != '' else 0
        continuation = interaction.getContinuations()[status]
        if status:
            if format:
                token = format % token
            continuation.setToken(token)
        continuation.select()
        return status == 1

    def _getTokenFromWizard(self):
        token = ''
        state, result = showOAuth2Wizard(self._ctx, self._model, self._parent)
        if state == SUCCESS:
            url, user, token = result
        return token

    def _showUserDialog(self, interaction, url, message):
        try:
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
        except Exception as e:
            msg = "Error: %s" % traceback.print_exc()
            print(msg)

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

