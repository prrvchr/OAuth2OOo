#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.embed import XTransactedObject
from com.sun.star.util import XUpdatable

from .unolib import PropertySet
from .unotools import getProperty
from .unotools import getConfiguration
from .logger import getLogger
from .oauth2tools import g_identifier


class WizardConfiguration(unohelper.Base,
                          XTransactedObject,
                          PropertySet):
    def __init__(self, ctx):
        self.ctx = ctx
        self.configuration = getConfiguration(self.ctx, g_identifier, True)
        self.Url = UrlWriter(self.configuration)
        self.HandlerTimeout = self.configuration.getByName("HandlerTimeout")
        self.RequestTimeout = self.configuration.getByName("RequestTimeout")
        self.Logger = getLogger(self.ctx)

    @property
    def UrlList(self):
        names = []
        for key, value in self.Url.Urls.items():
            if value["State"] < 8:
                names.append(key)
        return tuple(names)

    # XTransactedObject
    def commit(self):
        self.Url.commit()
        self.Url.Provider.commit()
        self.Url.Provider.Scope.commit()
    def revert(self):
        pass

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        properties["Url"] = getProperty("Url", "com.sun.star.uno.XInterface", readonly)
        properties["UrlList"] = getProperty("UrlList", "[]string", readonly)
        properties["HandlerTimeout"] = getProperty("HandlerTimeout", "short", readonly)
        properties["RequestTimeout"] = getProperty("RequestTimeout", "short", readonly)
        properties["Logger"] = getProperty("Logger", "com.sun.star.logging.XLogger", readonly)
        return properties


class UrlWriter(unohelper.Base,
                XTransactedObject,
                PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.Provider = ProviderWriter(self.configuration)
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
                                           "CodeChallengeMethod": "S256",
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

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Id"] = getProperty("Id", "string", transient)
        properties["Provider"] = getProperty("Provider", "com.sun.star.uno.XInterface", readonly)
        properties["ProviderName"] = getProperty("ProviderName", "string", transient)
        properties["ProviderList"] = getProperty("ProviderList", "[]string", readonly)
        properties["ScopeName"] = getProperty("ScopeName", "string", transient)
        properties["ScopeList"] = getProperty("ScopeList", "[]string", readonly)
        properties["ScopesList"] = getProperty("ScopesList", "[]string", readonly)
        properties["State"] = getProperty("State", "short", transient)
        return properties


class ProviderWriter(unohelper.Base,
                     XTransactedObject,
                     PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.redirect = "urn:ietf:wg:oauth:2.0:oob"
        self.Providers = {}
        self.Scope = ScopeWriter(self.configuration)
        self.revert()

    @property
    def Id(self):
        return self.Scope.User.ProviderId
    @Id.setter
    def Id(self, id):
        self.Scope.User.ProviderId = id
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
    def AuthorizationParameters(self):
        parameters = '{}'
        if self.Id in self.Providers:
            parameters = self.Providers[self.Id]["AuthorizationParameters"]
        return parameters
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
    def TokenParameters(self):
        parameters = '{}'
        if self.Id in self.Providers:
            parameters = self.Providers[self.Id]["TokenParameters"]
        return parameters
    @property
    def CodeChallenge(self):
        enabled = True
        if self.Id in self.Providers:
            enabled = self.Providers[self.Id]["CodeChallenge"]
        return enabled
    @CodeChallenge.setter
    def CodeChallenge(self, enabled):
        if self.Id in self.Providers:
            self.Providers[self.Id]["CodeChallenge"] = enabled
    @property
    def CodeChallengeMethod(self):
        method = "S256"
        if self.Id in self.Providers:
            method = self.Providers[self.Id]["CodeChallengeMethod"]
        return method
    @CodeChallengeMethod.setter
    def CodeChallengeMethod(self, method):
        if self.Id in self.Providers:
            self.Providers[self.Id]["CodeChallengeMethod"] = method
    @property
    def HttpHandler(self):
        enabled = True
        if self.Id in self.Providers:
            enabled = self.Providers[self.Id]["HttpHandler"]
        return enabled
    @HttpHandler.setter
    def HttpHandler(self, enabled):
        if self.Id in self.Providers and self.Providers[self.Id]["HttpHandler"] != enabled:
            self.Providers[self.Id]["HttpHandler"] = enabled
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
                provider.replaceByName("CodeChallengeMethod", value["CodeChallengeMethod"])
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
                                  "AuthorizationParameters": provider.getByName("AuthorizationParameters"),
                                  "TokenUrl": provider.getByName("TokenUrl"),
                                  "TokenParameters": provider.getByName("TokenParameters"),
                                  "CodeChallenge": provider.getByName("CodeChallenge"),
                                  "CodeChallengeMethod": provider.getByName("CodeChallengeMethod"),
                                  "HttpHandler": provider.getByName("HttpHandler"),
                                  "RedirectAddress": provider.getByName("RedirectAddress"),
                                  "RedirectPort": provider.getByName("RedirectPort"),
                                  "State": 1}

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Scope"] = getProperty("Scope", "com.sun.star.uno.XInterface", readonly)
        properties["ClientId"] = getProperty("ClientId", "string", transient)
        properties["ClientSecret"] = getProperty("ClientSecret", "string", transient)
        properties["AuthorizationUrl"] = getProperty("AuthorizationUrl", "string", transient)
        properties["AuthorizationParameters"] = getProperty("AuthorizationParameters", "string", transient)
        properties["TokenUrl"] = getProperty("TokenUrl", "string", transient)
        properties["TokenParameters"] = getProperty("TokenParameters", "string", transient)
        properties["CodeChallenge"] = getProperty("CodeChallenge", "boolean", transient)
        properties["CodeChallengeMethod"] = getProperty("CodeChallengeMethod", "string", transient)
        properties["HttpHandler"] = getProperty("HttpHandler", "boolean", transient)
        properties["RedirectAddress"] = getProperty("RedirectAddress", "string", transient)
        properties["RedirectPort"] = getProperty("RedirectPort", "short", transient)
        properties["RedirectUri"] = getProperty("RedirectUri", "string", readonly)
        properties["State"] = getProperty("State", "short", transient)
        return properties


class ScopeWriter(unohelper.Base,
                  XTransactedObject,
                  PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.Id = ""
        self.Scopes = {}
        self.User = UserWriter(self.configuration)
        self.revert()

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

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Id"] = getProperty("Id", "string", transient)
        properties["User"] = getProperty("User", "com.sun.star.uno.XInterface", readonly)
        properties["Value"] = getProperty("Value", "string", readonly)
        properties["Values"] = getProperty("Values", "[]string", transient)
        properties["State"] = getProperty("State", "short", transient)
        return properties


class UserWriter(unohelper.Base,
                 XUpdatable,
                 PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.Id = ""
        self.ProviderId = ""
        self._Scope = []

    @property
    def Scope(self):
        return " ".join(self._Scope)

    # XUpdatable
    def update(self):
        scope = []
        providers = self.configuration.getByName("Providers")
        if providers.hasByName(self.ProviderId):
            provider = providers.getByName(self.ProviderId)
            users = provider.getByName("Users")
            if users.hasByName(self.Id):
                user = users.getByName(self.Id)
                scope = list(user.getByName("Scopes"))
        self._Scope = scope

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Id"] = getProperty("Id", "string", transient)
        properties["Scope"] = getProperty("Scope", "string", readonly)
        return properties
