#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-24 https://prrvchr.github.io                                  ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import uno

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.uno import Exception as UnoException

from ..model import TokenModel

from .httpserver import WatchDog
from .httpserver import Server

from ..oauth2 import CustomParser

from ..requestresponse import getRequestResponse

from ..oauth2 import getParserItems
from ..oauth2 import getResponseResults
from ..oauth2 import setParametersArguments
from ..oauth2 import setResquestParameter

from ..unotool import generateUuid
from ..unotool import getCurrentLocale
from ..unotool import getStringResource

from ..requestparameter import RequestParameter

from ..oauth2helper import isEmailValid
from ..oauth2helper import isUserAuthorized

from ..logger import getLogger

from ..configuration import g_extension
from ..configuration import g_identifier
from ..configuration import g_defaultlog
from ..configuration import g_basename

from six import string_types
import time
import validators
import base64
import hashlib
import json
import requests
import socket
from string import Template
from contextlib import closing
from threading import Condition
import traceback


class WizardModel(TokenModel):
    def __init__(self, ctx, close=False, readonly=False, url='', user=''):
        super(WizardModel, self).__init__(ctx, url, user)
        self._uuid = generateUuid()
        self._close = close
        self._readonly = readonly
        self._host = 'localhost'
        self._port = self._findFreePort()
        self._code = 'http://%s:%s' % (self._host, self._port)
        self._path = self._config.getByName('BaseUrl')
        self._locale = getCurrentLocale(ctx)
        self._language = self._config.getByName('Language')
        self._watchdog = None
        self._logger = getLogger(ctx, g_defaultlog, g_basename)
        self._resolver = getStringResource(ctx, g_identifier, 'dialogs', 'MessageBox')
        self._resources = {'Title':              'PageWizard%s.Title',
                           'Step':               'PageWizard%s.Step',
                           'UrlLabel':           'PageWizard1.Label4.Label',
                           'ProviderTitle':      'ProviderDialog.Title',
                           'ScopeTitle':         'ScopeDialog.Title',
                           'AuthorizationError': 'PageWizard3.Label2.Label',
                           'RequestMessage':     'PageWizard3.TextField1.Text.%s',
                           'TokenError':         'PageWizard3.Label9.Label',
                           'TokenLabel':         'PageWizard4.Label1.Label',
                           'TokenAccess':        'PageWizard4.Label6.Label',
                           'TokenRefresh':       'PageWizard4.Label4.Label',
                           'TokenExpires':       'PageWizard4.Label8.Label',
                           'DialogTitle':        'MessageBox.Title',
                           'DialogMessage':      'MessageBox.Message'}

    @property
    def HandlerTimeout(self):
        return self._config.getByName('HandlerTimeout')

    @property
    def User(self):
        return self._user

    @property
    def Url(self):
        return self._url
 
    def dispose(self):
        self._cancelServer()

    def _cancelServer(self):
        if self._watchdog is not None:
            if self._watchdog.is_alive():
                self._watchdog.cancel()
                self._watchdog.join()
            self._watchdog = None

