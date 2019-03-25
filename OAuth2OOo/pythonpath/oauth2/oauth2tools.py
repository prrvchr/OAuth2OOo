#!
# -*- coding: utf-8 -*-

import uno

from .unotools import createService
from .unotools import getCurrentLocale
from .requests.compat import urlencode

import base64
import hashlib

g_wizard_paths = ((1, 2, 3), (1, 2, 4))
g_identifier = 'com.gmail.prrvchr.extensions.OAuth2OOo'

def getAuthorizationUrl(ctx, configuration, code, state):
    success, main, parameters = _getUrlMainAndParameters(ctx, configuration)
    parameters = urlencode(_getUrlParameters(ctx, configuration, code, state, parameters))
    return '%s?%s' % (main, parameters)

def getAuthorizationStr(ctx, configuration, code, state):
    presentation = ''
    success, main, parameters = _getUrlMainAndParameters(ctx, configuration)
    if success:
        transformer = ctx.ServiceManager.createInstance('com.sun.star.util.URLTransformer')
        url = uno.createUnoStruct('com.sun.star.util.URL')
        url.Complete = '%s?%s' % (main, _getUrlArguments(ctx, configuration, code, state, parameters))
        success, url = transformer.parseStrict(url)
        if success:
            presentation = transformer.getPresentation(url, False)
    return presentation

def getActivePath(configuration):
    return 0 if configuration.Url.Provider.HttpHandler else 1

def checkUrl(ctx, configuration, code, state):
    success, main, parameters = _getUrlMainAndParameters(ctx, configuration)
    if success:
        transformer = ctx.ServiceManager.createInstance('com.sun.star.util.URLTransformer')
        url = uno.createUnoStruct('com.sun.star.util.URL')
        url.Complete = '%s?%s' % (main, _getUrlArguments(ctx, configuration, code, state, parameters))
        success, url = transformer.parseStrict(url)
    return success

def openUrl(ctx, configuration, code, state, option=''):
    url = getAuthorizationUrl(ctx, configuration, code, state)
    message = getAuthorizationStr(ctx, configuration, code, state)
    service = 'com.sun.star.system.SystemShellExecute'
    ctx.ServiceManager.createInstance(service).execute(url, option, 0)

def _getUrlMainAndParameters(ctx, configuration):
    main = configuration.Url.Provider.AuthorizationUrl
    parameters = {}
    transformer = ctx.ServiceManager.createInstance('com.sun.star.util.URLTransformer')
    url = uno.createUnoStruct('com.sun.star.util.URL')
    url.Complete = main
    success, url = transformer.parseStrict(url)
    if success:
        main = url.Main
        parameters = _getParametersFromArguments(url.Arguments)
    return success, main, parameters

def _getParametersFromArguments(arguments):
    parameters = {}
    for arg in arguments.split('&'):
        parts = arg.split('=')
        if len(parts) > 1:
            name = unquote(parts[0]).strip()
            value = unquote('='.join(parts[1:])).strip()
            parameters[name] = value
    return parameters

def _getUrlParameters(ctx, configuration, code, state, parameters={}):
    parameters['client_id'] = configuration.Url.Provider.ClientId
    parameters['redirect_uri'] = configuration.Url.Provider.RedirectUri
    parameters['response_type'] = 'code'
    parameters['response_mode'] = 'query'
    parameters['scope'] = configuration.Url.Provider.Scope.Value
#        parameters['access_type'] = 'offline'
    if configuration.Url.Provider.CodeChallenge:
        method = configuration.Url.Provider.CodeChallengeMethod
        parameters['code_challenge_method'] = method
        parameters['code_challenge'] = _getCodeChallenge(code, method)
    if configuration.Url.Provider.ClientSecret:
        parameters['client_secret'] = configuration.Url.Provider.ClientSecret
    parameters['login_hint'] = configuration.Url.Provider.Scope.User.Id
    parameters['prompt'] = 'consent'
    parameters['hl'] = getCurrentLocale(ctx).Language
    parameters['state'] = state
    return parameters

def _getUrlArguments(ctx, configuration, code, state, parameters={}):
    arguments = []
    parameters = _getUrlParameters(ctx, configuration, code, state, parameters)
    for key, value in parameters.items():
        arguments.append('%s=%s' % (key, value))
    return '&'.join(arguments)

def _getCodeChallenge(code, method):
    if method == 'S256':
        code = hashlib.sha256(code.encode('utf-8')).digest()
        padding = {0:0, 1:2, 2:1}[len(code) % 3]
        challenge = base64.urlsafe_b64encode(code).decode('utf-8')
        code = challenge[:len(challenge)-padding]
    return code
