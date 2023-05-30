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

from com.sun.star.lang import XComponent
from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import EventObject
from com.sun.star.auth import XOAuth2Service
from com.sun.star.auth import RefreshTokenException

from com.sun.star.rest import RequestException

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

from oauth2 import getAccessToken
from oauth2 import getParentWindow
from oauth2 import getSessionMode
from oauth2 import showOAuth2Wizard

from oauth2 import RequestParameter

from oauth2 import getRequestResponse
from oauth2 import getInputStream
from oauth2 import getSimpleFile
from oauth2 import download
from oauth2 import upload

from oauth2 import getLogger

from oauth2 import g_oauth2
from oauth2 import g_defaultlog
from oauth2 import g_basename

from oauth2 import OAuth2Model
from oauth2 import OAuth2OOo

import requests
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = g_oauth2


class OAuth2Service(unohelper.Base,
                    XComponent,
                    XServiceInfo,
                    XOAuth2Service):
    def __init__(self, ctx):
        self._ctx = ctx
        self._result = None
        self._model = OAuth2Model(ctx, True)
        self._session = self._getSession()
        self._listeners = []
        self._mode = OFFLINE
        self._logger = getLogger(ctx, g_defaultlog, g_basename)

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
    def isOnLine(self):
        return self._mode != OFFLINE
    def isOffLine(self, host):
        self._mode = getSessionMode(self._ctx, host)
        return self._mode != ONLINE

    def unquoteUrl(self, url):
        return requests.utils.unquote(url)

    def initializeUrl(self, url):
        return self._model.initializeUrl(url)

    def initializeSession(self, url, user):
        return self._model.initializeSession(url, user)

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
        self._logger.logp(INFO, 'OAuth2Service', 'getAuthorization()', msg)
        return authorized

    def getToken(self, format=''):
        try:
            token = getAccessToken(self._ctx, self._model, getParentWindow(self._ctx))
        except RefreshTokenException as e:
            e.Context = self
            raise e
        if format:
            token = format % token
        return token

    def getRequestParameter(self, name):
        return RequestParameter(name)

    def execute(self, parameter):
        print("OAuth2Service.executeRequest() 1")
        return getRequestResponse(self._ctx, self._session, parameter, self.Timeout)

    def getInputStream(self, parameter, chunk, decode):
        return getInputStream(self._session, parameter, self.Timeout, chunk, decode)

    def download(self, parameter, url, chunk, retry, delay):
        return download(self._ctx, self._logger, self._session, parameter, url, self.Timeout, chunk, retry, delay)

    def upload(self, parameter, url, chunk, retry, delay):
        return upload(self._ctx, self._logger, self._session, parameter, url, self.Timeout, chunk, retry, delay)

    # Private method
    def _getSession(self):
        session = requests.Session()
        session.auth = OAuth2OOo(self)
        session.codes = requests.codes
        return session

    # XComponent
    def dispose(self):
        source = EventObject(self)
        for listener in self._listeners:
            listener.disposing(source)
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