# WizardModel getter methods called by WizardPages 1
    def getActivePath(self, user, url, provider, scope):
        urls = self._config.getByName('Urls')
        scopes = self._config.getByName('Scopes')
        providers = self._config.getByName('Providers')
        if urls.hasByName(url) and isUserAuthorized(scopes, providers, scope, provider, user):
            path = 1
        else:
            path = 0
        return path

    def getInitData(self):
        return self._user, self._url, self.UrlList, not self._readonly

    def getProviderData(self, resolver, name):
        providers = self._config.getByName('Providers')
        if providers.hasByName(name):
            data = self._getProviderData(providers.getByName(name))
        else:
            data = self._getDefaultProviderData()
        return self.getProviderTitle(resolver, name), data

    def saveProviderData(self, name, clientid, clientsecret, authorizationurl, tokenurl,
                         authorizationparameters, tokenparameters, challenge, challengemethod,
                         signin, page, handler, address, port):
        providers = self._config.getByName('Providers')
        if not providers.hasByName(name):
            providers.insertByName(name, providers.createInstance())
        provider = providers.getByName(name)
        provider.replaceByName('ClientId', clientid)
        provider.replaceByName('ClientSecret', clientsecret)
        provider.replaceByName('AuthorizationUrl', authorizationurl)
        provider.replaceByName('TokenUrl', tokenurl)
        provider.replaceByName('AuthorizationParameters', authorizationparameters)
        provider.replaceByName('TokenParameters', tokenparameters)
        provider.replaceByName('CodeChallenge', challenge)
        provider.replaceByName('CodeChallengeMethod', challengemethod)
        provider.replaceByName('SignIn', signin)
        provider.replaceByName('SignInPage', page)
        provider.replaceByName('HttpHandler', handler)
        provider.replaceByName('RedirectAddress', address)
        provider.replaceByName('RedirectPort', port)
        self.commit()

    def getScopeData(self, resolver, name):
        title = self.getScopeTitle(resolver, name)
        scopes = self._config.getByName('Scopes')
        if scopes.hasByName(name):
            values = scopes.getByName(name).getByName('Values')
        else:
            values = ()
        return title, values

    def saveScopeData(self, name, provider, values):
        scopes = self._config.getByName('Scopes')
        if not scopes.hasByName(name):
            scopes.insertByName(name, scopes.createInstance())
        scope = scopes.getByName(name)
        scope.replaceByName('Provider', provider)
        # scope.replaceByName('Values', values)
        arguments = ('Values', uno.Any('[]string', tuple(values)))
        uno.invoke(scope, 'replaceByName', arguments)
        self.commit()

    def getMessageBoxData(self):
        return self.getDialogMessage(), self.getDialogTitle()

    def _getProviderData(self, provider):
        clientid = provider.getByName('ClientId')
        clientsecret = provider.getByName('ClientSecret')
        authorizationurl = provider.getByName('AuthorizationUrl')
        tokenurl = provider.getByName('TokenUrl')
        authorizationparameters = provider.getByName('AuthorizationParameters')
        tokenparameters = provider.getByName('TokenParameters')
        codechallenge = provider.getByName('CodeChallenge')
        codechallengemethod = provider.getByName('CodeChallengeMethod')
        signin = provider.getByName('SignIn')
        page = provider.getByName('SignInPage')
        httphandler = provider.getByName('HttpHandler')
        redirectaddress = provider.getByName('RedirectAddress')
        redirectport = provider.getByName('RedirectPort')
        return (clientid, clientsecret, authorizationurl, tokenurl, authorizationparameters, tokenparameters,
                codechallenge, codechallengemethod, signin, page, httphandler, redirectaddress, redirectport)

    def _getDefaultProviderData(self):
        clientid = ''
        clientsecret = ''
        authorizationurl = ''
        tokenurl = ''
        authorizationparameters = '{"prompt": "consent", "response_mode": "query", "scope": null, "login_hint": "current_user", "hl": "current_language"}'
        tokenparameters = '{"scope": null}'
        codechallenge = True
        codechallengemethod = 'S256'
        signin = False
        page = ''
        httphandler = True
        redirectaddress = 'localhost'
        redirectport = 8080
        return (clientid, clientsecret, authorizationurl, tokenurl, authorizationparameters, tokenparameters,
                codechallenge, codechallengemethod, signin, page, httphandler, redirectaddress, redirectport)

    def getUrlData(self, url):
        scope = self._getScope(url)
        provider = self._getProvider(scope)
        return self._getProviderList(), provider, scope

    def addUrl(self, name, scope):
        urls = self._config.getByName('Urls')
        if not urls.hasByName(name):
            urls.insertByName(name, urls.createInstance())
        url = urls.getByName(name)
        url.replaceByName('Scope', scope)
        self.commit()

    def saveUrl(self, url, scope):
        urls = self._config.getByName('Urls')
        if urls.hasByName(url):
             urls.getByName(url).replaceByName('Scope', scope)
             self.commit()

    def removeUrl(self, url):
        urls = self._config.getByName('Urls')
        if urls.hasByName(url):
            urls.removeByName(url)
            self.commit()

    def canRemoveProvider(self, provider):
        scopes = self._config.getByName('Scopes')
        for scope in scopes.ElementNames:
            if scopes.getByName(scope).getByName('Provider') == provider:
                return False
        return True

    def canRemoveScope(self, scope):
        urls = self._config.getByName('Urls')
        for url in urls.ElementNames:
            if urls.getByName(url).getByName('Scope') == scope:
                return False
        return True

    def removeProvider(self, provider):
        providers = self._config.getByName('Providers')
        if providers.hasByName(provider):
            providers.removeByName(provider)
            self.commit()

    def removeScope(self, scope):
        scopes = self._config.getByName('Scopes')
        if scopes.hasByName(scope):
            scopes.removeByName(scope)
            self.commit()

    def isScopeChanged(self, url, scope):
        urls = self._config.getByName('Urls')
        if urls.hasByName(url):
            return urls.getByName(url).getByName('Scope') != scope
        return False

    def getScopeList(self, provider):
        items = []
        scopes = self._config.getByName('Scopes')
        for name in scopes.ElementNames:
            if scopes.getByName(name).getByName('Provider') == provider:
                items.append(name)
        return tuple(items)

    def isConfigurationValid(self, email, url, provider, scope):
        return isEmailValid(email) and url != '' and provider != '' and scope != ''

    def isValueValid(self, value):
        return value != ''

    def isTextValid(self, text):
        if validators.length(text, 1):
            return True
        return False

    def isUrlValid(self, url):
        if validators.url(url):
            return True
        return False

    def isJsonValid(self, parameters):
        try:
            json.loads(parameters)
        except ValueError as e:
            return False
        return True

    def isDialogValid(self, clientid, authorizationurl, tokenurl, authorizationparameters, tokenparameters, signin, page):
        return (self.isTextValid(clientid) and self.isUrlValid(authorizationurl) and self.isUrlValid(tokenurl)
                and self.isJsonValid(authorizationparameters) and self.isJsonValid(tokenparameters) and (not signin or self.isTextValid(page)))

    def _getScope(self, url):
        scope = ''
        urls = self._config.getByName('Urls')
        if urls.hasByName(url):
            scope = urls.getByName(url).getByName('Scope')
        return scope

    def _getProvider(self, scope):
        provider = ''
        scopes = self._config.getByName('Scopes')
        if scopes.hasByName(scope):
            provider = scopes.getByName(scope).getByName('Provider')
        return provider

    def _getScopeValues(self, scope):
        values = ()
        scopes = self._config.getByName('Scopes')
        if scopes.hasByName(scope):
            values = scopes.getByName(scope).getByName('Values')
        return values

    def _getProviderList(self):
        return self._config.getByName('Providers').ElementNames

