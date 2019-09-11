#!
# -*- coding: utf-8 -*-

#from __futur__ import absolute_import

import uno

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .unotools import getCurrentLocale

from .oauth2lib import NoOAuth2

from .requests.compat import urlencode

import json
import base64
import hashlib

g_advance_to = 0 # 0 to disable
g_wizard_paths = ((1, 2, 3, 5), (1, 2, 4, 5), (1, 5))
g_identifier = 'com.gmail.prrvchr.extensions.OAuth2OOo'
g_refresh_overlap = 10 # must be positive, in second


def getActivePath(configuration):
    if configuration.Url.Scope.Authorized:
        activepath = 2
    elif configuration.Url.Scope.Provider.HttpHandler:
        activepath = 0
    else:
        activepath = 1
    return activepath

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

def openUrl(ctx, url, option=''):
    service = 'com.sun.star.system.SystemShellExecute'
    ctx.ServiceManager.createInstance(service).execute(url, option, 0)

def getAuthorizationUrl(ctx, configuration, uuid):
    main = configuration.Url.Scope.Provider.AuthorizationUrl
    parameters = urlencode(_getUrlParameters(ctx, configuration, uuid))
    return '%s?%s' % (main, parameters)

def updatePageTokenUI(window, configuration, strings):
    enabled = configuration.Url.Scope.Authorized
    if enabled:
        scope = configuration.Url.Scope.Provider.User.Scope
        refresh = configuration.Url.Scope.Provider.User.RefreshToken
        access = configuration.Url.Scope.Provider.User.AccessToken
        expire = configuration.Url.Scope.Provider.User.ExpiresIn
    else:
        scope = strings.resolveString('PageWizard5.Label2.Label')
        refresh = strings.resolveString('PageWizard5.Label4.Label')
        access = strings.resolveString('PageWizard5.Label6.Label')
        expire = strings.resolveString('PageWizard5.Label8.Label')
    window.getControl('Label2').Text = scope
    window.getControl('Label4').Text = refresh
    window.getControl('Label6').Text = access
    window.getControl('Label8').Text = expire
    window.getControl('CommandButton1').Model.Enabled = enabled
    window.getControl('CommandButton2').Model.Enabled = enabled
    window.getControl('CommandButton3').Model.Enabled = enabled

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

def getResponseFromRequest(logger, session, url, data, timeout):
    response = {}
    try:
        with session as s:
            with s.post(url, data=data, timeout=timeout, auth=NoOAuth2()) as r:
                if r.status_code == s.codes.ok:
                    response = r.json()
                else:
                    error = "ERROR: %s" % r.text
                    logger.logp(SEVERE, 'oauth2tools', 'getResponseFromRequest', error)
    except Exception as e:
        error = "ERROR: %s" % e
        logger.logp(SEVERE, 'oauth2tools', 'getResponseFromRequest', error)
    return response

def registerTokenFromResponse(configuration, response):
    token = getTokenFromResponse(configuration, response)
    return token != ''

def getRefreshToken(logger, session, configuration):
    url = configuration.Url.Scope.Provider.TokenUrl
    data = getRefreshParameters(configuration)
    message = "Make Http Request: %s?%s" % (url, data)
    logger.logp(INFO, 'oauth2tools', 'refreshToken', message)
    timeout = configuration.Timeout
    response = getResponseFromRequest(logger, session, url, data, timeout)
    token = getTokenFromResponse(configuration, response)
    if token:
        configuration.Url.Scope.Provider.User.commit()
    return token

def getTokenFromResponse(configuration, response):
    refresh = response.get('refresh_token', None)
    if refresh:
        configuration.Url.Scope.Provider.User.RefreshToken = refresh
    expires = response.get('expires_in', None)
    if expires:
        configuration.Url.Scope.Provider.User.ExpiresIn = expires
    token = response.get('access_token', '')
    if token:
        configuration.Url.Scope.Provider.User.AccessToken = token
        scope = configuration.Url.Scope.Value
        configuration.Url.Scope.Provider.User.Scope = scope
        configuration.Url.Scope.Provider.User.NeverExpires = expires is None
        #configuration.Url.Scope.Provider.User.commit()
    return token

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
    parameters['scope'] = setting.Url.Scope.Value
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
