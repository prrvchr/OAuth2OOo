#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.auth import XOAuth2Service
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE


from oauth2 import OAuth2OOo
from oauth2 import NoOAuth2
from oauth2 import Enumerator
from oauth2 import InputStream
from oauth2 import Uploader
from oauth2 import KeyMap
from oauth2 import getSessionMode
from oauth2 import execute
from oauth2 import getLogger

from oauth2 import OAuth2Configuration
from oauth2 import WizardController
from oauth2 import createService
from oauth2 import getTokenParameters
from oauth2 import getRefreshParameters
from oauth2 import g_identifier

import sys
import certifi
import traceback

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import socket
try:
    import ssl
except ImportError as e:
    logger = getLogger(uno.getComponentContext())
    logger.logp(SEVERE, "OAuth2Service", "import ssl", e)


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)
import requests


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Service' % g_identifier


class OAuth2Service(unohelper.Base,
                    XServiceInfo,
                    XOAuth2Service):
    def __init__(self, ctx):
        self.ctx = ctx
        self.Setting = OAuth2Configuration(self.ctx)
        self.Session = self._getSession()
        self.Logger = getLogger(self.ctx)
        self.Error = ''

    @property
    def ResourceUrl(self):
        return self.Setting.Url.Id
    @ResourceUrl.setter
    def ResourceUrl(self, url):
        self.Setting.Url.Id = url
    @property
    def UserName(self):
        return self.Setting.Url.Scope.Provider.User.Id
    @UserName.setter
    def UserName(self, name):
        self.Setting.Url.Scope.Provider.User.Id = name

    # XOAuth2Service
    def initializeSession(self, url):
        self.Setting.Url.Id = url

    def initializeUser(self, name):
        if not name:
            return False
        self.Setting.Url.Scope.Provider.User.Id = name
        return self._isAuthorized()

    def getKeyMap(self):
        return KeyMap()

    def getSessionMode(self, host):
        return getSessionMode(self.ctx, host)

    def getToken(self, format=''):
        level = INFO
        msg = "Request Token ... "
        if not self._isAuthorized():
            level = SEVERE
            msg += "ERROR: Cannot InitializeSession()..."
            token = ''
        elif self.Setting.Url.Scope.Provider.User.HasExpired:
            token = self._refreshToken()
            msg += "Refresh needed ... Done"
        else:
            token = self.Setting.Url.Scope.Provider.User.AccessToken
            msg += "Get from configuration ... Done"
        self.Logger.logp(level, "OAuth2Service", "getToken()", msg)
        if format:
            token = format % token
        return token

    def execute(self, parameter):
        return execute(self.Session, parameter)

    def getEnumerator(self, parameter):
        return Enumerator(self.Session, parameter)

    def getInputStream(self, parameter, chunk, buffer):
        return InputStream(self.Session, parameter, chunk, buffer)

    def getUploader(self, datasource):
        return Uploader(self.ctx, self.Session, datasource)

    def logp(self, level, source, method, message):
        if self.Logger.isLoggable(level):
            self.Logger.logp(level, source, method, message)

    def _isAuthorized(self):
        msg = "OAuth2 initialization... "
        if self.Setting.Url.Scope.Authorized:
            msg += "Done"
            self.Logger.logp(INFO, "OAuth2Service", "getToken()", msg)
            return True
        else:
            msg += "AuthorizationCode needed ... "
            code, codeverifier = self._getAuthorizationCode()
            if code is not None:
                msg += "Done ... Request Token ... "
                token = self._getTokens(code, codeverifier)
                if token:
                    msg += "Done"
                    self.Logger.logp(INFO, "OAuth2Service", "getToken()", msg)
                    return True
        msg += "ERROR: Aborted!!!"
        self.Logger.logp(SEVERE, "OAuth2Service", "getToken()", msg)
        return False

    def _getSession(self):
        #if sys.version_info[0] < 3:
        #    requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        session.mount('https://', MyAdapter())
        session.auth = OAuth2OOo(self)
        session.codes = requests.codes
        return session

    def _getAuthorizationCode(self):
        code = None
        self.Logger.logp(INFO, "OAuth2Service", "_getAuthorizationCode", "WizardController Loading...")
        controller = WizardController(self.ctx, self.ResourceUrl, self.UserName)
        self.Logger.logp(INFO, "OAuth2Service", "_getAuthorizationCode", "WizardController Loading... Done")
        if controller.Handler.Wizard.execute():
            if controller.AuthorizationCode.IsPresent:
                controller.Configuration.commit()
                code = controller.AuthorizationCode.Value
                self.UserName = controller.UserName
                self.ResourceUrl = controller.ResourceUrl
        controller.Server.cancel()
        self.Logger.logp(INFO, "OAuth2Service", "_getAuthorizationCode", "WizardController closed")
        return code, controller.CodeVerifier

    def _getTokens(self, code, codeverifier):
        url = self.Setting.Url.Scope.Provider.TokenUrl
        data = getTokenParameters(self.Setting, code, codeverifier)
        message = "Make Http Request: %s?%s" % (url, data)
        self.Logger.logp(INFO, "OAuth2Service", "_getTokens", message)
        response = self._getResponseFromRequest(url, data)
        return self._getTokenFromResponse(response)

    def _refreshToken(self):
        url = self.Setting.Url.Scope.Provider.TokenUrl
        data = getRefreshParameters(self.Setting)
        message = "Make Http Request: %s?%s" % (url, data)
        self.Logger.logp(INFO, "OAuth2Service", "_refreshToken", message)
        response = self._getResponseFromRequest(url, data)
        return self._getTokenFromResponse(response)

    def _getCertificat(self):
        verify = True
        if sys.version_info[0] < 3:
            verify = certifi.old_where()
        return verify

    def _getResponseFromRequest(self, url, data):
        response = {}
        timeout = self.Setting.RequestTimeout
        #verify = self._getCertificat()
        try:
            with self.Session as s:
                with s.post(url, data=data, timeout=timeout, auth=NoOAuth2()) as r:
                    if r.status_code == s.codes.ok:
                        response = r.json()
                    else:
                        msg = r.text
                        self.Logger.logp(SEVERE, "OAuth2Service", "_getResponseFromRequest", msg)
        except Exception as e:
            self.Logger.logp(SEVERE, "OAuth2Service", "_getResponseFromRequest", "%s" % e)
        return response

    def _getTokenFromResponse(self, response):
        refresh = response.get('refresh_token', None)
        if refresh:
            self.Setting.Url.Scope.Provider.User.RefreshToken = refresh
        expires = response.get('expires_in', None)
        if expires:
            self.Setting.Url.Scope.Provider.User.ExpiresIn = expires
        token = response.get('access_token', '')
        if token:
            self.Setting.Url.Scope.Provider.User.AccessToken = token
            scope = self.Setting.Url.Scope.Values
            self.Setting.Url.Scope.Provider.User.Scope = scope
            self.Setting.Url.Scope.Provider.User.NeverExpires = expires is None
            self.Setting.Url.Scope.Provider.User.commit()
            level = INFO
        else:
            level = SEVERE
        self.Logger.logp(level, "OAuth2Service", "_getTokenFromResponse", "%s" % response)
        return token

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
