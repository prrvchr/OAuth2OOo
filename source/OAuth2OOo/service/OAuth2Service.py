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

from com.sun.star.lang import EventObject
from com.sun.star.lang import XComponent
from com.sun.star.lang import XServiceInfo
from com.sun.star.auth import XOAuth2Service
from com.sun.star.auth import RefreshTokenException

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE

from oauth2 import RequestParameter
from oauth2 import OAuth2Model
from oauth2 import OAuth2OOo

from oauth2 import executeDispatch
from oauth2 import getConfiguration
from oauth2 import isAuthorized
from oauth2 import getPropertyValueSet

from oauth2 import getSessionMode

from oauth2 import getRequestResponse
from oauth2 import getInputStream
from oauth2 import download
from oauth2 import upload

from oauth2 import getLogger

from oauth2 import g_identifier
from oauth2 import g_oauth2
from oauth2 import g_defaultlog
from oauth2 import g_basename

import requests
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = g_oauth2


class OAuth2Service(unohelper.Base,
                    XComponent,
                    XServiceInfo,
                    XOAuth2Service):
    # FIXME: We should be able to return None if the user is not
    # FIXME: authorized and the OAuth2 Wizard has been canceled.
    def __new__(cls, ctx, url='', user=''):
        if url and user:
            config = getConfiguration(ctx, g_identifier)
            urls = config.getByName('Urls')
            scopes = config.getByName('Scopes')
            providers = config.getByName('Providers')
            if not isAuthorized(urls, scopes, providers, url, user):
                # FIXME: The Url and User name must not be able to be changed (ie: ReadOnly)
                args = {'Url': url, 'UserName': user, 'ReadOnly': True}
                executeDispatch(ctx, 'oauth2:wizard', getPropertyValueSet(args))
                # The OAuth2 Wizard has been canceled
                if not isAuthorized(urls, scopes, providers, url, user):
                    return None
        return super(OAuth2Service, cls).__new__(cls)

    def __init__(self, ctx, url='', user=''):
        self._ctx = ctx
        self._model = OAuth2Model(ctx, url, user)
        self._session = self._getSession(url)
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
    def unquoteUrl(self, url):
        return requests.utils.unquote(url)

    def getSessionMode(self, host):
        return getSessionMode(self._ctx, host)

    def isAuthorized(self):
        if self._model.isOAuth2():
            return self._model.isAuthorized()
        return False

    def getToken(self, format=''):
        token = ''
        if self.isAuthorized():
            token = self._model.getAccessToken(self)
            if format:
                try:
                    token = format % token
                except:
                    pass
        return token

    def getRequestParameter(self, name):
        return RequestParameter(name)

    def execute(self, parameter):
        cls, mtd = 'OAuth2Service', 'execute'
        print("OAuth2Service.executeRequest() 1")
        return getRequestResponse(self._ctx, self, self._session, cls, mtd, parameter, self.Timeout)

    def getInputStream(self, parameter, chunk, decode):
        cls, mtd = 'OAuth2Service', 'getInputStream'
        return getInputStream(self._ctx, self, self._session, cls, mtd, parameter, self.Timeout, chunk, decode)

    def download(self, parameter, url, chunk, retry, delay):
        return download(self._ctx, self, self._logger, self._session, parameter, url, self.Timeout, chunk, retry, delay)

    def upload(self, parameter, url, chunk, retry, delay):
        return upload(self._ctx, self, self._logger, self._session, parameter, url, self.Timeout, chunk, retry, delay)

    # Private method
    def _getSession(self, url):
        session = requests.Session()
        if url:
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

