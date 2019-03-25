#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.script import XDefaultMethod

from oauth2 import SettingReader
from oauth2 import WizardController
from oauth2 import PropertySet
from oauth2 import Initialization
from oauth2 import createService
from oauth2 import getProperty
from oauth2 import g_identifier

import sys
import certifi
import traceback

from oauth2 import requests

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Service' % g_identifier


class OAuth2Service(unohelper.Base,
                    XServiceInfo,
                    XDefaultMethod,
                    Initialization,
                    PropertySet):
    def __init__(self, ctx, *namedvalues):
        self.ctx = ctx
        self.Setting = SettingReader(self.ctx)
        self.initialize(namedvalues)
        self.Session = self._getSession()

    @property
    def ResourceUrl(self):
        return self.Setting.Url.Id
    @ResourceUrl.setter
    def ResourceUrl(self, url):
        if self.Setting.Url.Id != url:
            self.Setting.Url.Id = url
            self.Setting.Url.update()
    @property
    def UserName(self):
        return self.Setting.Url.Provider.Scope.User.Id
    @UserName.setter
    def UserName(self, name):
        if self.Setting.Url.Provider.Scope.User.Id != name:
            self.Setting.Url.Provider.Scope.User.Id = name
            self.Setting.Url.Provider.Scope.User.update()

    # XDefaultMethod
    def getDefaultMethodName(self):
        try:
            print("OAuth2Service.getDefaultMethodName()")
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
            msg = "Request Token ... "
            if not self.Setting.Url.Provider.Scope.Authorized:
                msg += "AuthorizationCode needed ... "
                code, codeverifier = self._getAuthorizationCode()
                if code is not None:
                    token = self._getTokens(code, codeverifier)
                    msg += "Done"
                else:
                    level = uno.getConstantByName('com.sun.star.logging.LogLevel.SEVERE')
                    msg += "ERROR: Aborted!!!"
                    token = ''
            elif self.Setting.Url.Provider.Scope.User.ExpiresIn < self.Setting.HandlerTimeout:
                token = self._refreshToken()
                msg += "Refresh needed ... Done"
            else:
                token = self.Setting.Url.Provider.Scope.User.AccessToken
                msg += "Get from configuration ... Done"
            self.Setting.Logger.logp(level, "OAuth2Service", "getToken()", msg)
            return token
        except Exception as e:
            print("OAUth2Service.getDefaultMethodName().Error: %s - %s" % (e, traceback.print_exc()))

    def _getSession(self):
        if sys.version_info[0] < 3:
            requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        session.codes = requests.codes
        return session

    def _getAuthorizationCode(self):
        try:
            code = None
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
            self.Setting.Logger.logp(level, "OAuth2Service", "_getAuthorizationCode", "WizardController Loading...")
            controller = WizardController(self.ctx, self.ResourceUrl, self.UserName)
            self.Setting.Logger.logp(level, "OAuth2Service", "_getAuthorizationCode", "WizardController Loading... Done")
            print("OAuth2Service._getAuthorizationCode() 1")
            if controller.Handler.Wizard.execute():
                print("OAuth2Service._getAuthorizationCode() 2")
                if controller.AuthorizationCode.IsPresent:
                    print("OAuth2Service._getAuthorizationCode() 3")
                    controller.Configuration.commit()
                    code = controller.AuthorizationCode.Value
                    self.UserName = controller.UserName
                    self.ResourceUrl = controller.ResourceUrl
            print("OAuth2Service._getAuthorizationCode() 4")
            controller.Server.cancel()
            self.Setting.Logger.logp(level, "OAuth2Service", "_getAuthorizationCode", "WizardController closed")
            return code, controller.CodeVerifier
        except Exception as e:
            print("PyOptionsDialog.__init__().Error: %s - %s" % (e, traceback.print_exc()))

    def _getTokens(self, code, codeverifier):
        url = self.Setting.Url.Provider.TokenUrl
        data = {}
        data['client_id'] = self.Setting.Url.Provider.ClientId
        data['redirect_uri'] = self.Setting.Url.Provider.RedirectUri
        data['grant_type'] = 'authorization_code'
        data['scope'] = self.Setting.Url.Provider.Scope.Values
        data['code'] = code
        if self.Setting.Url.Provider.CodeChallenge:
            data['code_verifier'] = codeverifier
        if self.Setting.Url.Provider.ClientSecret:
            data['client_secret'] = self.Setting.Url.Provider.ClientSecret
        message = "Make Http Request: %s?%s" % (url, data)
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Setting.Logger.logp(level, "OAuth2Service", "_getTokens", message)
        response = self._getResponseFromRequest(url, data)
        return self._getTokenFromResponse(response)

    def _refreshToken(self):
        url = self.Setting.Url.Provider.TokenUrl
        data = {}
        data['client_id'] = self.Setting.Url.Provider.ClientId
        data['refresh_token'] = self.Setting.Url.Provider.Scope.User.RefreshToken
        data['grant_type'] = 'refresh_token'
        data['scope'] = self.Setting.Url.Provider.Scope.User.Scope
        data['redirect_uri'] = self.Setting.Url.Provider.RedirectUri
        if self.Setting.Url.Provider.ClientSecret:
            data['client_secret'] = self.Setting.Url.Provider.ClientSecret
        message = "Make Http Request: %s?%s" % (url, data)
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Setting.Logger.logp(level, "OAuth2Service", "_refreshToken", message)
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
        verify = self._getCertificat()
        try:
            with self.Session as s:
                with s.post(url, data=data, timeout=timeout, verify=verify) as r:
                    if r.status_code == s.codes.ok:
                        response = r.json()
        except Exception as e:
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.SEVERE')
            self.Setting.Logger.logp(level, "OAuth2Service", "_getResponseFromRequest", "%s" % e)
        return response

    def _getTokenFromResponse(self, response):
        refresh = response.get('refresh_token', None)
        if refresh:
            self.Setting.Url.Provider.Scope.User.RefreshToken = refresh
        expires = response.get('expires_in', None)
        if expires:
            self.Setting.Url.Provider.Scope.User.ExpiresIn = expires
        token = response.get('access_token', '')
        if token:
            self.Setting.Url.Provider.Scope.User.AccessToken = token
            scope = self.Setting.Url.Provider.Scope.Values
            self.Setting.Url.Provider.Scope.User.Scope = scope
            self.Setting.Url.Provider.Scope.User.commit()
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        else:
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.SEVERE')
        self.Setting.Logger.logp(level, "OAuth2Service", "_getTokenFromResponse", "%s" % response)
        return token

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        transient = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.TRANSIENT')
        properties['ResourceUrl'] = getProperty('ResourceUrl', 'string', transient)
        properties['UserName'] = getProperty('UserName', 'string', transient)
        properties['Setting'] = getProperty('Setting', 'com.sun.star.uno.XInterface', readonly)
        return properties

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OAuth2Service,                             # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services
