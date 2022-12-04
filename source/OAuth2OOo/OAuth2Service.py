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
from com.sun.star.lang import EventObject
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
from oauth2 import disposeLogger
from oauth2 import execute
from oauth2 import getAccessToken
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
        self._listeners = []
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
        return self._model.initializeSession(url, user)

    def getKeyMap(self):
        return KeyMap()

    def getSessionMode(self, host):
        return getSessionMode(self._ctx, host)

    def getAuthorization(self, url, user, close=True, parent=None):
        authorized = False
        msg = "Request Authorization ... "
        self._model.initialize(url, user, close)
        state, result = showOAuth2Wizard(self._ctx, self._model, parent)
        if state == SUCCESS:
            url, user, token = result
            authorized = self.initializeSession(url, user)
        msg += "Authorization has been granted..." if authorized else "Authorization was not granted..."
        logMessage(self._ctx, INFO, msg, 'OAuth2Service', 'getAuthorization()')
        return authorized

    def getToken(self, format=''):
        token = getAccessToken(self._ctx, self._model, getParentWindow(self._ctx))
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

    # XComponent
    def dispose(self):
        source = EventObject(self)
        for listener in self._listeners:
            listener.disposing(source)
        disposeLogger()
    def addEventListener(self, listener):
        self._listeners.append(listener)
    def removeEventListener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

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

