#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.embed import XTransactedObject
from com.sun.star.util import XUpdatable

import oauth2
from oauth2 import PyPropertySet
import time
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.SettingReader"


class PySettingReader(unohelper.Base, XServiceInfo, PyPropertySet, XTransactedObject, XUpdatable):
    def __init__(self, ctx):
        self.ctx = ctx
        self.properties = {}
        maybevoid = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.MAYBEVOID")
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Url"] = oauth2.getProperty("Url", "com.sun.star.uno.XInterface", readonly)
        self.properties["UrlList"] = oauth2.getProperty("UrlList", "[]string", readonly)
        self.properties["RequestTimeout"] = oauth2.getProperty("RequestTimeout", "short", transient)
        self.properties["HandlerTimeout"] = oauth2.getProperty("HandlerTimeout", "short", transient)
        self.properties["Logger"] = oauth2.getProperty("Logger", "com.sun.star.logging.XLogger", readonly)
        self.configuration = oauth2.getConfiguration(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo", True)
        self.RequestTimeout = self.configuration.getByName("RequestTimeout")
        self.HandlerTimeout = self.configuration.getByName("HandlerTimeout")
        self.Logger = oauth2.getLogger(self.ctx)
        self.Url = PyUrlReader(self.configuration)

    @property
    def UrlList(self):
        return self.configuration.getByName("Urls").ElementNames

    # XTransactedObject
    def commit(self):
        self.configuration.replaceByName("RequestTimeout", self.RequestTimeout)
        self.configuration.replaceByName("HandlerTimeout", self.HandlerTimeout)
        if self.configuration.hasPendingChanges():
            self.configuration.commitChanges()
    def revert(self):
        self.RequestTimeout = self.configuration.getByName("RequestTimeout")
        self.HandlerTimeout = self.configuration.getByName("HandlerTimeout")

    # XUpdatable
    def update(self):
        pass

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


class PyUrlReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = oauth2.getProperty("Id", "string", transient)
        self.properties["Provider"] = oauth2.getProperty("Provider", "com.sun.star.uno.XInterface", readonly)
        self.Id = ""
        self.Provider = PyProviderReader(self.configuration)

    # XUpdatable
    def update(self):
        id = ""
        urls = self.configuration.getByName("Urls")
        if urls.hasByName(self.Id):
            id = urls.getByName(self.Id).getByName("Scope")
        self.Provider.Scope.Id = id
        self.Provider.Scope.update()
        self.Provider.update()


class PyProviderReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        self.properties["ClientId"] = oauth2.getProperty("ClientId", "string", readonly)
        self.properties["ClientSecret"] = oauth2.getProperty("ClientSecret", "string", readonly)
        self.properties["AuthorizationUrl"] = oauth2.getProperty("AuthorizationUrl", "string", readonly)
        self.properties["TokenUrl"] = oauth2.getProperty("TokenUrl", "string", readonly)
        self.properties["CodeChallenge"] = oauth2.getProperty("CodeChallenge", "boolean", readonly)
        self.properties["HttpHandler"] = oauth2.getProperty("HttpHandler", "boolean", readonly)
        self.properties["RedirectAddress"] = oauth2.getProperty("RedirectAddress", "string", readonly)
        self.properties["RedirectPort"] = oauth2.getProperty("RedirectPort", "short", readonly)
        self.properties["RedirectUri"] = oauth2.getProperty("RedirectUri", "string", readonly)
        self.properties["Scope"] = oauth2.getProperty("Scope", "com.sun.star.uno.XInterface", readonly)
        self.ClientId = ""
        self.ClientSecret = ""
        self.AuthorizationUrl = ""
        self.TokenUrl = ""
        self.CodeChallenge = True
        self.HttpHandler = True
        self.RedirectAddress = "localhost"
        self.RedirectPort = 8080
        self.redirect = "urn:ietf:wg:oauth:2.0:oob"
        self.Scope = PyScopeReader(self.configuration)

    @property
    def RedirectUri(self):
        if self.HttpHandler:
            uri = "http://%s:%s/" % (self.RedirectAddress, self.RedirectPort)
        else:
            uri = self.redirect
        return uri

    # XUpdatable
    def update(self):
        clientid = ""
        clientsecret = ""
        authorizationurl = ""
        tokenurl = ""
        codechallenge = True
        httphandler = True
        redirectaddress = "localhost"
        redirectport = 8080
        providers = self.configuration.getByName("Providers")
        if providers.hasByName(self.Scope.User.ProviderId):
            provider = providers.getByName(self.Scope.User.ProviderId)
            clientid = provider.getByName("ClientId")
            clientsecret = provider.getByName("ClientSecret")
            authorizationurl = provider.getByName("AuthorizationUrl")
            tokenurl = provider.getByName("TokenUrl")
            codechallenge = provider.getByName("CodeChallenge")
            httphandler = provider.getByName("HttpHandler")
            redirectaddress = provider.getByName("RedirectAddress")
            redirectport = provider.getByName("RedirectPort")
        self.ClientId = clientid
        self.ClientSecret = clientsecret
        self.AuthorizationUrl = authorizationurl
        self.TokenUrl = tokenurl
        self.CodeChallenge = codechallenge
        self.HttpHandler = httphandler
        self.RedirectAddress = redirectaddress
        self.RedirectPort = redirectport
        self.Scope.User.update()


class PyScopeReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        self.properties["Values"] = oauth2.getProperty("Values", "string", readonly)
        self.properties["Authorized"] = oauth2.getProperty("Authorized", "boolean", readonly)
        self.properties["User"] = oauth2.getProperty("User", "com.sun.star.uno.XInterface", readonly)
        self.Id = ""
        self._Values = []
        self.User = PyUserReader(self.configuration)

    @property
    def Values(self):
        values = self.User._Scope
        for value in self._Values:
            if value not in values:
                values.append(value)
        return " ".join(values)
    @property
    def Authorized(self):
        authorized = True
        for value in self._Values:
            if value not in self.User._Scope:
                authorized = False
                break
        return authorized

    # XUpdatable
    def update(self):
        id = ""
        values = []
        scopes = self.configuration.getByName("Scopes")
        if scopes.hasByName(self.Id):
            scope = scopes.getByName(self.Id)
            id = scope.getByName("Provider")
            values = list(scope.getByName("Values"))
        self._Values = values
        self.User.ProviderId = id


class PyUserReader(unohelper.Base, PyPropertySet, XTransactedObject, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = oauth2.getProperty("Id", "string", transient)
        self.properties["AccessToken"] = oauth2.getProperty("AccessToken", "string", transient)
        self.properties["RefreshToken"] = oauth2.getProperty("RefreshToken", "string", transient)
        self.properties["ExpiresIn"] = oauth2.getProperty("ExpiresIn", "short", transient)
        self.properties["Scope"] = oauth2.getProperty("Scope", "string", transient)
        self.Id = ""
        self.ProviderId = ""
        self.AccessToken = ""
        self.RefreshToken = ""
        self._TimeStamp = 0
        self._Scope = []

    @property
    def ExpiresIn(self):
        second = self._TimeStamp - int(time.time())
        return second if second > 0 else 0
    @ExpiresIn.setter
    def ExpiresIn(self, second):
        self._TimeStamp = int(time.time()) + second
    @property
    def Scope(self):
        return " ".join(self._Scope)
    @Scope.setter
    def Scope(self, scope):
        self._Scope = scope.split(" ")

    # XTransactedObject
    def commit(self):
        providers = self.configuration.getByName("Providers")
        if providers.hasByName(self.ProviderId):
            provider = providers.getByName(self.ProviderId)
            users = provider.getByName("Users")
            if not users.hasByName(self.Id):
                users.insertByName(self.Id, users.createInstance())
            user = users.getByName(self.Id)
            user.replaceByName("AccessToken", self.AccessToken)
            user.replaceByName("RefreshToken", self.RefreshToken)
            user.replaceByName("TimeStamp", self._TimeStamp)
#            user.replaceByName("Scopes", self._Scope)
            arguments = ("Scopes", uno.Any("[]string", tuple(self._Scope)))
            uno.invoke(user, "replaceByName", arguments)
            if self.configuration.hasPendingChanges():
                self.configuration.commitChanges()
    def revert(self):
        self.AccessToken = ""
        self.RefreshToken = ""
        self._TimeStamp = 0
        self._Scope = []

    # XUpdatable
    def update(self):
        accesstoken = ""
        refreshtoken = ""
        timestamp = 0
        scope = []
        providers = self.configuration.getByName("Providers")
        if providers.hasByName(self.ProviderId):
            provider = providers.getByName(self.ProviderId)
            users = provider.getByName("Users")
            if users.hasByName(self.Id):
                user = users.getByName(self.Id)
                accesstoken = user.getByName("AccessToken")
                refreshtoken = user.getByName("RefreshToken")
                timestamp = user.getByName("TimeStamp")
                scope = list(user.getByName("Scopes"))
        self.AccessToken = accesstoken
        self.RefreshToken = refreshtoken
        self._TimeStamp = timestamp
        self._Scope = scope


g_ImplementationHelper.addImplementation(PySettingReader,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