# WizardModel getter methods called by WizardPages 2
    def getTermsOfUse(self):
        return '%sTermsOfUse%s' % (self._path, self._language)

    def getPrivacyPolicy(self):
        return '%sPrivacyPolicy%s' % (self._path, self._language)

    def getAuthorizationUrl(self):
        scopes, url, arguments = self._getAuthorizationData()
        return self._getUrlArguments(url, arguments)

    def _getAuthorizationData(self):
        scope = self._config.getByName('Scopes').getByName(self._scope)
        provider = self._config.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        url, arguments = self._getAuthorizationUrl(provider, scopes)
        signin = provider.getByName('SignIn')
        if signin:
            arguments = self._getSignInArguments(url, arguments)
            url = self._path + signin + self._language
        return scopes, url, arguments

    def _getAuthorizationUrl(self, provider, scopes):
        arguments = self._getAuthorizationArguments(provider, scopes)
        authorization = provider.getByName('Authorization')
        url = authorization.getByName('Url')
        args = json.loads(Template(authorization.getByName('Arguments')).safe_substitute(arguments))
        return url, args

    def _getAuthorizationArguments(self, provider, scopes):
        arguments = {'ClientId':    provider.getByName('ClientId'),
                     'RedirectUri': self._getRedirectUri(provider),
                     'State':       self._code,
                     'Scopes':      ' '.join(scopes),
                     'User':        self._user,
                     'Language':    self._locale.Language}
        clientsecret = provider.getByName('ClientSecret')
        if clientsecret:
            arguments['ClientSecret'] = clientsecret
        method = provider.getByName('CodeChallengeMethod')
        if method:
            arguments['CodeChallengeMethod'] = method
            arguments['CodeChallenge'] = self._getCodeChallenge(method)
        return arguments

    def _getRedirectUri(self, provider):
        return Template(provider.getByName('RedirectUri')).safe_substitute({'Port': self._port})

    def _getSignInArguments(self, url, arguments):
        return {'user': self._user,
                'url':  self._getUrlArguments(url, arguments)}

    def _getUrlArguments(self, url, arguments):
        query = '&'.join(('%s=%s' % (k, v) for k, v in arguments.items()))
        return self._getUrl(url, query)

    def _getUrl(self, url, query):
        return '%s?%s' % (url, query)

    def _getUrlScopes(self, scope, provider):
        scopes = self._getUserScopes(provider)
        for s in scope.getByName('Values'):
            if s not in scopes:
                scopes.append(s)
        return scopes

    def _getUserScopes(self, provider):
        scopes = []
        users = provider.getByName('Users')
        if users.hasByName(self._user):
            scopes = list(users.getByName(self._user).getByName('Scopes'))
        return scopes

