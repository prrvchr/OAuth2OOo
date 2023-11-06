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

from com.sun.star.uno import Exception as UnoException

from ..model import TokenModel

from .httpserver import WatchDog
from .httpserver import Server

from ..requestresponse import getResponse

from ..unotool import generateUuid
from ..unotool import getCurrentLocale
from ..unotool import getStringResource

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
from threading import Condition
import traceback


class WizardModel(TokenModel):
    def __init__(self, ctx, close=False, readonly=False, url='', user=''):
        super(WizardModel, self).__init__(ctx, url, user)
        self._uuid = generateUuid()
        self._close = close
        self._readonly = readonly
        self._uri = 'http://%s:%s/'
        self._urn = 'urn:ietf:wg:oauth:2.0:oob'
        self._watchdog = None
        self._logger = getLogger(ctx, g_defaultlog, g_basename)
        self._resolver = getStringResource(ctx, g_identifier, g_extension)
        self._resources = {'Title': 'PageWizard%s.Title',
                           'Step': 'PageWizard%s.Step',
                           'UrlLabel': 'PageWizard1.Label4.Label',
                           'ProviderTitle': 'ProviderDialog.Title',
                           'ScopeTitle': 'ScopeDialog.Title',
                           'AuthorizationError': 'PageWizard3.Label2.Label',
                           'RequestMessage': 'PageWizard3.TextField1.Text.%s',
                           'TokenError': 'PageWizard4.Label2.Label',
                           'TokenLabel': 'PageWizard5.Label1.Label',
                           'TokenAccess': 'PageWizard5.Label6.Label',
                           'TokenRefresh': 'PageWizard5.Label4.Label',
                           'TokenExpires': 'PageWizard5.Label8.Label',
                           'DialogTitle': 'MessageBox.Title',
                           'DialogMessage': 'MessageBox.Message'}

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
            path = 2
        elif providers.hasByName(provider) and not providers.getByName(provider).getByName('HttpHandler'):
            path = 1
        else:
            path = 0
        return path

    def getInitData(self):
        return self._user, self._url, self.UrlList, not self._readonly

    def getProviderData(self, name):
        providers = self._config.getByName('Providers')
        if providers.hasByName(name):
            data = self._getProviderData(providers.getByName(name))
        else:
            data = self._getDefaultProviderData()
        return self.getProviderTitle(name), data

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

    def getScopeData(self, name):
        title = self.getScopeTitle(name)
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
        return self._getBaseUrl() % 'TermsOfUse'

    def getPrivacyPolicy(self):
        return self._getBaseUrl() % 'PrivacyPolicy'

    def getAuthorizationStr(self):
        scope = self._config.getByName('Scopes').getByName(self._scope)
        provider = self._config.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        main = provider.getByName('AuthorizationUrl')
        parameters = self._getUrlParameters(scopes, provider)
        arguments = self._getUrlArguments(parameters)
        url = '%s?%s' % (main, arguments)
        if provider.getByName('SignIn'):
            main = self._getSignInUrl(provider)
            parameters = self._getSignInParameters(url)
            arguments = self._getUrlArguments(parameters)
            url = '%s?%s' % (main, arguments)
        return url

    def _getUrlArguments(self, parameters):
        arguments = []
        for key, value in parameters.items():
            arguments.append('%s=%s' % (key, value))
        return '&'.join(arguments)

    def _getSignInUrl(self, provider):
        page = provider.getByName('SignInPage')
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

# WizardModel getter methods called by WizardPages 3
    def getAuthorizationData(self):
        scope = self._config.getByName('Scopes').getByName(self._scope)
        provider = self._config.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        main = provider.getByName('AuthorizationUrl')
        parameters = self._getUrlParameters(scopes, provider)
        url = '%s?%s' % (main, requests.compat.urlencode(parameters))
        if provider.getByName('SignIn'):
            main = self._getSignInUrl(provider)
            parameters = self._getSignInParameters(url)
            url = '%s?%s' % (main, requests.compat.urlencode(parameters))
        msg = "Make HTTP Request: %s?%s" % (main, self._getUrlArguments(parameters))
        self._logger.logp(INFO, 'WizardModel', 'getAuthorizationData()', msg)
        return scopes, url

    def startServer(self, scopes, notify, register):
        self._cancelServer()
        provider = self._config.getByName('Providers').getByName(self._provider)
        address = provider.getByName('RedirectAddress')
        port = provider.getByName('RedirectPort')
        lock = Condition()
        server = Server(self._ctx, self._user, self._getBaseUrl(), self._provider, address, port, self._uuid, lock)
        self._watchdog = WatchDog(self._ctx, server, notify, register, scopes, self._provider, self._user, self.HandlerTimeout, lock)
        server.start()
        self._watchdog.start()
        self._logger.logp(INFO, 'OAuth2Manager', 'startServer()', "WizardServer Started ... Done")

    def isServerRunning(self):
        return self._watchdog is not None and self._watchdog.isRunning()

    def registerToken(self, source, scopes, name, user, code):
        provider = self._config.getByName('Providers').getByName(name)
        return self._registerToken(source, scopes, provider, user, code)

    def getAuthorizationMessage(self, error):
        return self.getAuthorizationErrorTitle(), self.getRequestErrorMessage(error)

