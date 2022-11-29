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

from com.sun.star.lang import XServiceInfo
from com.sun.star.auth import XOAuth2Service

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK
from com.sun.star.ui.dialogs.ExecutableDialogResults import CANCEL

from com.sun.star.frame import XDispatchResultListener
from com.sun.star.frame.FrameSearchFlag import GLOBAL
from com.sun.star.frame.DispatchResultState import SUCCESS

from com.sun.star.uno import Exception as UnoException
from com.sun.star.auth import OAuth2Request

from oauth2 import KeyMap

from oauth2 import createService
from oauth2 import execute
from oauth2 import getParentWindow
from oauth2 import getSessionMode
from oauth2 import logMessage
from oauth2 import showOAuth2Wizard

from oauth2 import Request
from oauth2 import Response
from oauth2 import Enumeration
from oauth2 import Enumerator
from oauth2 import Iterator
from oauth2 import InputStream
from oauth2 import Uploader

from oauth2 import g_extension
from oauth2 import g_identifier
from oauth2 import g_oauth2

from oauth2 import OAuth2Model
from oauth2 import OAuth2OOo
from oauth2 import NoOAuth2

import requests
import time
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = g_oauth2


class OAuth2Service(unohelper.Base,
                    XServiceInfo,
                    XOAuth2Service):
    def __init__(self, ctx):
        self._ctx = ctx
        self._result = None
        self._model = OAuth2Model(ctx, True)
        self._session = self._getSession()
        self._parent = None
        self._warnings = []
        self._mode = OFFLINE

    @property
    def ResourceUrl(self):
        return self._model.Url
    @property
    def ProviderName(self):
        return self._model.Provider
    @property
    def UserName(self):
        return self._model.User
    @property
    def Timeout(self):
        return self._model.Timeout

    # XOAuth2Service
    def getWarnings(self):
        if self._warnings:
            return self._warnings.pop(0)
        return None
    def clearWarnings(self):
        self._warnings = []

    def isOnLine(self):
        return self._mode != OFFLINE
    def isOffLine(self, host):
        self._mode = getSessionMode(self._ctx, host)
        return self._mode != ONLINE

    def unquoteUrl(self, url):
        return requests.utils.unquote(url)

    def initializeUrl(self, url):
        self._model.initializeUrl(url)
        return True

    def initializeSession(self, url, user):
        self._model.initialize(url, user)
        return self._model.isInitialized()

    def getKeyMap(self):
        return KeyMap()

    def getSessionMode(self, host):
        return getSessionMode(self._ctx, host)

    def getAuthorization(self, url, user, close=True, parent=None):
        print("OAuth2Service.getAuthorization() 1 %s" % user)
        authorized = False
        self._model.initialize(url, user, close)
        state, result = showOAuth2Wizard(self._ctx, self._model, parent)
        print("OAuth2Service.getAuthorization() 2")
        if state == SUCCESS:
            url, user, token = result
            authorized = self.initializeSession(url, user)
        print("OAuth2Service.getAuthorization() 3")
        return authorized

    def getToken(self, format=''):
        level = INFO
        msg = "Request Token ... "
        if not self._isAuthorized():
            level = SEVERE
            msg += "ERROR: Cannot InitializeSession()..."
            token = ''
        elif self._model.isAccessTokenExpired():
            token = self._model.getRefreshedToken()
        else:
            token = self._model.getToken()
            msg += "Get from configuration ... Done"
        logMessage(self._ctx, level, msg, 'OAuth2Service', 'getToken()')
        if format:
            token = format % token
        return token

    def execute(self, parameter):
        response, error = execute(self._session, parameter, self.Timeout)
        if error:
            logMessage(self._ctx, SEVERE, error, 'OAuth2Service', 'execute()')
            self._warnings.append(self._getException(error))
        return response

    def getRequest(self, parameter, parser):
        return Request(self._session, parameter, self.Timeout, parser)

    def getResponse(self, parameter, parser):
        return Response(self._session, parameter, self.Timeout, parser)

    def getIterator(self, parameter, parser):
        return Iterator(self._session, self.Timeout, parameter, parser)

    def getEnumeration(self, parameter, parser):
        return Enumeration(self._session, parameter, self.Timeout, parser)

    def getEnumerator(self, parameter):
        return Enumerator(self._ctx, self._session, parameter, self.Timeout)

    def getInputStream(self, parameter, chunk, buffer):
        return InputStream(self._ctx, self._session, parameter, chunk, buffer, self.Timeout)

    def getUploader(self, chunk, url, user):
        return Uploader(self._ctx, self._session, chunk, url, user.callBack, self.Timeout)

    def _getSession(self):
        session = requests.Session()
        session.auth = OAuth2OOo(self)
        session.codes = requests.codes
        return session

    def _isAuthorized(self):
        print("OAuth2Service._isAuthorized() 1")
        if self._model.isInitialized() and self._model.isUrlScopeAuthorized():
            return True
        print("OAuth2Service._isAuthorized() 2")
        msg = "OAuth2 initialization ... AuthorizationCode needed ..."
        parent = getParentWindow(self._ctx) if self._parent is None else self._parent
        print("OAuth2Service._isAuthorized() 3")
        if self.getAuthorization(self.ResourceUrl, self.UserName, True, parent):
            print("OAuth2Service._isAuthorized() 4")
            msg += " Done"
            logMessage(self._ctx, INFO, msg, 'OAuth2Service', '_isAuthorized()')
            return True
        msg += " ERROR: Wizard Aborted!!!"
        logMessage(self._ctx, SEVERE, msg, 'OAuth2Service', '_isAuthorized()')
        print("OAuth2Service._isAuthorized() 5")
        return False

    def _getToolkit(self):
        return createService(self._ctx, 'com.sun.star.awt.Toolkit')

    def _isDocument(self, frame):
        controller = frame.getController()
        return controller.getModel() is not None

    def _getException(self, message):
        error = UnoException()
        error.Message = message
        error.Context = self
        return error

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OAuth2Service,
                                         g_ImplementationName,
                                        (g_ImplementationName,))

