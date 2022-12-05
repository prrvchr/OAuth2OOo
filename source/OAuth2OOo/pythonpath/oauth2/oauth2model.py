#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
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
import unohelper

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.frame.DispatchResultState import SUCCESS

from .configuration import g_extension
from .configuration import g_identifier
from .configuration import g_refresh_overlap

from .unotool import generateUuid
from .unotool import getConfiguration
from .unotool import getCurrentLocale
from .unotool import getStringResource

from .logger import logMessage
from .logger import disposeLogger

from .wizard import WatchDog
from .wizard import Server

from requests.compat import urlencode
from requests import Session
import time
import validators
import base64
import hashlib
import json
from threading import Condition
import traceback


class OAuth2Model(unohelper.Base):
    def __init__(self, ctx, close=None, url='', user=''):
        self._ctx = ctx
        self._user = ''
        self._url = ''
        self._scope = ''
        self._provider = ''
        self._uuid = ''
        self._close = False
        self._uri = 'http://%s:%s/'
        self._urn = 'urn:ietf:wg:oauth:2.0:oob'
        self._watchdog = None
        self._configuration = getConfiguration(ctx, g_identifier, True)
        self._resolver = getStringResource(ctx, g_identifier, g_extension)
        self._resources = {'Title': 'PageWizard%s.Title',
                           'Step': 'PageWizard%s.Step',
                           'UrlLabel': 'PageWizard1.Label4.Label',
                           'ProviderTitle': 'ProviderDialog.Title',
                           'ScopeTitle': 'ScopeDialog.Title',
                           'TokenLabel': 'PageWizard5.Label1.Label',
                           'TokenAccess': 'PageWizard5.Label7.Label',
                           'TokenRefresh': 'PageWizard5.Label5.Label',
                           'TokenExpires': 'PageWizard5.Label9.Label',
                           'DialogTitle': 'MessageBox.Title',
                           'DialogMessage': 'MessageBox.Message',
                           'UserTitle': 'UserDialog.Title',
                           'UserLabel': 'UserDialog.Label1.Label'}
        self.initialize(url, user, close)

    def initialize(self, url, user, close=None):
        self._user = user
        self.initializeUrl(url, close)

    def initializeUrl(self, url, close=None):
        self._url = url
        self._scope, self._provider = self._getUrlData(url)
        self._uuid = generateUuid()
        if close is not None:
            self._close = close

    def _getUrlData(self, url):
        scope = provider = ''
        urls = self._configuration.getByName('Urls')
        if urls.hasByName(url):
            scope = urls.getByName(url).getByName('Scope')
            scopes = self._configuration.getByName('Scopes')
            if scopes.hasByName(scope):
                provider = scopes.getByName(scope).getByName('Provider')
        return scope, provider

    @property
    def User(self):
        return self._user

    @property
    def Url(self):
        return self._url

    @property
    def Timeout(self):
        return self._configuration.getByName('ConnectTimeout'), self._configuration.getByName('ReadTimeout')
    @property
    def ConnectTimeout(self):
        return self._configuration.getByName('ConnectTimeout')
    @ConnectTimeout.setter
    def ConnectTimeout(self, timeout):
        self._configuration.replaceByName('ConnectTimeout', timeout)
    @property
    def ReadTimeout(self):
        return self._configuration.getByName('ReadTimeout')
    @ReadTimeout.setter
    def ReadTimeout(self, timeout):
        self._configuration.replaceByName('ReadTimeout', timeout)
    @property
    def HandlerTimeout(self):
        return self._configuration.getByName('HandlerTimeout')
    @HandlerTimeout.setter
    def HandlerTimeout(self, timeout):
        self._configuration.replaceByName('HandlerTimeout', timeout)
    @property
    def UrlList(self):
        return self._configuration.getByName('Urls').ElementNames

    def commit(self):
        if self._configuration.hasPendingChanges():
            self._configuration.commitChanges()

    def getProviderName(self, url):
        provider = ''
        if self._configuration.getByName('Urls').hasByName(url):
            scope = self._configuration.getByName('Urls').getByName(url).getByName('Scope')
            if self._configuration.getByName('Scopes').hasByName(scope):
                provider = self._configuration.getByName('Scopes').getByName(scope).getByName('Provider')
        return provider

# OAuth2Model getter methods called by OptionsManager
    def getOptionsDialogData(self):
        return self.ConnectTimeout, self.ReadTimeout, self.HandlerTimeout, self.UrlList

