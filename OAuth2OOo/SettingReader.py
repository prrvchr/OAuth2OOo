#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.embed import XTransactedObject
from com.sun.star.util import XUpdatable
from com.sun.star.uno import XReference

import unotools
from unotools import PyServiceInfo, PyPropertySet
import time
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.SettingReader"


class PySettingReader(unohelper.Base, PyServiceInfo, PyPropertySet, XTransactedObject, XUpdatable):
    def __init__(self, ctx):
        self.ctx = ctx
        self.properties = {}
        maybevoid = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.MAYBEVOID")
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Url"] = unotools.getProperty("Url", "com.sun.star.uno.XInterface", readonly)
        self.properties["UrlList"] = unotools.getProperty("UrlList", "[]string", readonly)
        self.properties["RequestTimeout"] = unotools.getProperty("RequestTimeout", "short", transient)
        self.properties["HandlerTimeout"] = unotools.getProperty("HandlerTimeout", "short", transient)
        self.properties["Logger"] = unotools.getProperty("Logger", "com.sun.star.logging.XLogger", readonly)
        self.configuration = unotools.getConfiguration(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo", True)
        self.RequestTimeout = self.configuration.getByName("RequestTimeout")
        self.HandlerTimeout = self.configuration.getByName("HandlerTimeout")
        self.Logger = unotools.getLogger(self.ctx)
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


class PyUrlReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = unotools.getProperty("Id", "string", transient)
        self.properties["Provider"] = unotools.getProperty("Provider", "com.sun.star.uno.XInterface", readonly)
        self.Id = ""
        self.Provider = PyProviderReader(self.configuration)

    # XUpdatable
    def update(self):
        id = ""
        urls = self.configuration.getByName("Urls")
        if urls.hasByName(self.Id):
            id = urls.getByName(self.Id).getByName("Scope")
        self.Provider.Scope.ScopeId = id
        self.Provider.Scope.update()
        self.Provider.update()


class PyProviderReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        self.properties["ClientId"] = unotools.getProperty("ClientId", "string", readonly)
        self.properties["ClientSecret"] = unotools.getProperty("ClientSecret", "string", readonly)
        self.properties["AuthorizationUrl"] = unotools.getProperty("AuthorizationUrl", "string", readonly)
        self.properties["TokenUrl"] = unotools.getProperty("TokenUrl", "string", readonly)
        self.properties["CodeChallenge"] = unotools.getProperty("CodeChallenge", "boolean", readonly)
        self.properties["HttpHandler"] = unotools.getProperty("HttpHandler", "boolean", readonly)
        self.properties["RedirectAddress"] = unotools.getProperty("RedirectAddress", "string", readonly)
        self.properties["RedirectPort"] = unotools.getProperty("RedirectPort", "short", readonly)
        self.properties["RedirectUri"] = unotools.getProperty("RedirectUri", "string", readonly)
        self.properties["Scope"] = unotools.getProperty("Scope", "com.sun.star.uno.XInterface", readonly)
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
        self.properties["Values"] = unotools.getProperty("Values", "string", readonly)
        self.properties["Authorized"] = unotools.getProperty("Authorized", "boolean", readonly)
        self.properties["User"] = unotools.getProperty("User", "com.sun.star.uno.XInterface", readonly)
        self.ScopeId = ""
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
        if scopes.hasByName(self.ScopeId):
            scope = scopes.getByName(self.ScopeId)
            id = scope.getByName("Provider")
            values = list(scope.getByName("Values"))
        self.User.ProviderId = id
        self._Values = values


class PyUserReader(unohelper.Base, PyPropertySet, XTransactedObject, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = unotools.getProperty("Id", "string", transient)
        self.properties["AccessToken"] = unotools.getProperty("AccessToken", "string", transient)
        self.properties["RefreshToken"] = unotools.getProperty("RefreshToken", "string", transient)
        self.properties["ExpiresIn"] = unotools.getProperty("ExpiresIn", "short", transient)
        self.properties["Scope"] = unotools.getProperty("Scope", "string", transient)
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