# WizardModel getter methods called by WizardPages 3
    def getAuthorizationData(self):
        scopes, url, arguments = self._getAuthorizationData()
        msg = "Make HTTP Request: %s" % self._getUrlArguments(url, arguments)
        self._logger.logp(INFO, 'WizardModel', 'getAuthorizationData()', msg)
        return scopes, self._getUrl(url, requests.compat.urlencode(arguments))

    def startServer(self, scopes, notify, register):
        self._cancelServer()
        lock = Condition()
        server = Server(self._ctx, self._user, self._getBaseUrl(), self._provider, self._host, self._port, self._code, lock)
        self._watchdog = WatchDog(self._ctx, server, notify, register, scopes, self._provider, self._user, self.HandlerTimeout, lock)
        server.start()
        self._watchdog.start()
        self._logger.logp(INFO, 'OAuth2Manager', 'startServer()', "WizardServer Started ... Done")

    def isServerRunning(self):
        return self._watchdog is not None and self._watchdog.isRunning()

    def registerToken(self, source, scopes, name, user, code):
        provider = self._config.getByName('Providers').getByName(name)
        return self._registerToken(source, scopes, provider, user, code)

    def getAuthorizationMessage(self, resolver, error):
        return self.getAuthorizationErrorTitle(resolver), self.getRequestErrorMessage(resolver, error)

# WizardModel getter methods called by WizardPages 4
    def closeWizard(self):
        return self._close

    def getTokenData(self, resolver):
        label = self.getTokenLabel(resolver)
        never, scopes, access, refresh, expires = self.getUserTokenData(resolver)
        return label, never, scopes, access, refresh, expires

    def getUserTokenData(self, resolver):
        users = self._config.getByName('Providers').getByName(self._provider).getByName('Users')
        user = users.getByName(self._user)
        scopes = user.getByName('Scopes')
        refresh = user.getByName('RefreshToken') if user.hasByName('RefreshToken') else self.getTokenRefresh(resolver)
        access = user.getByName('AccessToken') if user.hasByName('AccessToken') else self.getTokenAccess(resolver)
        timestamp = user.getByName('TimeStamp')
        never = user.getByName('NeverExpires')
        expires = self.getTokenExpires(resolver) if never else timestamp - int(time.time())
        return never, scopes, access, refresh, expires

    def refreshToken(self, source):
        provider = self._config.getByName('Providers').getByName(self._provider)
        user = provider.getByName('Users').getByName(self._user)
        self._refreshToken(source, provider, user)

    def deleteUser(self):
        providers = self._config.getByName('Providers')
        if providers.hasByName(self._provider):
            provider = providers.getByName(self._provider)
            users = provider.getByName('Users')
            if users.hasByName(self._user):
                users.removeByName(self._user)
                self.commit()

# WizardModel private getter methods called by WizardPages 1 and WizardPages 3
    def _getBaseUrl(self):
        return self._path + '%s' + self._language

# WizardModel private getter methods called by WizardPages 2 and WizardPages 3
    def _getCodeVerifier(self):
        return self._uuid + self._uuid

    def _getCodeChallenge(self, method):
        code = self._getCodeVerifier()
        if method == 'S256':
            if isinstance(code, string_types):
                code = code.encode('utf-8')
            code = hashlib.sha256(code).digest()
            padding = {0:0, 1:2, 2:1}[len(code) % 3]
            challenge = base64.urlsafe_b64encode(code).decode('utf-8')
            code = challenge[:len(challenge)-padding]
        return code