# OAuth2Model getter methods called by OAuth2Handler
    def getUserData(self, url, msg):
        provider = self.getProviderName(url)
        title = self.getUserTitle(provider)
        label = self.getUserLabel(msg)
        return title, label

# OAuth2Model getter methods called by OAuth2Service
    def isAccessTokenExpired(self):
        providers = self._configuration.getByName('Providers')
        user = providers.getByName(self._provider).getByName('Users').getByName(self._user)
        if user.getByName('NeverExpires'):
            return False
        now = int(time.time())
        expire = max(0, user.getByName('TimeStamp') - now)
        return expire < g_refresh_overlap

    def getRefreshedToken(self):
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        user = provider.getByName('Users').getByName(self._user)
        self._refreshToken(provider, user)
        return user.getByName('AccessToken')

    def getToken(self):
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        user = provider.getByName('Users').getByName(self._user)
        return user.getByName('AccessToken')
 
    def dispose(self):
        self.cancelServer()
        disposeLogger()

    def initializeSession(self, url, user):
        self.initialize(url, user)
        return self.isAuthorized()

    def isAuthorized(self):
        providers = self._configuration.getByName('Providers')
        return self._isInitialized(providers) and self._isUrlScopeAuthorized(providers)

    def _isInitialized(self, providers):
        if providers.hasByName(self._provider):
            users = providers.getByName(self._provider).getByName('Users')
            return users.hasByName(self._user)
        return False

    def _isUrlScopeAuthorized(self, providers):
        scopes = self._configuration.getByName('Scopes')
        if scopes.hasByName(self._scope):
            values = providers.getByName(self._provider).getByName('Users').getByName(self._user).getByName('Scopes')
            for scope in scopes.getByName(self._scope).getByName('Values'):
                if scope not in values:
                    return False
            return True
        return False

