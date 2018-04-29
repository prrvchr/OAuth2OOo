#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.task import XJob

import unotools
from unotools import PyServiceInfo, PyPropertySet, PyInitialization
import sys
import certifi
import requests

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.OAuth2Service"


class PyOAuth2Service(unohelper.Base, PyServiceInfo, PyPropertySet, PyInitialization, XJob):
    def __init__(self, ctx, *namedvalues):
        self.ctx = ctx
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties = {}
        self.properties["ResourceUrl"] = unotools.getProperty("ResourceUrl", "string", transient)
        self.properties["UserName"] = unotools.getProperty("UserName", "string", transient)
        self.properties["Setting"] = unotools.getProperty("Setting", "com.sun.star.uno.XInterface", readonly)
        self._Setting = unotools.createService(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo.SettingReader")
        self.initialize(namedvalues)

    @property
    def ResourceUrl(self):
        return self.Setting.Url.Id
    @ResourceUrl.setter
    def ResourceUrl(self, url):
        if self.Setting.Url.Id != url:
            self.Setting.Url.Id = url
            self.Setting.update()
    @property
    def UserName(self):
        return self.Setting.Url.Provider.Scope.User.Id
    @UserName.setter
    def UserName(self, name):
        if self.Setting.Url.Provider.Scope.User.Id != name:
            self.Setting.Url.Provider.Scope.User.Id = name
            self.Setting.Url.Provider.Scope.User.update()
    @property
    def Setting(self):
        return self._Setting

    # XJob
    def execute(self, namedvalues=()):
        self.initialize(namedvalues)
        token = self.Setting.Url.Provider.Scope.User.AccessToken
        if not token or self.Setting.Url.Provider.Scope.NeedAuthorization:
            code, codeverifier = self._getAuthorizationCode()
            if code is not None:
                token = self._getTokens(code, codeverifier)
        elif self.Setting.Url.Provider.Scope.User.ExpiresIn < self.Setting.HandlerTimeout:
            token = self._refreshToken()
        return token

    def _getAuthorizationCode(self):
        code = None
        service = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardController"
        controller = unotools.createService(self.ctx, service, ResourceUrl=self.ResourceUrl, UserName=self.UserName)
        codeverifier = controller.CodeVerifier
        if controller.Wizard.execute():
            code = controller.AuthorizationCode
            controller.Configuration.commit()
            self.UserName = controller.UserName
            self.ResourceUrl = controller.ResourceUrl
        controller.dispose()
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
        timeout = self.Setting.RequestTimeout
        verify = self._getCertificat()
        response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=verify)
        return self._getTokenFromResponse(response.json())

    def _refreshToken(self):
        url = self.Setting.Url.Provider.TokenUrl
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {}
        data["client_id"] = self.Setting.Url.Provider.ClientId
        data["refresh_token"] = self.Setting.Url.Provider.Scope.User.RefreshToken
        data["grant_type"] = "refresh_token"
        data["scope"] = self.Setting.Url.Provider.Scope.Values
        data["redirect_uri"] = self.Setting.Url.Provider.RedirectUri
        if self.Setting.Url.Provider.ClientSecret:
            data["client_secret"] = self.Setting.Url.Provider.ClientSecret
        timeout = self.Setting.RequestTimeout
        verify = self._getCertificat()
        response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=verify)
        return self._getTokenFromResponse(response.json())

    def _getCertificat(self):
        verify = True
        if sys.version_info[0] == 2:
            requests.packages.urllib3.disable_warnings()
            verify = certifi.old_where()
        return verify

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
        return token


g_ImplementationHelper.addImplementation(PyOAuth2Service,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services