# WizardModel private getter/setter methods called by WizardPages 3
    def _registerToken(self, source, scopes, provider, user, code):
        error = None
        arguments = self._getTokenArguments(scopes, provider, code)
        request = provider.getByName('Token')
        name = request.getByName('Name')
        parameter = RequestParameter(name)
        setParametersArguments(request.getByName('Parameters'), arguments)
        setResquestParameter(arguments, request, parameter)
        parser = CustomParser(*getParserItems(request))
        timestamp = int(time.time())
        cls, mtd = 'WizardModel', '_registerToken()'
        try:
            response = getRequestResponse(self._ctx, source, requests.Session(), cls, mtd, parameter, self.Timeout)
        except UnoException as e:
            error = e.Message
        msg = "Receive Response Status: %s - Content: %s" % (response.StatusCode, response.Text)
        if response.Ok and parser.hasItems():
            results = getResponseResults(parser, response)
            self._saveUserToken(scopes, provider, user, results, timestamp)
        else:
            error = msg
        response.close()
        self._logger.logp(INFO, 'WizardModel', '_registerToken()', msg)
        return error

    def _getTokenArguments(self, scopes, provider, code):
        arguments = {'ClientSecret': provider.getByName('ClientSecret'),
                     'ClientId':     provider.getByName('ClientId'),
                     'RedirectUri':  self._getRedirectUri(provider),
                     'Scopes':       ' '.join(scopes),
                     'Code':         code}
        method = provider.getByName('CodeChallengeMethod')
        if method:
            arguments['CodeVerifier'] = self._getCodeVerifier()
        return arguments

    def _saveUserToken(self, scopes, provider, name, results, timestamp):
        users = provider.getByName('Users')
        if not users.hasByName(name):
            users.insertByName(name, users.createInstance())
        user = users.getByName(name)
        # user.replaceByName('Scopes', scopes)
        arguments = ('Scopes', uno.Any('[]string', tuple(scopes)))
        uno.invoke(user, 'replaceByName', arguments)
        refresh, access, never, expires = self._getTokenFromResults(results, timestamp)
        self._saveTokens(user, refresh, access, never, expires)

# WizardModel private getter/setter methods
    def _saveTokens(self, user, refresh, access, never, timestamp):
        if refresh is not None:
            user.replaceByName('RefreshToken', refresh)
        self._saveRefreshedToken(user, refresh, access, never, timestamp)

    def _findFreePort(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

# WizardModel StringResource methods
    def getPageStep(self, resolver, pageid):
        resource = self._resources.get('Step') % pageid
        return resolver.resolveString(resource)

    def getPageTitle(self, resolver, pageid):
        resource = self._resources.get('Title') % pageid
        return resolver.resolveString(resource)

    def getUrlLabel(self, resolver, url):
        resource = self._resources.get('UrlLabel')
        return resolver.resolveString(resource) % url

    def getProviderTitle(self, resolver, name):
        resource = self._resources.get('ProviderTitle')
        return resolver.resolveString(resource) % name

    def getScopeTitle(self, resolver, name):
        resource = self._resources.get('ScopeTitle')
        return resolver.resolveString(resource) % name

    def getTokenLabel(self, resolver):
        resource = self._resources.get('TokenLabel')
        return resolver.resolveString(resource) % (self._provider, self._user)

    def getTokenAccess(self, resolver):
        resource = self._resources.get('TokenAccess')
        return resolver.resolveString(resource)

    def getTokenRefresh(self, resolver):
        resource = self._resources.get('TokenRefresh')
        return resolver.resolveString(resource)

    def getTokenExpires(self, resolver):
        resource = self._resources.get('TokenExpires')
        return resolver.resolveString(resource)

    def getDialogTitle(self):
        resource = self._resources.get('DialogTitle')
        return self._resolver.resolveString(resource)

    def getDialogMessage(self):
        resource = self._resources.get('DialogMessage')
        return self._resolver.resolveString(resource)

    def getAuthorizationErrorTitle(self, resolver):
        resource = self._resources.get('AuthorizationError')
        return resolver.resolveString(resource)

    def getTokenErrorTitle(self, resolver):
        resource = self._resources.get('TokenError')
        return resolver.resolveString(resource)

    def getRequestErrorMessage(self, resolver, error):
        resource = self._resources.get('RequestMessage')
        return resolver.resolveString(resource % error)