# OAuth2Model getter methods called by WizardPages 1
    def getActivePath(self, user, url, provider, scope):
        urls = self._configuration.getByName('Urls')
        providers = self._configuration.getByName('Providers')
        if urls.hasByName(url) and self._isAuthorized(user, scope, provider, providers):
            path = 2
        elif providers.hasByName(provider) and not providers.getByName(provider).getByName('HttpHandler'):
            path = 1
        else:
            path = 0
        return path

    def _isAuthorized(self, user, scope, provider, providers):
        values = self._getScopeValues(scope)
        authorized = len(values) > 0
        scopes = ()
        if providers.hasByName(provider):
            users = providers.getByName(provider).getByName('Users')
            if users.hasByName(user):
                scopes = users.getByName(user).getByName('Scopes')
        for value in values:
            if value not in scopes:
                authorized = False
                break
        return authorized

    def getInitData(self):
        return self._user, self._url, self.UrlList

    def getProviderData(self, name):
        providers = self._configuration.getByName('Providers')
        if providers.hasByName(name):
            data = self._getProviderData(providers.getByName(name))
        else:
            data = self._getDefaultProviderData()
        return data

    def saveProviderData(self, name, handler, address, port, clientsecret, challenge, challengemethod,
                         clientid, authorizationurl, tokenurl, authorizationparameters, tokenparameters):
        providers = self._configuration.getByName('Providers')
        if not providers.hasByName(name):
            providers.insertByName(name, providers.createInstance())
        provider = providers.getByName(name)
        provider.replaceByName('HttpHandler', handler)
        provider.replaceByName('RedirectAddress', address)
        provider.replaceByName('RedirectPort', port)
        provider.replaceByName('ClientSecret', clientsecret)
        provider.replaceByName('CodeChallenge', challenge)
        provider.replaceByName('CodeChallengeMethod', challengemethod)
        provider.replaceByName('ClientId', clientid)
        provider.replaceByName('AuthorizationUrl', authorizationurl)
        provider.replaceByName('TokenUrl', tokenurl)
        provider.replaceByName('AuthorizationParameters', authorizationparameters)
        provider.replaceByName('TokenParameters', tokenparameters)
        self.commit()

    def getScopeData(self, name):
        title = self.getScopeTitle(name)
        scopes = self._configuration.getByName('Scopes')
        if scopes.hasByName(name):
            values = scopes.getByName(name).getByName('Values')
        else:
            values = ()
        return title, values

    def saveScopeData(self, name, provider, values):
        scopes = self._configuration.getByName('Scopes')
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
        authorizationurl = provider.getByName('AuthorizationUrl')
        tokenurl = provider.getByName('TokenUrl')
        codechallenge = provider.getByName('CodeChallenge')
        codechallengemethod = provider.getByName('CodeChallengeMethod')
        clientsecret = provider.getByName('ClientSecret')
        authorizationparameters = provider.getByName('AuthorizationParameters')
        tokenparameters = provider.getByName('TokenParameters')
        redirectaddress = provider.getByName('RedirectAddress')
        redirectport = provider.getByName('RedirectPort')
        httphandler = provider.getByName('HttpHandler')
        return (clientid, authorizationurl, tokenurl, codechallenge, codechallengemethod, clientsecret,
                authorizationparameters, tokenparameters, redirectaddress, redirectport, httphandler)

    def _getDefaultProviderData(self):
        clientid = ''
        authorizationurl = ''
        tokenurl = ''
        codechallenge = True
        codechallengemethod = 'S256'
        clientsecret = ''
        authorizationparameters = '{"prompt": "consent", "response_mode": "query", "scope": null, "login_hint": "current_user", "hl": "current_language"}'
        tokenparameters = '{"scope": null}'
        redirectaddress = 'localhost'
        redirectport = 8080
        httphandler = True
        return (clientid, authorizationurl, tokenurl, codechallenge, codechallengemethod, clientsecret,
                authorizationparameters, tokenparameters, redirectaddress, redirectport, httphandler)

    def getUrlData(self, url):
        scope = self._getScope(url)
        provider = self._getProvider(scope)
        return self._getProviderList(), provider, scope

    def addUrl(self, name, scope):
        urls = self._configuration.getByName('Urls')
        if not urls.hasByName(name):
            urls.insertByName(name, urls.createInstance())
        url = urls.getByName(name)
        url.replaceByName('Scope', scope)
        self.commit()

    def saveUrl(self, url, scope):
        urls = self._configuration.getByName('Urls')
        if urls.hasByName(url):
             urls.getByName(url).replaceByName('Scope', scope)
             self.commit()

    def removeUrl(self, url):
        urls = self._configuration.getByName('Urls')
        if urls.hasByName(url):
            urls.removeByName(url)
            self.commit()

    def canRemoveProvider(self, provider):
        scopes = self._configuration.getByName('Scopes')
        for scope in scopes.ElementNames:
            if scopes.getByName(scope).getByName('Provider') == provider:
                return False
        return True

    def canRemoveScope(self, scope):
        urls = self._configuration.getByName('Urls')
        for url in urls.ElementNames:
            if urls.getByName(url).getByName('Scope') == scope:
                return False
        return True

    def removeProvider(self, provider):
        providers = self._configuration.getByName('Providers')
        if providers.hasByName(provider):
            providers.removeByName(provider)
            self.commit()

    def removeScope(self, scope):
        scopes = self._configuration.getByName('Scopes')
        if scopes.hasByName(scope):
            scopes.removeByName(scope)
            self.commit()

    def isScopeChanged(self, url, scope):
        urls = self._configuration.getByName('Urls')
        if urls.hasByName(url):
            return urls.getByName(url).getByName('Scope') != scope
        return False

    def getScopeList(self, provider):
        scopes = []
        for name in self._configuration.getByName('Scopes').ElementNames:
            scope = self._configuration.getByName('Scopes').getByName(name)
            if scope.getByName('Provider') == provider:
                scopes.append(name)
        return tuple(scopes)

    def isConfigurationValid(self, email, url, provider, scope):
        return self.isEmailValid(email) and url != '' and provider != '' and scope != ''

    def isValueValid(self, value):
        return value != ''

    def isEmailValid(self, email):
        if validators.email(email):
            return True
        return False

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

    def isDialogValid(self, clientid, authorizationurl, tokenurl, authorizationparameters, tokenparameters):
        return (self.isTextValid(clientid) and self.isUrlValid(authorizationurl) and self.isUrlValid(tokenurl)
                and self.isJsonValid(authorizationparameters) and self.isJsonValid(tokenparameters))

    def _getScope(self, url):
        scope = ''
        urls = self._configuration.getByName('Urls')
        if urls.hasByName(url):
            scope = urls.getByName(url).getByName('Scope')
        return scope

    def _getProvider(self, scope):
        provider = ''
        scopes = self._configuration.getByName('Scopes')
        if scopes.hasByName(scope):
            provider = scopes.getByName(scope).getByName('Provider')
        return provider

    def _getScopeValues(self, scope):
        values = ()
        scopes = self._configuration.getByName('Scopes')
        if scopes.hasByName(scope):
            values = scopes.getByName(scope).getByName('Values')
        return values

    def _getProviderList(self):
        return self._configuration.getByName('Providers').ElementNames

