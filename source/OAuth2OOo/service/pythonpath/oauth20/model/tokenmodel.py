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

from com.sun.star.auth import RefreshTokenException

from .basemodel import BaseModel

from ..requestparameter import RequestParameter

from ..oauth2 import CustomParser

from ..oauth2helper import isUserAuthorized

from ..requestresponse import getRequestResponse

from ..oauth2 import getParserItems
from ..oauth2 import getResponseResults
from ..oauth2 import setParametersArguments
from ..oauth2 import setResquestParameter

from ..unotool import executeDispatch
from ..unotool import getPropertyValueSet

from ..configuration import g_refresh_overlap

import time
import requests
import traceback


class TokenModel(BaseModel):
    def __init__(self, ctx, url='', user=''):
        super(TokenModel, self).__init__(ctx)
        if url and user:
            self.initialize(url, user)
        else:
            self._isoauth2 = False
            self._url = self._user = ''
            self._scope = self._provider = ''

# TokenModel setter methods
    def initialize(self, url, user):
        self._isoauth2 = True
        self._url = url
        self._user = user
        self._scope, self._provider = self._getUrlData(url)

# TokenModel getter methods
    def isOAuth2(self):
        return self._isoauth2

    def isAuthorized(self):
        if not self.hasAuthorization():
            args = {'Url': self._url, 'UserName': self._user, 'ReadOnly': True}
            executeDispatch(self._ctx, 'oauth2:wizard', getPropertyValueSet(args))
            return self.hasAuthorization()
        return True

    def hasAuthorization(self):
        if self._isoauth2:
            scopes = self._config.getByName('Scopes')
            providers = self._config.getByName('Providers')
            return isUserAuthorized(scopes, providers, self._scope, self._provider, self._user)
        return True

    def getAccessToken(self, source):
        token = ''
        if self._isoauth2:
            providers = self._config.getByName('Providers')
            if self._isAccessTokenExpired(providers):
                token = self._getRefreshedToken(source, providers)
            else:
                token = self._getAccessToken(providers)
        return token

# TokenModel private methods
    def _getUrlData(self, url):
        scope = provider = ''
        urls = self._config.getByName('Urls')
        if urls.hasByName(url):
            scope = urls.getByName(url).getByName('Scope')
            scopes = self._config.getByName('Scopes')
            if scopes.hasByName(scope):
                provider = scopes.getByName(scope).getByName('Provider')
        return scope, provider

    def _isAccessTokenExpired(self, providers):
        if providers.hasByName(self._provider):
            provider = providers.getByName(self._provider)
            users = provider.getByName('Users')
            if users.hasByName(self._user):
                user = users.getByName(self._user)
                if user.getByName('NeverExpires'):
                    return False
                now = int(time.time())
                expire = max(0, user.getByName('TimeStamp') - now)
                return expire < g_refresh_overlap
        return True

    def _getRefreshedToken(self, source, providers):
        if providers.hasByName(self._provider):
            provider = providers.getByName(self._provider)
            users = provider.getByName('Users')
            if users.hasByName(self._user):
                user = users.getByName(self._user)
                self._refreshToken(source, provider, user)
                return user.getByName('AccessToken')
        return None

    def _getAccessToken(self, providers):
        if providers.hasByName(self._provider):
            provider = providers.getByName(self._provider)
            users = provider.getByName('Users')
            if users.hasByName(self._user):
                user = users.getByName(self._user)
                return user.getByName('AccessToken')

    def _refreshToken(self, source, provider, user):
        arguments = self._getRefreshArguments(user, provider)
        request = provider.getByName('RefreshToken')
        name = request.getByName('Name')
        parameter = RequestParameter(name)
        setParametersArguments(request.getByName('Parameters'), arguments)
        setResquestParameter(arguments, request, parameter)
        parser = CustomParser(*getParserItems(request))
        timestamp = int(time.time())
        cls, mtd = 'TokenModel', '_refreshToken()'
        response = getRequestResponse(self._ctx, source, requests.Session(), cls, mtd, parameter, self.Timeout)
        if response.Ok and parser.hasItems():
            results = getResponseResults(parser, response)
            response.close()
            refresh, access, never, expires = self._getTokenFromResults(results, timestamp)
            self._saveRefreshedToken(user, refresh, access, never, expires)
        else:
            msg = '%s::%s ERROR: %s' % (cls, mtd, response.Text)
            response.close()
            raise self._getRefreshTokenException(msg)

    def _getRefreshArguments(self, user, provider):
        return {'ClientSecret': provider.getByName('ClientSecret'),
                'ClientId':     provider.getByName('ClientId'),
                'RedirectUri':  provider.getByName('RedirectUri'),
                'RefreshToken': user.getByName('RefreshToken'),
                'Scopes':       ' '.join(user.getByName('Scopes'))}

    def _getTokenFromResults(self, results, timestamp):
        refresh = results.get('RefreshToken', None)
        access = results.get('AccessToken', None)
        expires = results.get('ExpiresIn', None)
        never = expires is None
        return refresh, access, never, 0 if never else timestamp + expires

    def _saveRefreshedToken(self, user, refresh, access, never, timestamp):
        if access is not None:
            user.replaceByName('AccessToken', access)
        user.replaceByName('NeverExpires', never)
        user.replaceByName('TimeStamp', timestamp)
        self.commit()

    def _getRefreshTokenException(self, message):
        error = RefreshTokenException()
        error.Message = message
        error.ResourceUrl = self._url
        error.UserName = self._user
        return error

