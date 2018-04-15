#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.embed import XTransactedObject
from com.sun.star.util import XUpdatable

import unotools
from unotools import PyServiceInfo, PyPropertySet
import time

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.SettingReader"


class PySettingReader(unohelper.Base, PyServiceInfo, PyPropertySet, XTransactedObject, XUpdatable):
    def __init__(self, ctx):
        self.ctx = ctx
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Url"] =            uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "Url",
                                                                0,
                                                                uno.getTypeByName("com.sun.star.uno.XInterface"),
                                                                readonly)
        self.properties["UrlList"] =        uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "UrlList",
                                                                1,
                                                                uno.getTypeByName("[]string"),
                                                                readonly)
        self.properties["RequestTimeout"] = uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "RequestTimeout",
                                                                2,
                                                                uno.getTypeByName("short"),
                                                                transient)
        self.properties["HandlerTimeout"] = uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "HandlerTimeout",
                                                                3,
                                                                uno.getTypeByName("short"),
                                                                transient)
        self.configuration = unotools.getConfiguration(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo", True)
        self._RequestTimeout = None
        self._HandlerTimeout = None
        self._Url = PyUrlReader(self.configuration)

    @property
    def Url(self):
        return self._Url
    @property
    def UrlList(self):
        return self.configuration.getByName("Urls").ElementNames
    @property
    def RequestTimeout(self):
        if self._RequestTimeout is None:
            self._RequestTimeout = self.configuration.getByName("RequestTimeout")
        return self._RequestTimeout
    @RequestTimeout.setter
    def RequestTimeout(self, timeout):
        self._RequestTimeout = timeout
    @property
    def HandlerTimeout(self):
        if self._HandlerTimeout is None:
            self._HandlerTimeout = self.configuration.getByName("HandlerTimeout")
        return self._HandlerTimeout
    @HandlerTimeout.setter
    def HandlerTimeout(self, timeout):
        self._HandlerTimeout = timeout

    # XTransactedObject
    def commit(self):
        self.configuration.replaceByName("RequestTimeout", self._RequestTimeout)
        self.configuration.replaceByName("HandlerTimeout", self._HandlerTimeout)
        if self.configuration.hasPendingChanges():
            self.configuration.commitChanges()
    def revert(self):
        self._RequestTimeout = self.configuration.getByName("RequestTimeout")
        self._HandlerTimeout = self.configuration.getByName("HandlerTimeout")

    # XUpdatable
    def update(self):
        self.Url.update()
        self.Url.Provider.Scope.User.update()


class PyUrlReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] =         uno.createUnoStruct("com.sun.star.beans.Property",
                                                            "Id",
                                                            0,
                                                            uno.getTypeByName("string"),
                                                            transient)
        self.properties["Provider"] =   uno.createUnoStruct("com.sun.star.beans.Property",
                                                            "Provider",
                                                            1,
                                                            uno.getTypeByName("com.sun.star.uno.XInterface"),
                                                            readonly)
        self._Id = ""
        self._Provider = PyProviderReader(self.configuration)

    @property
    def Id(self):
        return self._Id
    @Id.setter
    def Id(self, id):
        self._Id = id
    @property
    def Provider(self):
        return self._Provider

    # XUpdatable
    def update(self):
        urls = self.configuration.getByName("Urls")
        if urls.hasByName(self.Id):
            url = urls.getByName(self.Id)
            self.Provider.Scope.User.ScopeId = url.getByName("Scope")
        self.Provider.Scope.update()
        self.Provider.update()


class PyProviderReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        self.properties["ClientId"] =           uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "ClientId",
                                                                    0,
                                                                    uno.getTypeByName("string"),
                                                                    readonly)
        self.properties["ClientSecret"] =       uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "ClientSecret",
                                                                    1,
                                                                    uno.getTypeByName("string"),
                                                                    readonly)
        self.properties["AuthorizationUrl"] =   uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "AuthorizationUrl",
                                                                    2,
                                                                    uno.getTypeByName("string"),
                                                                    readonly)
        self.properties["TokenUrl"] =           uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "TokenUrl",
                                                                    3,
                                                                    uno.getTypeByName("string"),
                                                                    readonly)
        self.properties["CodeChallenge"] =      uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "CodeChallenge",
                                                                    4,
                                                                    uno.getTypeByName("boolean"),
                                                                    readonly)
        self.properties["HttpHandler"] =        uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "HttpHandler",
                                                                    5,
                                                                    uno.getTypeByName("boolean"),
                                                                    readonly)
        self.properties["RedirectAddress"] =    uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "RedirectAddress",
                                                                    6,
                                                                    uno.getTypeByName("string"),
                                                                    readonly)
        self.properties["RedirectPort"] =       uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "RedirectPort",
                                                                    7,
                                                                    uno.getTypeByName("short"),
                                                                    readonly)
        self.properties["RedirectUri"] =        uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "RedirectUri",
                                                                    8,
                                                                    uno.getTypeByName("string"),
                                                                    readonly)
        self.properties["Scope"] =              uno.createUnoStruct("com.sun.star.beans.Property",
                                                                    "Scope",
                                                                    9,
                                                                    uno.getTypeByName("com.sun.star.uno.XInterface"),
                                                                    readonly)
        self._ClientId = ""
        self._ClientSecret = ""
        self._AuthorizationUrl = ""
        self._TokenUrl = ""
        self._CodeChallenge = True
        self._HttpHandler = True
        self._RedirectAddress = "localhost"
        self._RedirectPort = 8080
        self.redirect = "urn:ietf:wg:oauth:2.0:oob"
        self._Scope = PyScopeReader(self.configuration)

    @property
    def ClientId(self):
        return self._ClientId
    @property
    def ClientSecret(self):
        return self._ClientSecret
    @property
    def AuthorizationUrl(self):
        return self._AuthorizationUrl
    @property
    def TokenUrl(self):
        return self._TokenUrl
    @property
    def CodeChallenge(self):
        return self._CodeChallenge
    @property
    def HttpHandler(self):
        return self._HttpHandler
    @property
    def RedirectAddress(self):
        return self._RedirectAddress
    @property
    def RedirectPort(self):
        return self._RedirectPort
    @property
    def RedirectUri(self):
        if self.HttpHandler:
            uri = "http://%s:%s/" % (self.RedirectAddress, self.RedirectPort)
        else:
            uri = self.redirect
        return uri
    @property
    def Scope(self):
        return self._Scope

    # XUpdatable
    def update(self):
        providers = self.configuration.getByName("Providers")
        if providers.hasByName(self.Scope.ProviderId):
            provider = providers.getByName(self.Scope.ProviderId)
            self._ClientId = provider.getByName("ClientId")
            self._ClientSecret = provider.getByName("ClientSecret")
            self._AuthorizationUrl = provider.getByName("AuthorizationUrl")
            self._TokenUrl = provider.getByName("TokenUrl")
            self._CodeChallenge = provider.getByName("CodeChallenge")
            self._HttpHandler = provider.getByName("HttpHandler")
            self._RedirectAddress = provider.getByName("RedirectAddress")
            self._RedirectPort = provider.getByName("RedirectPort")
        else:
            self._ClientId = ""
            self._ClientSecret = ""
            self._AuthorizationUrl = ""
            self._TokenUrl = ""
            self._CodeChallenge = True
            self._HttpHandler = True
            self._RedirectAddress = "localhost"
            self._RedirectPort = 8080


