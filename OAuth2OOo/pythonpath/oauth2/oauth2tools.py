#!
# -*- coding: utf-8 -*-

import uno

from .oauth2lib import JsonHook
from .unotools import createService
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
    return 0 if configuration.Url.Provider.HttpHandler else 1

def getAuthorizationStr(ctx, configuration, uuid):
    main = configuration.Url.Provider.AuthorizationUrl
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
    main = configuration.Url.Provider.AuthorizationUrl
    parameters = urlencode(_getUrlParameters(ctx, configuration, uuid))
    return '%s?%s' % (main, parameters)

def _getUrlArguments(ctx, configuration, uuid):
    arguments = []
    parameters = _getUrlParameters(ctx, configuration, uuid)
    for key, value in parameters.items():
        arguments.append('%s=%s' % (key, value))
    return '&'.join(arguments)

def _getUrlParameters(ctx, configuration, uuid):
    parameters = getUrlBaseParameters(configuration, uuid)
    optional = getUrlOptionalParameters(ctx, configuration)
    options = configuration.Url.Provider.AuthorizationParameters
    update = getUpdateOption(options, parameters, optional)
    parameters.update(update)
    return parameters

def getUrlBaseParameters(configuration, uuid):
    parameters = {}
    parameters['response_type'] = 'code'
    parameters['client_id'] = configuration.Url.Provider.ClientId
    parameters['state'] = uuid
    if configuration.Url.Provider.HttpHandler:
        parameters['redirect_uri'] = configuration.Url.Provider.RedirectUri
    if configuration.Url.Provider.CodeChallenge:
        method = configuration.Url.Provider.CodeChallengeMethod
        parameters['code_challenge_method'] = method
        parameters['code_challenge'] = _getCodeChallenge(uuid + uuid, method)
    return parameters

def getUrlOptionalParameters(ctx, configuration):
    parameters = {}
    parameters['scope'] = configuration.Url.Provider.Scope.Value
    parameters['client_secret'] = configuration.Url.Provider.ClientSecret
    parameters['current_user'] = configuration.Url.Provider.Scope.User.Id
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
    data = getTokenBaseParameters(setting, code, codeverifier)
    optional = getTokenOptionalParameters(setting)
    options = setting.Url.Provider.TokenParameters
    update = getUpdateOption(options, data, optional)
    data.update(update)
    return data

def getTokenBaseParameters(setting, code, codeverifier):
    parameters = {}
    parameters['code'] = code
    parameters['grant_type'] = 'authorization_code'
    parameters['client_id'] = setting.Url.Provider.ClientId
    if setting.Url.Provider.HttpHandler:
        parameters['redirect_uri'] = setting.Url.Provider.RedirectUri
    if setting.Url.Provider.CodeChallenge:
        parameters['code_verifier'] = codeverifier
    return parameters

def getTokenOptionalParameters(setting):
    parameters = {}
    parameters['scope'] = setting.Url.Provider.Scope.Values
    parameters['client_secret'] = setting.Url.Provider.ClientSecret
    return parameters

def getRefreshParameters(setting):
    data = getRefreshBaseParameters(setting)
    optional = getRefreshOptionalParameters(setting)
    options = setting.Url.Provider.TokenParameters
    update = getUpdateOption(options, data, optional)
    data.update(update)
    return data

def getRefreshBaseParameters(setting):
    parameters = {}
    parameters['refresh_token'] = setting.Url.Provider.Scope.User.RefreshToken
    parameters['grant_type'] = 'refresh_token'
    parameters['client_id'] = setting.Url.Provider.ClientId
    if setting.Url.Provider.CodeChallenge:
        parameters['redirect_uri'] = setting.Url.Provider.RedirectUri
    return parameters

def getRefreshOptionalParameters(setting):
    parameters = {}
    parameters['scope'] = setting.Url.Provider.Scope.User.Scope
    parameters['client_secret'] = setting.Url.Provider.ClientSecret
    return parameters

def getUpdateOption(option, data, optional):
    options = JsonHook(data, optional)
    update = json.loads(option, object_pairs_hook=options.hook)
    return update
