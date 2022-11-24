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

from oauth2 import g_extension
from oauth2 import g_identifier
from oauth2 import g_refresh_overlap
from oauth2 import generateUuid
from oauth2 import getConfiguration
from oauth2 import getCurrentLocale
from oauth2 import getStringResource
from oauth2 import logMessage

from requests.compat import urlencode
from requests import Session

from .wizard import WatchDog
from .wizard import Server

import time
import validators
import base64
import hashlib
import json
from threading import Condition
import traceback


class OAuth2Model(unohelper.Base):
    def __init__(self, ctx, close=False):
        self._ctx = ctx
        self._user = ''
        self._url = ''
        self._scope = ''
        self._provider = ''
        self._uuid = ''
        self._close = close
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
                           'DialogMessage': 'MessageBox.Message'}

    @property
    def User(self):
        return self._user
    @User.setter
    def User(self, user):
        self._user = user

    @property
    def Url(self):
        return self._url
    @Url.setter
    def Url(self, url):
        self._url = url
        self._scope, self._provider = self._getUrlData(url)
        self._uuid = generateUuid()

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

# OAuth2Model getter methods called by OAuth2Service
    def isInitialized(self):
        providers = self._configuration.getByName('Providers')
        if providers.hasByName(self._provider):
            users = providers.getByName(self._provider).getByName('Users')
            return users.hasByName(self._user)
        return False

    def isUrlScopeAuthorized(self):
        scopes = self._configuration.getByNames('Scopes')
        providers = self._configuration.getByName('Providers')
        if scopes.hasByName(self._scope):
            values = providers.getByName(self._provider).getByName('Users').getByName(self._user).getByName('Scopes')
            for scope in scopes.getByName(self._scope).getByName('Values'):
                if scope not in values:
                    return False
            return True
        return False

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

# OAuth2Model getter methods called by WizardPages 1
    def getActivePath(self, user, url):
        scope = self._getScope(url)
        provider = self._getProvider(scope)
        providers = self._configuration.getByName('Providers')
        if self.isAuthorized(user, scope, provider, providers):
            path = 2
        elif providers.hasByName(provider) and not providers.getByName(provider).getByName('HttpHandler'):
            path = 1
        else:
            path = 0
        return path

    def isAuthorized(self, user, scope, provider, providers):
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
        return scope, self._getScopeList(), provider, self._getProviderList()

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

    def _getScopeList(self):
        return self._configuration.getByName('Scopes').ElementNames

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

    def _getCodeChallenge(self, method):
        code = self._getCodeVerifier()
        if method == 'S256':
            code = hashlib.sha256(code.encode('utf-8')).digest()
            padding = {0:0, 1:2, 2:1}[len(code) % 3]
            challenge = base64.urlsafe_b64encode(code).decode('utf-8')
            code = challenge[:len(challenge)-padding]
        return code

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
        parameters = urlencode(self._getUrlParameters(scopes, provider))
        url = '%s?%s' % (main, parameters)
        if provider.getByName('SignIn'):
            main = self._getSignInUrl()
            parameters = urlencode(self._getSignInParameters(url))
            url = '%s?%s' % (main, parameters)
        return scopes, url

    def startServer(self, scopes, notify, register):
        self.cancelServer()
        provider, user, url, address, port, uuid, timeout = self._getServerData()
        lock = Condition()
        server = Server(self._ctx, user, url, address, port, uuid, lock)
        self._watchdog = WatchDog(self._ctx, server, notify, register, scopes, provider, user, timeout, lock)
        server.start()
        self._watchdog.start()
        logMessage(self._ctx, INFO, "WizardServer Started ... Done", 'OAuth2Manager', 'startServer()')

    def canAdvance(self):
        return self._watchdog is None

    def cancelServer(self):
        if self._watchdog is not None:
            if self._watchdog.is_alive():
                self._watchdog.cancel()
            self._watchdog = None

    def registerUserToken(self, scopes, name, user, code):
        self._registerUserToken(scopes, name, user, code)
        self._watchdog = None

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
        self._registerUserToken(scopes, self._provider, self._user, code)

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
            refresh = user.getByName('RefreshToken')
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
        response = self._getResponseFromRequest(url, data, self.Timeout)
        self._saveToken(user, *self._getTokenFromResponse(response))

    def revokeToken(self):
        provider = self._configuration.getByName('Providers').getByName(self._provider)
        user = provider.getByName('Users').getByName(self._user)
        token = user.getByName('AccessToken')
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % token
        data = {'token': token}
        response = self._getResponseFromRequest(url, data, self.Timeout)
        print("OAuth2Model.revokeToken() %s" % (response, ))

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

# OAuth2Model private getter/setter methods called by WizardPages 3 and WizardPages 4
    def _registerUserToken(self, scopes, name, user, code):
        provider = self._configuration.getByName('Providers').getByName(name)
        url = provider.getByName('TokenUrl')
        parameters = self._getTokenParameters(scopes, provider, code)
        msg = "Make Http Request: %s?%s" % (url, parameters)
        logMessage(self._ctx, INFO, msg, 'OAuth2Model', '_registerToken()')
        response = self._getResponseFromRequest(url, parameters, self.Timeout)
        self._saveUserToken(scopes, provider, user, response)

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

    def _saveUserToken(self, scopes, provider, name, response):
        users = provider.getByName('Users')
        if not users.hasByName(name):
            users.insertByName(name, users.createInstance())
        user = users.getByName(name)
        # user.replaceByName('Scopes', scopes)
        arguments = ('Scopes', uno.Any('[]string', tuple(scopes)))
        uno.invoke(user, 'replaceByName', arguments)
        self._saveToken(user, *self._getTokenFromResponse(response))

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
                print("ERROR: OAuth2Model._getResponseFromRequest() %s - %s" % (response, traceback.print_exc()))
        return response

    def _getTokenFromResponse(self, response):
        print("OAuth2Model._getTokenFromResponse() %s" % (response, ))
        refresh = response.get('refresh_token', None)
        access = response.get('access_token', None)
        expires = response.get('expires_in', None)
        never = expires is None
        timestamp = 0 if never else int(time.time()) + expires
        return refresh, access, never, timestamp

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