class PyScopeReader(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Values"] =     uno.createUnoStruct("com.sun.star.beans.Property",
                                                            "Values",
                                                            0,
                                                            uno.getTypeByName("string"),
                                                            readonly)
        self.properties["User"] =       uno.createUnoStruct("com.sun.star.beans.Property",
                                                            "User",
                                                            1,
                                                            uno.getTypeByName("com.sun.star.uno.XInterface"),
                                                            readonly)
        self.ProviderId = ""
        self._Values = []
        self._User = PyUserReader(self.configuration)

    @property
    def Values(self):
        return " ".join(self._Values)
    @property
    def User(self):
        return self._User

    # XUpdatable
    def update(self):
        scopes = self.configuration.getByName("Scopes")
        if scopes.hasByName(self.User.ScopeId):
            scope = scopes.getByName(self.User.ScopeId)
            self._Values = scope.getByName("Values")
            self.ProviderId = scope.getByName("Provider")
        else:
            self._Values = []
            self.ProviderId = ""


class PyUserReader(unohelper.Base, PyPropertySet, XTransactedObject, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] =             uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "Id",
                                                                0,
                                                                uno.getTypeByName("string"),
                                                                transient)
        self.properties["AccessToken"] =    uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "AccessToken",
                                                                1,
                                                                uno.getTypeByName("string"),
                                                                transient)
        self.properties["RefreshToken"] =   uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "RefreshToken",
                                                                2,
                                                                uno.getTypeByName("string"),
                                                                transient)
        self.properties["ExpiresIn"] =      uno.createUnoStruct("com.sun.star.beans.Property",
                                                                "ExpiresIn",
                                                                3,
                                                                uno.getTypeByName("short"),
                                                                transient)
        self._Id = ""
        self.ScopeId = ""
        self._AccessToken = ""
        self._RefreshToken = ""
        self._TimeStamp = 0

    @property
    def Id(self):
        return self._Id
    @Id.setter
    def Id(self, id):
        self._Id = id
    @property
    def AccessToken(self):
        return self._AccessToken
    @AccessToken.setter
    def AccessToken(self, token):
        self._AccessToken = token
    @property
    def RefreshToken(self):
        return self._RefreshToken
    @RefreshToken.setter
    def RefreshToken(self, token):
        self._RefreshToken = token
    @property
    def ExpiresIn(self):
        second = self._TimeStamp - int(time.time())
        return second if second > 0 else 0
    @ExpiresIn.setter
    def ExpiresIn(self, second):
        self._TimeStamp = int(time.time()) + second

    # XTransactedObject
    def commit(self):
        scopes = self.configuration.getByName("Scopes")
        if scopes.hasByName(self.ScopeId):
            scope = scopes.getByName(self.ScopeId)
            users = scope.getByName("Users")
            if not users.hasByName(self.Id):
                users.insertByName(self.Id, users.createInstance())
            user = users.getByName(self.Id)
            user.replaceByName("AccessToken", self._AccessToken)
            user.replaceByName("RefreshToken", self._RefreshToken)
            user.replaceByName("TimeStamp", self._TimeStamp)
            if self.configuration.hasPendingChanges():
                self.configuration.commitChanges()
    def revert(self):
        self._AccessToken = ""
        self._RefreshToken = ""
        self._TimeStamp = 0

    # XUpdatable
    def update(self):
        user = None
        scopes = self.configuration.getByName("Scopes")
        if scopes.hasByName(self.ScopeId):
            scope = scopes.getByName(self.ScopeId)
            users = scope.getByName("Users")
            if users.hasByName(self.Id):
                user = users.getByName(self.Id)
        if user is not None:
            self._AccessToken = user.getByName("AccessToken")
            self._RefreshToken = user.getByName("RefreshToken")
            self._TimeStamp = user.getByName("TimeStamp")
        else:
            self.revert()


g_ImplementationHelper.addImplementation(PySettingReader,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