# OAuth2Model getter methods called by WizardPages 2
    def getTermsOfUse(self):
        return self._getBaseUrl() % 'TermsOfUse'

    def getPrivacyPolicy(self):
        return self._getBaseUrl() % 'PrivacyPolicy'

    def getAuthorizationStr(self):
        scope = self._configuration.getByName('Scopes').getByName(self._scope)
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        main = provider.getByName('AuthorizationUrl')
        parameters = self._getUrlParameters(scopes, provider)
        arguments = self._getUrlArguments(parameters)
        url = '%s?%s' % (main, arguments)
        if provider.getByName('SignIn'):
            main = self._getSignInUrl()
            parameters = self._getSignInParameters(url)
            arguments = self._getUrlArguments(parameters)
            url = '%s?%s' % (main, arguments)
        return url

    def _getUrlArguments(self, parameters):
        arguments = []
        for key, value in parameters.items():
            arguments.append('%s=%s' % (key, value))
        return '&'.join(arguments)

    def _getSignInUrl(self):
        page = '%sSignIn' % self._provider
        return self._getBaseUrl() % page

    def _getSignInParameters(self, url):
        parameters = {}
        parameters['user'] = self._user
        parameters['url'] = url
        return parameters

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

# OAuth2Model getter methods called by WizardPages 3
    def getAuthorizationData(self):
        scope = self._configuration.getByName('Scopes').getByName(self._scope)
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        main = provider.getByName('AuthorizationUrl')
        parameters = self._getUrlParameters(scopes, provider)
        msg = "Make HTTP Request: %s?%s" % (main, self._getUrlArguments(parameters))
        logMessage(self._ctx, INFO, msg, 'OAuth2Model', 'getAuthorizationData()')
        url = '%s?%s' % (main, urlencode(parameters))
        if provider.getByName('SignIn'):
            main = self._getSignInUrl()
            parameters = urlencode(self._getSignInParameters(url))
            url = '%s?%s' % (main, parameters)
        return scopes, url

    def startServer(self, scopes, notify, register):
        self.cancelServer()
        provider, user, url, address, port, uuid, timeout = self._getServerData()
        lock = Condition()
        server = Server(self._ctx, user, url, provider, address, port, uuid, lock)
        self._watchdog = WatchDog(self._ctx, server, notify, register, scopes, provider, user, timeout, lock)
        server.start()
        self._watchdog.start()
        logMessage(self._ctx, INFO, "WizardServer Started ... Done", 'OAuth2Manager', 'startServer()')

    def cancelServer(self):
        if self._watchdog is not None:
            if self._watchdog.is_alive():
                self._watchdog.cancel()
            self._watchdog = None

    def registerToken(self, scopes, name, user, code):
        self._registerToken(scopes, name, user, code)

    def _getServerData(self):
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        address = provider.getByName('RedirectAddress')
        port = provider.getByName('RedirectPort')
        return self._provider, self._user, self._getBaseUrl(), address, port, self._uuid, self._getHandlerTimeout()

    def _getHandlerTimeout(self):
        return self._configuration.getByName('HandlerTimeout')

# OAuth2Model getter methods called by WizardPages 4
    def isCodeValid(self, code):
        return code != ''

    def setAuthorization(self, code):
        scope = self._configuration.getByName('Scopes').getByName(self._scope)
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        self._registerToken(scopes, self._provider, self._user, code)

