#!
# -*- coding: utf-8 -*-

#from __futur__ import absolute_import

import uno

from .unotools import getCurrentLocale
from .requests.compat import urlencode

import json
import base64
import hashlib

g_advance_to = 2 # 0 to disable
g_wizard_paths = ((1, 2, 3), (1, 2, 4))
g_identifier = 'com.gmail.prrvchr.extensions.OAuth2OOo'
g_refresh_overlap = 10 # must be positive, in second


def getActivePath(configuration):
    return 0 if configuration.Url.Scope.Provider.HttpHandler else 1

def getAuthorizationStr(ctx, configuration, uuid):
    main = configuration.Url.Scope.Provider.AuthorizationUrl
    parameters = _getUrlArguments(ctx, configuration, uuid)
    return '%s?%s' % (main, parameters)

def checkUrl(ctx, configuration, uuid):
    transformer = ctx.ServiceManager.createInstance('com.sun.star.util.URLTransformer')
    url = uno.createUnoStruct('com.sun.star.util.URL')
    url.Complete = getAuthorizationStr(ctx, configuration, uuid)
    success, url = transformer.parseStrict(url)
    return success

def openUrl(ctx, configuration, uuid, option=''):
    url = _getAuthorizationUrl(ctx, configuration, uuid)
    service = 'com.sun.star.system.SystemShellExecute'
    ctx.ServiceManager.createInstance(service).execute(url, option, 0)

def _getAuthorizationUrl(ctx, configuration, uuid):
    main = configuration.Url.Scope.Provider.AuthorizationUrl
    parameters = urlencode(_getUrlParameters(ctx, configuration, uuid))
    return '%s?%s' % (main, parameters)

def _getUrlArguments(ctx, configuration, uuid):
    arguments = []
    parameters = _getUrlParameters(ctx, configuration, uuid)
    for key, value in parameters.items():
        arguments.append('%s=%s' % (key, value))
    return '&'.join(arguments)

def _getUrlParameters(ctx, configuration, uuid):
    parameters = _getUrlBaseParameters(configuration, uuid)
    optional = _getUrlOptionalParameters(ctx, configuration)
    option = configuration.Url.Scope.Provider.AuthorizationParameters
    parameters = _parseParameters(parameters, optional, option)
    return parameters

def _getUrlBaseParameters(configuration, uuid):
    parameters = {}
    parameters['response_type'] = 'code'
    parameters['client_id'] = configuration.Url.Scope.Provider.ClientId
    parameters['state'] = uuid
    if configuration.Url.Scope.Provider.HttpHandler:
        parameters['redirect_uri'] = configuration.Url.Scope.Provider.RedirectUri
    if configuration.Url.Scope.Provider.CodeChallenge:
        method = configuration.Url.Scope.Provider.CodeChallengeMethod
        parameters['code_challenge_method'] = method
        parameters['code_challenge'] = _getCodeChallenge(uuid + uuid, method)
    return parameters

def _getUrlOptionalParameters(ctx, configuration):
    parameters = {}
    parameters['scope'] = configuration.Url.Scope.Value
    parameters['client_secret'] = configuration.Url.Scope.Provider.ClientSecret
    parameters['current_user'] = configuration.Url.Scope.Provider.User.Id
    parameters['current_language'] = getCurrentLocale(ctx).Language
    return parameters

def _getCodeChallenge(code, method):
    if method == 'S256':
        code = hashlib.sha256(code.encode('utf-8')).digest()
        padding = {0:0, 1:2, 2:1}[len(code) % 3]
        challenge = base64.urlsafe_b64encode(code).decode('utf-8')
        code = challenge[:len(challenge)-padding]
    return code

def getTokenParameters(setting, code, codeverifier):
    parameters = _getTokenBaseParameters(setting, code, codeverifier)
    optional = _getTokenOptionalParameters(setting)
    option = setting.Url.Scope.Provider.TokenParameters
    parameters = _parseParameters(parameters, optional, option)
    return parameters

def _getTokenBaseParameters(setting, code, codeverifier):
    parameters = {}
    parameters['code'] = code
    parameters['grant_type'] = 'authorization_code'
    parameters['client_id'] = setting.Url.Scope.Provider.ClientId
    if setting.Url.Scope.Provider.HttpHandler:
        parameters['redirect_uri'] = setting.Url.Scope.Provider.RedirectUri
    if setting.Url.Scope.Provider.CodeChallenge:
        parameters['code_verifier'] = codeverifier
    return parameters

def _getTokenOptionalParameters(setting):
    parameters = {}
    parameters['scope'] = setting.Url.Scope.Values
    parameters['client_secret'] = setting.Url.Scope.Provider.ClientSecret
    return parameters

def getRefreshParameters(setting):
    parameters = _getRefreshBaseParameters(setting)
    optional = _getRefreshOptionalParameters(setting)
    option = setting.Url.Scope.Provider.TokenParameters
    parameters = _parseParameters(parameters, optional, option)
    return parameters

def _getRefreshBaseParameters(setting):
    parameters = {}
    parameters['refresh_token'] = setting.Url.Scope.Provider.User.RefreshToken
    parameters['grant_type'] = 'refresh_token'
    parameters['client_id'] = setting.Url.Scope.Provider.ClientId
    if setting.Url.Scope.Provider.CodeChallenge:
        parameters['redirect_uri'] = setting.Url.Scope.Provider.RedirectUri
    return parameters

def _getRefreshOptionalParameters(setting):
    parameters = {}
    parameters['scope'] = setting.Url.Scope.Provider.User.Scope
    parameters['client_secret'] = setting.Url.Scope.Provider.ClientSecret
    return parameters

def _parseParameters(base, optional, option):
    options = json.loads(option)
    for key, value in options.items():
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