# WizardModel getter methods called by WizardPages 4
    def isCodeValid(self, code):
        return code != ''

    def setAuthorization(self, source, code):
        scope = self._config.getByName('Scopes').getByName(self._scope)
        provider = self._config.getByName('Providers').getByName(self._provider)
        scopes = self._getUrlScopes(scope, provider)
        return self._registerToken(source, scopes, provider, self._user, code)

# WizardModel getter methods called by WizardPages 5
    def closeWizard(self):
        return self._close

    def getTokenData(self):
        label = self.getTokenLabel()
        never, scopes, access, refresh, expires = self.getUserTokenData()
        return label, never, scopes, access, refresh, expires

    def getUserTokenData(self):
        users = self._config.getByName('Providers').getByName(self._provider).getByName('Users')
        user = users.getByName(self._user)
        scopes = user.getByName('Scopes')
        refresh = user.getByName('RefreshToken') if user.hasByName('RefreshToken') else self.getTokenRefresh()
        access = user.getByName('AccessToken') if user.hasByName('AccessToken') else self.getTokenAccess()
        timestamp = user.getByName('TimeStamp')
        never = user.getByName('NeverExpires')
        expires = self.getTokenExpires() if never else timestamp - int(time.time())
        return never, scopes, access, refresh, expires

    def refreshToken(self, source):
        provider = self._config.getByName('Providers').getByName(self._provider)
        user = provider.getByName('Users').getByName(self._user)
        return self._refreshToken(source, provider, user, True)

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
        return self._config.getByName('BaseUrl')

# WizardModel private getter methods called by WizardPages 2 and WizardPages 3
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
            if isinstance(code, string_types):
                code = code.encode('utf-8')
            code = hashlib.sha256(code).digest()
            padding = {0:0, 1:2, 2:1}[len(code) % 3]
            challenge = base64.urlsafe_b64encode(code).decode('utf-8')
            code = challenge[:len(challenge)-padding]
        return code

# WizardModel private getter/setter methods called by WizardPages 3 and WizardPages 4
    def _registerToken(self, source, scopes, provider, user, code):
        error = None
        session = requests.Session()
        url = provider.getByName('TokenUrl')
        data = self._getTokenParameters(scopes, provider, code)
        msg = "Make HTTP Request: %s?%s" % (url, self._getUrlArguments(data))
        self._logger.logp(INFO, 'WizardModel', '_registerToken()', msg)
        timestamp = int(time.time())
        cls, mtd = 'WizardModel', '_registerToken()'
        name = 'Register Token for User: %s' % user
        try:
            response = getResponse(self._ctx, source, session, cls, mtd, name,
                                   'POST', url, self.Timeout, {'data': data})
        except UnoException as e:
            error = e.Message
        msg = "Receive Response Status: %s - Content: %s" % (response.status_code, response.text)
        if response.ok:
            self._saveUserToken(scopes, provider, user, response, timestamp)
        else:
            error = msg
        response.close()
        self._logger.logp(INFO, 'WizardModel', '_registerToken()', msg)
        return error

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
        refresh, access, never, expires = self._getTokenFromResponse(response, timestamp)
        self._saveTokens(user, refresh, access, never, expires)

# WizardModel private getter/setter methods
    def _saveTokens(self, user, refresh, access, never, timestamp):
        if refresh is not None:
            user.replaceByName('RefreshToken', refresh)
        self._saveRefreshedToken(user, refresh, access, never, timestamp)

# WizardModel StringResource methods
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

    def getAuthorizationErrorTitle(self):
        resource = self._resources.get('AuthorizationError')
        return self._resolver.resolveString(resource)

    def getTokenErrorTitle(self):
        resource = self._resources.get('TokenError')
        return self._resolver.resolveString(resource)

    def getRequestErrorMessage(self, error):
        resource = self._resources.get('RequestMessage')
        return self._resolver.resolveString(resource % error)