# OAuth2Model getter methods called by WizardPages 5
    def closeWizard(self):
        return self._close

    def getTokenData(self):
        label = self.getTokenLabel()
        users = self._configuration.getByName('Providers').getByName(self._provider).getByName('Users')
        exist = users.hasByName(self._user)
        if exist:
            user = users.getByName(self._user)
            scopes = user.getByName('Scopes')
            refresh = user.getByName('RefreshToken') if user.hasByName('RefreshToken') else ''
            access = user.getByName('AccessToken')
            timestamp = user.getByName('TimeStamp')
            never = user.getByName('NeverExpires')
            expires = 0 if never else timestamp - int(time.time())
        else:
            scopes = ()
            access = self.getTokenAccess()
            refresh = self.getTokenRefresh()
            expires = self.getTokenExpires()
        return label, exist, scopes, access, refresh, expires

    def refreshToken(self):
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        user = provider.getByName('Users').getByName(self._user)
        self._refreshToken(provider, user)

    def _refreshToken(self, provider, user):
        url = provider.getByName('TokenUrl')
        data = self._getRefreshParameters(user, provider)
        timestamp = int(time.time())
        response = self._getResponseFromRequest(url, data, self.Timeout)
        self._saveToken(user, *self._getTokenFromResponse(response, timestamp))

    def deleteUser(self):
        providers = self._configuration.getByName('Providers')
        if providers.hasByName(self._provider):
            provider = providers.getByName(self._provider)
            users = provider.getByName('Users')
            if users.hasByName(self._user):
                users.removeByName(self._user)
                self.commit()

    def _getRefreshParameters(self, user, provider):
        parameters = self._getRefreshBaseParameters(user, provider)
        optional = self._getRefreshOptionalParameters(user, provider)
        option = provider.getByName('TokenParameters')
        parameters = self._parseParameters(parameters, optional, option)
        return parameters
    
    def _getRefreshBaseParameters(self, user, provider):
        parameters = {}
        parameters['refresh_token'] = user.getByName('RefreshToken')
        parameters['grant_type'] = 'refresh_token'
        parameters['client_id'] = provider.getByName('ClientId')
        return parameters
    
    def _getRefreshOptionalParameters(self, user, provider):
        parameters = {}
        parameters['scope'] = ' '.join(user.getByName('Scopes'))
        parameters['client_secret'] = provider.getByName('ClientSecret')
        return parameters

 # OAuth2Model private getter methods called by WizardPages 1 and WizardPages 3
    def _getBaseUrl(self):
        return self._configuration.getByName('BaseUrl')

# OAuth2Model private getter methods called by WizardPages 2 and WizardPages 3
    def _getCodeVerifier(self):
        return self._uuid + self._uuid

    def _getRedirectUri(self, provider):
        if provider.getByName('HttpHandler'):
            uri = self._uri % (provider.getByName('RedirectAddress'), provider.getByName('RedirectPort'))
        else:
            uri = self._urn
        return uri

    def _getUrlParameters(self, scopes, provider):
        parameters = self._getUrlBaseParameters(provider)
        optional = self._getUrlOptionalParameters(scopes, provider)
        option = provider.getByName('AuthorizationParameters')
        parameters = self._parseParameters(parameters, optional, option)
        return parameters

    def _getUrlBaseParameters(self, provider):
        parameters = {}
        parameters['response_type'] = 'code'
        parameters['client_id'] = provider.getByName('ClientId')
        parameters['state'] = self._uuid
        parameters['redirect_uri'] = self._getRedirectUri(provider)
        if provider.getByName('CodeChallenge'):
            method = provider.getByName('CodeChallengeMethod')
            parameters['code_challenge_method'] = method
            parameters['code_challenge'] = self._getCodeChallenge(method)
        return parameters

    def _getUrlOptionalParameters(self, scopes, provider):
        parameters = {}
        parameters['scope'] = ' '.join(scopes)
        parameters['client_secret'] = provider.getByName('ClientSecret')
        parameters['current_user'] = self._user
        parameters['current_language'] = getCurrentLocale(self._ctx).Language
        return parameters

    def _getCodeChallenge(self, method):
        code = self._getCodeVerifier()
        if method == 'S256':
            code = hashlib.sha256(code.encode('utf-8')).digest()
            padding = {0:0, 1:2, 2:1}[len(code) % 3]
            challenge = base64.urlsafe_b64encode(code).decode('utf-8')
            code = challenge[:len(challenge)-padding]
        return code

