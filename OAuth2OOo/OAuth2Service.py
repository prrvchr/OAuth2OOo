#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo

import oauth2
from oauth2 import PyPropertySet, PyInitialization
import sys
import certifi
import requests

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.OAuth2Service"


class PyOAuth2Service(unohelper.Base, XServiceInfo, PyPropertySet, PyInitialization):
    def __init__(self, ctx, *namedvalues):
        self.ctx = ctx
        self.properties = self._getPropertySetInfo()
        self.Setting = oauth2.createService(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo.SettingReader")
        self.initialize(namedvalues)

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["ResourceUrl"] = oauth2.getProperty("ResourceUrl", "string", transient)
        properties["UserName"] = oauth2.getProperty("UserName", "string", transient)
        properties["Token"] = oauth2.getProperty("Token", "string", readonly)
        properties["Setting"] = oauth2.getProperty("Setting", "com.sun.star.uno.XInterface", readonly)
        return properties

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
    @property
    def Token(self):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        if not self.Setting.Url.Provider.Scope.Authorized:
            self.Setting.Logger.logp(level, "PyOAuth2Service", "getToken", "AuthorizationCode needed")
            code, codeverifier = self._getAuthorizationCode()
            token = "" if code is None else self._getTokens(code, codeverifier)
        elif self.Setting.Url.Provider.Scope.User.ExpiresIn < self.Setting.HandlerTimeout:
            self.Setting.Logger.logp(level, "PyOAuth2Service", "getToken", "Refresh token needed")
            token = self._refreshToken()
        else:
            self.Setting.Logger.logp(level, "PyOAuth2Service", "getToken", "Get token from configuration")
            token = self.Setting.Url.Provider.Scope.User.AccessToken
        return token

    def _getAuthorizationCode(self):
        code = None
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Setting.Logger.logp(level, "PyOAuth2Service", "_getAuthorizationCode", "WizardController Loading...")
        service = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardController"
        controller = oauth2.createService(self.ctx, service, ResourceUrl=self.ResourceUrl, UserName=self.UserName)
        codeverifier = controller.CodeVerifier
        self.Setting.Logger.logp(level, "PyOAuth2Service", "_getAuthorizationCode", "WizardController Loading... Done")
        if controller.Wizard.execute():
            controller.Configuration.commit()
            code = controller.AuthorizationCode
            self.UserName = controller.UserName
            self.ResourceUrl = controller.ResourceUrl
        controller.dispose()
        self.Setting.Logger.logp(level, "PyOAuth2Service", "_getAuthorizationCode", "WizardController closed")
        return code, codeverifier

    def _getTokens(self, code, codeverifier):
        url = self.Setting.Url.Provider.TokenUrl
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {}
        data["client_id"] = self.Setting.Url.Provider.ClientId
        data["redirect_uri"] = self.Setting.Url.Provider.RedirectUri
        data["grant_type"] = "authorization_code"
        data["scope"] = self.Setting.Url.Provider.Scope.Values
        data["code"] = code
        if self.Setting.Url.Provider.CodeChallenge:
            data["code_verifier"] = codeverifier
        if self.Setting.Url.Provider.ClientSecret:
            data["client_secret"] = self.Setting.Url.Provider.ClientSecret
        message = "Make Http Request: %s?%s" % (url, data)
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Setting.Logger.logp(level, "PyOAuth2Service", "_getTokens", message)
        response = self._getResponseFromRequest(url, headers, data)
        return self._getTokenFromResponse(response)

    def _refreshToken(self):
        url = self.Setting.Url.Provider.TokenUrl
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {}
        data["client_id"] = self.Setting.Url.Provider.ClientId
        data["refresh_token"] = self.Setting.Url.Provider.Scope.User.RefreshToken
        data["grant_type"] = "refresh_token"
        data["scope"] = self.Setting.Url.Provider.Scope.User.Scope
        data["redirect_uri"] = self.Setting.Url.Provider.RedirectUri
        if self.Setting.Url.Provider.ClientSecret:
            data["client_secret"] = self.Setting.Url.Provider.ClientSecret
        message = "Make Http Request: %s?%s" % (url, data)
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Setting.Logger.logp(level, "PyOAuth2Service", "_refreshToken", message)
        response = self._getResponseFromRequest(url, headers, data)
        return self._getTokenFromResponse(response)

    def _getCertificat(self):
        verify = True
        if sys.version_info[0] == 2:
            requests.packages.urllib3.disable_warnings()
            verify = certifi.old_where()
        return verify

    def _getResponseFromRequest(self, url, headers, data):
        response = {}
        timeout = self.Setting.RequestTimeout
        verify = self._getCertificat()
        try:
            response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=verify).json()
        except Exception as e:
            level = uno.getConstantByName("com.sun.star.logging.LogLevel.SEVERE")
            self.Setting.Logger.logp(level, "PyOAuth2Service", "_getResponseFromRequest", "%s" % e)
        return response

    def _getTokenFromResponse(self, response):
        token = ""
        if "refresh_token" in response:
            self.Setting.Url.Provider.Scope.User.RefreshToken = response["refresh_token"]
        if "access_token" in response:
            token = response["access_token"]
            self.Setting.Url.Provider.Scope.User.AccessToken = token
        if "expires_in" in response:
            self.Setting.Url.Provider.Scope.User.ExpiresIn = response["expires_in"]
        if token:
            scope = self.Setting.Url.Provider.Scope.Values
            self.Setting.Url.Provider.Scope.User.Scope = scope
            self.Setting.Url.Provider.Scope.User.commit()
            level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        else:
            level = uno.getConstantByName("com.sun.star.logging.LogLevel.SEVERE")
        self.Setting.Logger.logp(level, "PyOAuth2Service", "_getTokenFromResponse", "%s" % response)
        return token

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(PyOAuth2Service,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services
