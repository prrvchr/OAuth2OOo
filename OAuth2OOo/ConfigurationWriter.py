#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.embed import XTransactedObject
from com.sun.star.util import XUpdatable

import unotools
from unotools import PyServiceInfo, PyPropertySet

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.ConfigurationWriter"


class PyConfigurationWriter(unohelper.Base, PyServiceInfo, PyPropertySet, XTransactedObject):
    def __init__(self, ctx):
        self.ctx = ctx
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        self.properties["Url"] = unotools.getProperty("Url", "com.sun.star.uno.XInterface", readonly)
        self.properties["UrlList"] = unotools.getProperty("UrlList", "[]string", readonly)
        self.properties["HandlerTimeout"] = unotools.getProperty("HandlerTimeout", "short", readonly)
        self.configuration = unotools.getConfiguration(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo", True)
        self._Url = PyUrlWriter(self.configuration)
        self._HandlerTimeout = None

    @property
    def Url(self):
        return self._Url
    @property
    def UrlList(self):
        names = []
        for key, value in self.Url.Urls.items():
            if value["State"] < 8:
                names.append(key)
        return tuple(names)
    @property
    def HandlerTimeout(self):
        if self._HandlerTimeout is None:
            self._HandlerTimeout = self.configuration.getByName("HandlerTimeout")
        return self._HandlerTimeout

    # XTransactedObject
    def commit(self):
        self.Url.commit()
        self.Url.Provider.commit()
        self.Url.Provider.Scope.commit()
    def revert(self):
        pass


class PyUrlWriter(unohelper.Base, PyPropertySet, XTransactedObject):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = unotools.getProperty("Id", "string", transient)
        self.properties["Provider"] = unotools.getProperty("Provider", "com.sun.star.uno.XInterface", readonly)
        self.properties["ProviderName"] = unotools.getProperty("ProviderName", "string", transient)
        self.properties["ProviderList"] = unotools.getProperty("ProviderList", "[]string", readonly)
        self.properties["ScopeName"] = unotools.getProperty("ScopeName", "string", transient)
        self.properties["ScopeList"] = unotools.getProperty("ScopeList", "[]string", readonly)
        self.properties["ScopesList"] = unotools.getProperty("ScopesList", "[]string", readonly)
        self.properties["State"] = unotools.getProperty("State", "short", transient)
        self._Provider = PyProviderWriter(self.configuration)
        self._Id = ""
        self.Urls = {}
        self.revert()

    @property
    def Id(self):
        return self._Id
    @Id.setter
    def Id(self, id):
        self._Id = id
        if id and id not in self.Urls:
            self.Urls[id] = {"Scope": "", "State": 2}
        scope = ""
        if id in self.Urls:
            scope = self.Urls[id]["Scope"]
            if self.Urls[id]["State"] > 7:
                self.Urls[id]["State"] = 2
        self.Provider.Scope.Id = scope
        provider = ""
        if scope in self.Provider.Scope.Scopes:
            provider = self.Provider.Scope.Scopes[scope]["Provider"]
        self.Provider.Id = provider
    @property
    def Provider(self):
        return self._Provider
    @property
    def ProviderName(self):
        return self.Provider.Id
    @ProviderName.setter
    def ProviderName(self, id):
        self.Provider.Id = id
        if id and id not in self.Provider.Providers:
            self.Provider.Providers[id] = {"ClientId": "",
                                           "ClientSecret": "",
                                           "AuthorizationUrl": "",
                                           "TokenUrl": "",
                                           "CodeChallenge": True,
                                           "HttpHandler": True,
                                           "RedirectAddress": "localhost",
                                           "RedirectPort": 8080,
                                           "State": 2}
        elif id in self.Provider.Providers:
            if self.Provider.Providers[id]["State"] > 7:
                self.Provider.Providers[id]["State"] = 2
    @property
    def ProviderList(self):
        names = []
        for key, value in self.Provider.Providers.items():
            if value["State"] < 8:
                names.append(key)
        return tuple(names)
    @property
    def ScopeName(self):
        return self.Provider.Scope.Id
    @ScopeName.setter
    def ScopeName(self, id):
        self.Provider.Scope.Id = id
        if id and id not in self.Provider.Scope.Scopes:
            self.Provider.Scope.Scopes[id] = {"Provider": self.Provider.Id,
                                              "Values": [],
                                              "State": 2}
        elif id in self.Provider.Scope.Scopes:
            if self.Provider.Scope.Scopes[id]["State"] > 7:
                self.Provider.Scope.Scopes[id]["State"] = 2
        if id and self.Id in self.Urls:
            self.Urls[self.Id]["Scope"] = id
            self.State = 4
    @property
    def ScopeList(self):
        names = []
        for key, value in self.Provider.Scope.Scopes.items():
            if value["State"] < 8 and value["Provider"] == self.Provider.Id:
                names.append(key)
        return tuple(names)
    @property
    def ScopesList(self):
        names = []
        for key, value in self.Provider.Scope.Scopes.items():
            if value["State"] < 8:
                names.append(key)
        return tuple(names)
    @property
    def State(self):
        state = 2
        if self.Id in self.Urls:
            state = self.Urls[self.Id]["State"]
        return state
    @State.setter
    def State(self, state):
        if self.Id in self.Urls:
            self.Urls[self.Id]["State"] = state

    # XTransactedObject
    def commit(self):
        urls = self.configuration.getByName("Urls")
        for key, value in self.Urls.items():
            if value["State"] < 4:
                continue
            elif value["State"] < 8:
                if not urls.hasByName(key):
                    urls.insertByName(key, urls.createInstance())
                url = urls.getByName(key)
                url.replaceByName("Scope", value["Scope"])
            elif urls.hasByName(key):
                    urls.removeByName(key)
        if self.configuration.hasPendingChanges():
            self.configuration.commitChanges()
    def revert(self):
        self.Urls = {}
        urls = self.configuration.getByName("Urls")
        for id in urls.ElementNames:
            url = urls.getByName(id)
            self.Urls[id] = {"Scope": url.getByName("Scope"),
                             "State": 1}


class PyProviderWriter(unohelper.Base, PyPropertySet, XTransactedObject):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Scope"] = unotools.getProperty("Scope", "com.sun.star.uno.XInterface", readonly)
        self.properties["ClientId"] = unotools.getProperty("ClientId", "string", transient)
        self.properties["ClientSecret"] = unotools.getProperty("ClientSecret", "string", transient)
        self.properties["AuthorizationUrl"] = unotools.getProperty("AuthorizationUrl", "string", transient)
        self.properties["TokenUrl"] = unotools.getProperty("TokenUrl", "string", transient)
        self.properties["CodeChallenge"] = unotools.getProperty("CodeChallenge", "boolean", transient)
        self.properties["HttpHandler"] = unotools.getProperty("HttpHandler", "boolean", transient)
        self.properties["RedirectAddress"] = unotools.getProperty("RedirectAddress", "string", transient)
        self.properties["RedirectPort"] = unotools.getProperty("RedirectPort", "short", transient)
        self.properties["RedirectUri"] = unotools.getProperty("RedirectUri", "string", readonly)
        self.properties["State"] = unotools.getProperty("State", "short", transient)
        self.redirect = "urn:ietf:wg:oauth:2.0:oob"
        self.Providers = {}
        self._Scope = PyScopeWriter(self.configuration)
        self.revert()

    @property
    def Id(self):
        return self.Scope.User.ProviderId
    @Id.setter
    def Id(self, id):
        self.Scope.User.ProviderId = id
    @property
    def Scope(self):
        return self._Scope
    @property
    def ClientId(self):
        id = ""
        if self.Id in self.Providers:
            id = self.Providers[self.Id]["ClientId"]
        return id
    @ClientId.setter
    def ClientId(self, id):
        if self.Id in self.Providers:
            self.Providers[self.Id]["ClientId"] = id
    @property
    def ClientSecret(self):
        secret = ""
        if self.Id in self.Providers:
            secret = self.Providers[self.Id]["ClientSecret"]
        return secret
    @ClientSecret.setter
    def ClientSecret(self, secret):
        if self.Id in self.Providers:
            self.Providers[self.Id]["ClientSecret"] = secret
    @property
    def AuthorizationUrl(self):
        url = ""
        if self.Id in self.Providers:
            url = self.Providers[self.Id]["AuthorizationUrl"]
        return url
    @AuthorizationUrl.setter
    def AuthorizationUrl(self, url):
        if self.Id in self.Providers:
            self.Providers[self.Id]["AuthorizationUrl"] = url
    @property
    def TokenUrl(self):
        url = ""
        if self.Id in self.Providers:
            url = self.Providers[self.Id]["TokenUrl"]
        return url
    @TokenUrl.setter
    def TokenUrl(self, url):
        if self.Id in self.Providers:
            self.Providers[self.Id]["TokenUrl"] = url
    @property
    def CodeChallenge(self):
        enable = True
        if self.Id in self.Providers:
            enable = self.Providers[self.Id]["CodeChallenge"]
        return enable
    @CodeChallenge.setter
    def CodeChallenge(self, enable):
        if self.Id in self.Providers:
            self.Providers[self.Id]["CodeChallenge"] = enable
    @property
    def HttpHandler(self):
        enable = True
        if self.Id in self.Providers:
            enable = self.Providers[self.Id]["HttpHandler"]
        return enable
    @HttpHandler.setter
    def HttpHandler(self, enable):
        if self.Id in self.Providers and self.Providers[self.Id]["HttpHandler"] != enable:
            self.Providers[self.Id]["HttpHandler"] = enable
            self.State = 4
    @property
    def RedirectAddress(self):
        address = "localhost"
        if self.Id in self.Providers:
            address =  self.Providers[self.Id]["RedirectAddress"]
        return address
    @RedirectAddress.setter
    def RedirectAddress(self, address):
        if self.Id in self.Providers and self.Providers[self.Id]["RedirectAddress"] != address:
            self.Providers[self.Id]["RedirectAddress"] = address
            self.State = 4
    @property
    def RedirectPort(self):
        port = 8080
        if self.Id in self.Providers:
            port = self.Providers[self.Id]["RedirectPort"]
        return port
    @RedirectPort.setter
    def RedirectPort(self, port):
        if self.Id in self.Providers and self.Providers[self.Id]["RedirectPort"] != port:
            self.Providers[self.Id]["RedirectPort"] = port
            self.State = 4
    @property
    def RedirectUri(self):
        if self.HttpHandler:
            uri = "http://%s:%s/" % (self.RedirectAddress, self.RedirectPort)
        else:
            uri = self.redirect
        return uri
    @property
    def State(self):
        state = 2
        if self.Id in self.Providers:
            state = self.Providers[self.Id]["State"]
        return state
    @State.setter
    def State(self, state):
        if self.Id in self.Providers:
            self.Providers[self.Id]["State"] = state
            if state == 8:
                for scope in self.Scope.Scopes.values():
                    if scope["Provider"] == self.Id:
                        scope["State"] = 8

    # XTransactedObject
    def commit(self):
        providers = self.configuration.getByName("Providers")
        for key, value in self.Providers.items():
            if value["State"] < 4:
                continue
            elif value["State"] < 8:
                if not providers.hasByName(key):
                    providers.insertByName(key, providers.createInstance())
                provider = providers.getByName(key)
                provider.replaceByName("ClientId", value["ClientId"])
                provider.replaceByName("ClientSecret", value["ClientSecret"])
                provider.replaceByName("AuthorizationUrl", value["AuthorizationUrl"])
                provider.replaceByName("TokenUrl", value["TokenUrl"])
                provider.replaceByName("CodeChallenge", value["CodeChallenge"])
                provider.replaceByName("HttpHandler", value["HttpHandler"])
                provider.replaceByName("RedirectAddress", value["RedirectAddress"])
                provider.replaceByName("RedirectPort", value["RedirectPort"])
            elif providers.hasByName(key):
                providers.removeByName(key)
        if self.configuration.hasPendingChanges():
            self.configuration.commitChanges()
    def revert(self):
        self.Providers = {}
        providers = self.configuration.getByName("Providers")
        for id in providers.ElementNames:
            provider = providers.getByName(id)
            self.Providers[id] = {"ClientId": provider.getByName("ClientId"),
                                  "ClientSecret": provider.getByName("ClientSecret"),
                                  "AuthorizationUrl": provider.getByName("AuthorizationUrl"),
                                  "TokenUrl": provider.getByName("TokenUrl"),
                                  "CodeChallenge": provider.getByName("CodeChallenge"),
                                  "HttpHandler": provider.getByName("HttpHandler"),
                                  "RedirectAddress": provider.getByName("RedirectAddress"),
                                  "RedirectPort": provider.getByName("RedirectPort"),
                                  "State": 1}


class PyScopeWriter(unohelper.Base, PyPropertySet, XTransactedObject):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = unotools.getProperty("Id", "string", transient)
        self.properties["User"] = unotools.getProperty("User", "com.sun.star.uno.XInterface", readonly)
        self.properties["Value"] = unotools.getProperty("Value", "string", readonly)
        self.properties["Values"] = unotools.getProperty("Values", "[]string", transient)
        self.properties["State"] = unotools.getProperty("State", "short", transient)
        self.Id = ""
        self.Scopes = {}
        self._User = PyUserWriter(self.configuration)
        self.revert()

    @property
    def User(self):
        return self._User
    @property
    def Value(self):
        values = self.User._Scope
        if self.Id in self.Scopes:
            for value in self.Scopes[self.Id]["Values"]:
                if value not in values:
                    values.append(value)
        return " ".join(values)
    @property
    def Values(self):
        values = []
        if self.Id in self.Scopes:
            values = self.Scopes[self.Id]["Values"]
        return tuple(values)
    @Values.setter
    def Values(self, values):
        if self.Id in self.Scopes:
            self.Scopes[self.Id]["Values"] = values
    @property
    def State(self):
        state = 2
        if self.Id in self.Scopes:
            state = self.Scopes[self.Id]["State"]
        return state
    @State.setter
    def State(self, state):
        if self.Id in self.Scopes:
            self.Scopes[self.Id]["State"] = state

    # XTransactedObject
    def commit(self):
        scopes = self.configuration.getByName("Scopes")
        for key, value in self.Scopes.items():
            if value["State"] < 4:
                continue
            elif value["State"] < 8:
                if not scopes.hasByName(key):
                    scopes.insertByName(key, scopes.createInstance())
                    scopes.getByName(key).replaceByName("Provider", value["Provider"])
                scope = scopes.getByName(key)
#               scope.replaceByName("Value", value["Values"])
                arguments = ("Values", uno.Any("[]string", value["Values"]))
                uno.invoke(scope, "replaceByName", arguments)
            elif scopes.hasByName(key):
                scopes.removeByName(key)
        if self.configuration.hasPendingChanges():
            self.configuration.commitChanges()
    def revert(self):
        self.Scopes = {}
        scopes = self.configuration.getByName("Scopes")
        for id in scopes.ElementNames:
            scope = scopes.getByName(id)
            self.Scopes[id] = {"Provider": scope.getByName("Provider"),
                               "Values": scope.getByName("Values"),
                               "State": 1}


class PyUserWriter(unohelper.Base, PyPropertySet, XUpdatable):
    def __init__(self, configuration):
        self.configuration = configuration
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        self.properties["Id"] = unotools.getProperty("Id", "string", transient)
        self.properties["Scope"] = unotools.getProperty("Scope", "string", readonly)
        self._Id = ""
        self.ProviderId = ""
        self._Scope = []

    @property
    def Id(self):
        return self._Id
    @Id.setter
    def Id(self, id):
        self._Id = id
        self.update()
    @property
    def Scope(self):
        return " ".join(self._Scope)

    # XUpdatable
    def update(self):
        self._Scope = []
        providers = self.configuration.getByName("Providers")
        if providers.hasByName(self.ProviderId):
            provider = providers.getByName(self.ProviderId)
            users = provider.getByName("Users")
            if users.hasByName(self._Id):
                user = users.getByName(self._Id)
                self._Scope = list(user.getByName("Scopes"))


g_ImplementationHelper.addImplementation(PyConfigurationWriter,                     # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