# OAuth2Model private getter/setter methods called by WizardPages 3 and WizardPages 4
    def _registerToken(self, scopes, name, user, code):
        provider = self._configuration.getByName('Providers').getByName(name)
        url = provider.getByName('TokenUrl')
        parameters = self._getTokenParameters(scopes, provider, code)
        msg = "Make HTTP Request: %s?%s" % (url, self._getUrlArguments(parameters))
        logMessage(self._ctx, INFO, msg, 'OAuth2Model', '_registerToken()')
        timestamp = int(time.time())
        response = self._getResponseFromRequest(url, parameters, self.Timeout)
        self._saveUserToken(scopes, provider, user, response, timestamp)
        msg = "Receive Response: %s" % (response, )
        logMessage(self._ctx, INFO, msg, 'OAuth2Model', '_registerToken()')

    def _getTokenParameters(self, scopes, provider, code):
        parameters = self._getTokenBaseParameters(provider, code)
        optional = self._getTokenOptionalParameters(scopes, provider)
        option = provider.getByName('TokenParameters')
        parameters = self._parseParameters(parameters, optional, option)
        return parameters

    def _getTokenBaseParameters(self, provider, code):
        parameters = {}
        parameters['code'] = code
        parameters['grant_type'] = 'authorization_code'
        parameters['client_id'] = provider.getByName('ClientId')
        parameters['redirect_uri'] = self._getRedirectUri(provider)
        if provider.getByName('CodeChallenge'):
            parameters['code_verifier'] = self._getCodeVerifier()
        return parameters

    def _getTokenOptionalParameters(self, scopes, provider):
        parameters = {}
        parameters['scope'] = ' '.join(scopes)
        parameters['client_secret'] = provider.getByName('ClientSecret')
        return parameters

    def _saveUserToken(self, scopes, provider, name, response, timestamp):
        users = provider.getByName('Users')
        if not users.hasByName(name):
            users.insertByName(name, users.createInstance())
        user = users.getByName(name)
        # user.replaceByName('Scopes', scopes)
        arguments = ('Scopes', uno.Any('[]string', tuple(scopes)))
        uno.invoke(user, 'replaceByName', arguments)
        self._saveToken(user, *self._getTokenFromResponse(response, timestamp))

# OAuth2Model private getter/setter methods
    def _parseParameters(self, base, optional, required):
        for key, value in json.loads(required).items():
            if value is None:
                if key in base:
                    del base[key]
                elif key in optional:
                    base[key] = optional[key]
            elif value in optional:
                base[key] = optional[value]
            else:
                base[key] = value
        return base

    def _getResponseFromRequest(self, url, data, timeout):
        session = Session()
        response = {}
        with session as s:
            try:
                with s.post(url, data=data, timeout=timeout) as r:
                    r.raise_for_status()
                    response = r.json()
            except Exception as e:
                msg = "HTTP ERROR: %s" % (e, )
                logMessage(self._ctx, SEVERE, msg, 'OAuth2Model', '_getResponseFromRequest()')
                print("ERROR: OAuth2Model._getResponseFromRequest() %s - %s" % (response, traceback.print_exc()))
        return response

    def _getTokenFromResponse(self, response, timestamp):
        print("OAuth2Model._getTokenFromResponse() %s" % (response, ))
        refresh = response.get('refresh_token', None)
        access = response.get('access_token', None)
        expires = response.get('expires_in', None)
        never = expires is None
        return refresh, access, never, 0 if never else timestamp + expires

    def _saveToken(self, user, refresh, access, never, timestamp):
        if refresh is not None:
            user.replaceByName('RefreshToken', refresh)
        if access is not None:
            user.replaceByName('AccessToken', access)
        user.replaceByName('NeverExpires', never)
        user.replaceByName('TimeStamp', timestamp)
        self.commit()

# OAuth2Model StringResource methods
    def getPageStep(self, pageid):
        resource = self._resources.get('Step') % pageid
        return self._resolver.resolveString(resource)

    def getPageTitle(self, pageid):
        resource = self._resources.get('Title') % pageid
        return self._resolver.resolveString(resource)

    def getUrlLabel(self, url):
        resource = self._resources.get('UrlLabel')
        return self._resolver.resolveString(resource) % url

    def getProviderTitle(self, name):
        resource = self._resources.get('ProviderTitle')
        return self._resolver.resolveString(resource) % name

    def getScopeTitle(self, name):
        resource = self._resources.get('ScopeTitle')
        return self._resolver.resolveString(resource) % name

    def getTokenLabel(self):
        resource = self._resources.get('TokenLabel')
        return self._resolver.resolveString(resource) % (self._provider, self._user)

    def getTokenAccess(self):
        resource = self._resources.get('TokenAccess')
        return self._resolver.resolveString(resource)

    def getTokenRefresh(self):
        resource = self._resources.get('TokenRefresh')
        return self._resolver.resolveString(resource)

    def getTokenExpires(self):
        resource = self._resources.get('TokenExpires')
        return self._resolver.resolveString(resource)

    def getDialogTitle(self):
        resource = self._resources.get('DialogTitle')
        return self._resolver.resolveString(resource)

    def getDialogMessage(self):
        resource = self._resources.get('DialogMessage')
        return self._resolver.resolveString(resource)

    def getUserTitle(self, provider):
        resource = self._resources.get('UserTitle')
        return self._resolver.resolveString(resource) % provider

    def getUserLabel(self, msg):
        resource = self._resources.get('UserLabel')
        return self._resolver.resolveString(resource) % msg

