#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.embed import XTransactedObject
from com.sun.star.util import XUpdatable

from .unolib import PropertySet
from .unotools import getProperty
from .unotools import getConfiguration
from .logger import getLogger
from .oauth2tools import g_identifier

import time
import traceback


class SettingReader(unohelper.Base,
                    XTransactedObject,
                    XUpdatable,
                    PropertySet):
    def __init__(self, ctx):
        self.ctx = ctx
        self.configuration = getConfiguration(self.ctx, g_identifier, True)
        self.RequestTimeout = self.configuration.getByName("RequestTimeout")
        self.HandlerTimeout = self.configuration.getByName("HandlerTimeout")
        self.Logger = getLogger(self.ctx)
        self.Url = UrlReader(self.configuration)

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


    def _getPropertySetInfo(self):
        properties = {}
        maybevoid = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.MAYBEVOID")
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Url"] = getProperty("Url", "com.sun.star.uno.XInterface", readonly)
        properties["UrlList"] = getProperty("UrlList", "[]string", readonly)
        properties["RequestTimeout"] = getProperty("RequestTimeout", "short", transient)
        properties["HandlerTimeout"] = getProperty("HandlerTimeout", "short", transient)
        properties["Logger"] = getProperty("Logger", "com.sun.star.logging.XLogger", readonly)
        return properties


class UrlReader(unohelper.Base,
                XUpdatable,
                PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.Id = ""
        self.Provider = ProviderReader(self.configuration)

    # XUpdatable
    def update(self):
        id = ""
        urls = self.configuration.getByName("Urls")
        if urls.hasByName(self.Id):
            id = urls.getByName(self.Id).getByName("Scope")
        self.Provider.Scope.Id = id
        self.Provider.Scope.update()
        self.Provider.update()

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Id"] = getProperty("Id", "string", transient)
        properties["Provider"] = getProperty("Provider", "com.sun.star.uno.XInterface", readonly)
        return properties


class ProviderReader(unohelper.Base,
                     XUpdatable,
                     PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.ClientId = ""
        self.ClientSecret = ""
        self.AuthorizationUrl = ""
        self.TokenUrl = ""
        self.CodeChallenge = True
        self.HttpHandler = True
        self.RedirectAddress = "localhost"
        self.RedirectPort = 8080
        self.redirect = "urn:ietf:wg:oauth:2.0:oob"
        self.Scope = ScopeReader(self.configuration)

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

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        properties["ClientId"] = getProperty("ClientId", "string", readonly)
        properties["ClientSecret"] = getProperty("ClientSecret", "string", readonly)
        properties["AuthorizationUrl"] = getProperty("AuthorizationUrl", "string", readonly)
        properties["TokenUrl"] = getProperty("TokenUrl", "string", readonly)
        properties["CodeChallenge"] = getProperty("CodeChallenge", "boolean", readonly)
        properties["HttpHandler"] = getProperty("HttpHandler", "boolean", readonly)
        properties["RedirectAddress"] = getProperty("RedirectAddress", "string", readonly)
        properties["RedirectPort"] = getProperty("RedirectPort", "short", readonly)
        properties["RedirectUri"] = getProperty("RedirectUri", "string", readonly)
        properties["Scope"] = getProperty("Scope", "com.sun.star.uno.XInterface", readonly)
        return properties


class ScopeReader(unohelper.Base,
                  XUpdatable,
                  PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
        self.Id = ""
        self._Values = []
        self.User = UserReader(self.configuration)

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

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        properties["Values"] = getProperty("Values", "string", readonly)
        properties["Authorized"] = getProperty("Authorized", "boolean", readonly)
        properties["User"] = getProperty("User", "com.sun.star.uno.XInterface", readonly)
        return properties


class UserReader(unohelper.Base,
                 XTransactedObject,
                 XUpdatable,
                 PropertySet):
    def __init__(self, configuration):
        self.configuration = configuration
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

    def _getPropertySetInfo(self):
        properties = {}
        transient = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.TRANSIENT")
        properties["Id"] = getProperty("Id", "string", transient)
        properties["AccessToken"] = getProperty("AccessToken", "string", transient)
        properties["RefreshToken"] = getProperty("RefreshToken", "string", transient)
        properties["ExpiresIn"] = getProperty("ExpiresIn", "short", transient)
        properties["Scope"] = getProperty("Scope", "string", transient)
        return properties
