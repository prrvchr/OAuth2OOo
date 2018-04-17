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
import traceback

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
        try:
            print("PyOAuth2Service.execute:1")
            self.initialize(namedvalues)
            print("PyOAuth2Service.execute:2")
            token = self.Setting.Url.Provider.Scope.User.AccessToken
            print("PyOAuth2Service.execute:3")
            if not token:
                print("PyOAuth2Service.execute:4")
                code, codeverifier = self._getAuthorizationCode()
                if code is not None:
                    print("PyOAuth2Service.execute:5")
                    token = self._getTokens(code, codeverifier)
            elif self.Setting.Url.Provider.Scope.User.ExpiresIn < self.Setting.HandlerTimeout:
                print("PyOAuth2Service.execute:6")
                token = self._refreshToken()
            print("PyOAuth2Service.execute:7")
            return token
        except Exception as e:
            print("PyOAuth2Service.execute error: %s" % e)
            traceback.print_exc()

    def _getAuthorizationCode(self):
        try:
            code = None
            service = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardController"
            controller = unotools.createService(self.ctx, service, ResourceUrl=self.ResourceUrl, UserName=self.UserName)
            codeverifier = controller.CodeVerifier
            if controller.Wizard.execute():
                code = controller.AuthorizationCode
                controller.Configuration.commit()
                self.UserName = controller.UserName
                self.ResourceUrl = controller.ResourceUrl
                print("_getAuthorizationCode: %s" % code)
            else:
                controller.cancel()
            controller.Wizard.DialogWindow.dispose()
            return code, codeverifier
        except Exception as e:
            print("PyOAuth2Service._getAuthorizationCode error: %s" % e)
            traceback.print_exc()

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
        print("_getTokens.data: %s" % data)
        response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=verify)
        print("_getTokens: %s" % (response.json(), ))
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
        print("_getTokens.verify: %s" % verify)
        response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=verify)
        print("_refreshToken: %s" % (response.json(), ))
        return self._getTokenFromResponse(response.json())

    def _getCertificat(self):
        verify = True
        if sys.version_info[0] == 2:
            requests.packages.urllib3.disable_warnings()
            verify = certifi.old_where()
        return verify

    def _getTokenFromResponse(self, response):
        token = None
        if "refresh_token" in response:
            self.Setting.Url.Provider.Scope.User.RefreshToken = response["refresh_token"]
        if "access_token" in response:
            token = response["access_token"]
            self.Setting.Url.Provider.Scope.User.AccessToken = token
        if "expires_in" in response:
            self.Setting.Url.Provider.Scope.User.ExpiresIn = response["expires_in"]
        if token:
            self.Setting.Url.Provider.Scope.User.commit()
        return token


g_ImplementationHelper.addImplementation(PyOAuth2Service,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services
