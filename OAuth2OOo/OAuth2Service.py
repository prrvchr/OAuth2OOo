#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.lang import XInitialization
from com.sun.star.task import XInteractionHandler2
from com.sun.star.auth import XOAuth2Service
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE
from com.sun.star.ui.dialogs.ExecutableDialogResults import OK
from com.sun.star.ui.dialogs.ExecutableDialogResults import CANCEL

from com.sun.star.uno import Exception as UnoException

from oauth2 import OAuth2OOo
from oauth2 import NoOAuth2
from oauth2 import Enumerator
from oauth2 import InputStream
from oauth2 import Uploader
from oauth2 import KeyMap
from oauth2 import DialogHandler
from oauth2 import getSessionMode
from oauth2 import execute
from oauth2 import getLogger
from oauth2 import getDialog
from oauth2 import getStringResource

from oauth2 import OAuth2Setting
from oauth2 import WizardController
from oauth2 import createService
from oauth2 import getConfiguration
from oauth2 import getRefreshToken
from oauth2 import g_identifier
from oauth2 import g_wizard_paths
from oauth2 import g_refresh_overlap

import sys
import time
from oauth2 import requests

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Service' % g_identifier


class OAuth2Service(unohelper.Base,
                    XServiceInfo,
                    XInitialization,
                    XInteractionHandler2,
                    XOAuth2Service):
    def __init__(self, ctx):
        self.ctx = ctx
        logger = getLogger(self.ctx)
        self.configuration = getConfiguration(self.ctx, g_identifier, True)
        self.Setting = OAuth2Setting(self.ctx, logger)
        self.Session = self._getSession()
        self._Url = ''
        self._Provider = KeyMap()
        self._Users = None
        self._UserName = ''
        self._User = KeyMap()
        self.Parent = None
        self.Logger = logger
        self.Error = ''
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo')
        self._checkSSL()

    @property
    def ResourceUrl(self):
        return self._Url
    @property
    def ProviderName(self):
        return self._Provider.getDefaultValue('Name', 'Test')
    @property
    def TokenUrl(self):
        return self._Provider.getDefaultValue('TokenUrl', '')
    @property
    def TokenParameters(self):
        return self._Provider.getDefaultValue('TokenParameters', '')
    @property
    def RequiredScopes(self):
        return self._Provider.getDefaultValue('RequiredScopes', ())
    @property
    def IsAuthorized(self):
        scopes = self.RequiredScopes
        authorized = len(scopes) > 0
        for scope in scopes:
            if scope not in self.AcquiredScopes:
                authorized = False
                break
        return authorized
    @property
    def HasExpired(self):
        expired = False
        if not self.NeverExpires:
            now = int(time.time())
            expiresin = max(0, self.TimeStamp - now)
            expired = expiresin < g_refresh_overlap
        return expired
    @property
    def UserName(self):
        return self._UserName
    @property
    def AcquiredScopes(self):
        return self._User.getDefaultValue('Scopes', ())
    @property
    def AccessToken(self):
        return self._User.getDefaultValue('AccessToken', '')
    @property
    def TimeStamp(self):
        return self._User.getDefaultValue('TimeStamp', 0)
    @property
    def NeverExpires(self):
        return self._User.getDefaultValue('NeverExpires', False)
    @property
    def Timeout(self):
        return self.Setting.Timeout

    # XInitialization
    def initialize(self, properties):
        for property in properties:
            print("OAuth2Service.initialize() %s: %s"  % (property.Name, property.Value))
            if property.Name == 'Parent':
                self.Parent = property.Value

    # XInteractionHandler2, XInteractionHandler
    def handle(self, interaction):
        self.handleInteractionRequest(interaction)
    def handleInteractionRequest(self, interaction):
        try:
            handler = DialogHandler()
            dialog = getDialog(self.ctx, self.Parent, handler, 'OAuth2OOo', 'UserDialog')
            # TODO: interaction.getRequest() does not seem to be functional under LibreOffice !!!
            # dialog.setTitle(interaction.getRequest().Message)
            print("OAuth2Service.handleInteractionRequest() 4 %s" % interaction.getProviderName())
            self._initUserDialog(dialog, interaction.getProviderName())
            status = dialog.execute()
            approved = status == OK
            continuation = interaction.getContinuations()[status]
            if approved:
                username = dialog.getControl('TextField1').Model.Text
                continuation.setUserName(username)
            continuation.select()
            dialog.dispose()
            return approved
        except Exception as e:
            print("OAuth2Service.handleInteractionRequest() ERROR: %s - %s" % (e, traceback.print_exc()))

    def _initUserDialog(self, dialog, name):
        title = self.stringResource.resolveString('UserDialog.Title')
        label = self.stringResource.resolveString('UserDialog.Label1.Label')
        dialog.setTitle(title % name)
        dialog.getControl('Label1').Text = label % name

    # XOAuth2Service
    def initializeSession(self, url, name):
        if self.initializeUrl(url):
            return self.initializeUser(name)
        return False

    def initializeUrl(self, url):
        try:
            print("OAuth2Service.initializeUrl() 1")
            self._Url = url
            self._Provider = KeyMap()
            self._Users = None
            provider = None
            providername = ''
            requiredscopes = ()
            tokenurl = ''
            tokenparameters = ''
            urls = self.configuration.getByName('Urls')
            if not urls.hasByName(self._Url):
                self.Error = "Can't retrieve ResourceUrl: %s from Configuration" % self._Url
                return False
            url = urls.getByName(self._Url)
            if not url.hasByName('Scope'):
                self.Error = "Can't retrieve Scope for ResourceUrl: %s from Configuration" % self._Url
                return False
            scopename = url.getByName('Scope')
            scopes = self.configuration.getByName('Scopes')
            if not scopes.hasByName(scopename):
                self.Error = "Can't retrieve Scope: %s from Configuration" % scopename
                return False
            scope = scopes.getByName(scopename)
            if not scope.hasByName('Provider'):
                self.Error = "Can't retrieve Provider for Scope: %s from Configuration" % scopename
                return False
            providername = scope.getByName('Provider')
            self._Provider.insertValue('Name', providername)
            print("OAuth2Service.initializeUrl() 2 %s" % providername)
            if not scope.hasByName('Values'):
                self.Error = "Can't retrieve Values for Scope: %s from Configuration" % scopename
                return False
            requiredscopes = scope.getByName('Values')
            self._Provider.insertValue('RequiredScopes', requiredscopes)
            providers = self.configuration.getByName('Providers')
            if not providers.hasByName(providername):
                self.Error = "Can't retrieve Provider: %s from Configuration" % providername
                return False
            provider = providers.getByName(providername)
            print("OAuth2Service.initializeUrl() 3")
            if provider.hasByName('ClientId'):
                clientid = provider.getByName('ClientId')
                self._Provider.insertValue('ClientId', clientid)
            if provider.hasByName('ClientSecret'):
                clientsecret = provider.getByName('ClientSecret')
                self._Provider.insertValue('ClientSecret', clientsecret)
            if provider.hasByName('TokenUrl'):
                tokenurl = provider.getByName('TokenUrl')
                self._Provider.insertValue('TokenUrl', tokenurl)
            if provider.hasByName('TokenParameters'):
                tokenparameters = provider.getByName('TokenParameters')
                self._Provider.insertValue('TokenParameters', tokenparameters)
            if provider.hasByName('Users'):
                self._Users = provider.getByName('Users')
            init = provider is not None
            print("OAuth2Service.initializeUrl() 4 %s" % (init, ))
            return provider is not None
            #self.Setting.Url.Id = url
        except Exception as e:
            print("OAuth2Service.initializeUrl() ERROR: %s - %s" % (e, traceback.print_exc()))

    def initializeUser(self, name):
        print("OAuth2Service.initializeUser() 1 %s" % name)
        if self._initializeUser(name):
            print("OAuth2Service.initializeUser() 2")
            return self._isAuthorized()
        return False

    def getKeyMap(self):
        return KeyMap()

    def getSessionMode(self, host):
        return getSessionMode(self.ctx, host)

    def getAuthorization(self, url, username, close=True):
        authorized = False
        msg = "Wizard Loading ..."
        controller = WizardController(self.ctx, self.Setting, self.Session, url, username, close)
        print("OAuth2Service.getAuthorizationCode() 1")
        msg += " Done ..."
        if controller.Wizard.execute() == OK:
            msg +=  " Retrieving Authorization Code ..."
            print("OAuth2Service._getAuthorizationCode() 2")
            if controller.Error:
                print("OAuth2Service._getAuthorizationCode() 3")
                msg += " ERROR: cant retrieve Authorization Code: %s" % controller.Error
            else:
                msg += " Done"
                authorized = self.initializeUrl(controller.ResourceUrl)
                authorized &= self.initializeUser(controller.UserName)
                #self.ResourceUrl = controller.ResourceUrl
                #self.UserName = controller.UserName
                print("OAuth2Service._getAuthorizationCode() 4")
        else:
            print("OAuth2Service._getAuthorizationCode() 5")
            msg +=  " ERROR: Wizard as been aborted"
            controller.Server.cancel()
        controller.Wizard.DialogWindow.dispose()
        self.Logger.logp(INFO, 'OAuth2Service', 'getAuthorization()', msg)
        return authorized

    def getToken(self, format=''):
        print("OAuth2Service.getToken() 1")
        level = INFO
        msg = "Request Token ... "
        if not self._isAuthorized():
            print("OAuth2Service.getToken() 2")
            level = SEVERE
            msg += "ERROR: Cannot InitializeSession()..."
            token = ''
        elif self.HasExpired:
            print("OAuth2Service.getToken() 3")
            token = getRefreshToken(self.Logger, self.Session, self._Provider, self._User, self.Timeout)
            if token.IsPresent:
                self._User = token.Value
                token = self.AccessToken
                msg += "Refresh needed ... Done"
            else:
                token = ''
                print("OAuth2Service.getToken() 4")
        else:
            print("OAuth2Service.getToken() 5")
            token = self.AccessToken
            msg += "Get from configuration ... Done"
        self.Logger.logp(level, 'OAuth2Service', 'getToken()', msg)
        if format:
            token = format % token
        return token

    def execute(self, parameter):
        response, self.Error = execute(self.Session, parameter, self.Timeout)
        return response

    def getEnumerator(self, parameter):
        return Enumerator(self.Session, parameter, self.Timeout, self.Logger)

    def getInputStream(self, parameter, chunk, buffer):
        return InputStream(self.Session, parameter, chunk, buffer, self.Timeout, self.Logger)

    def getUploader(self, datasource):
        return Uploader(self.ctx, self.Session, datasource, self.Timeout)

    def logp(self, level, source, method, message):
        if self.Logger.isLoggable(level):
            self.Logger.logp(level, source, method, message)

    def _getSession(self):
        if sys.version_info[0] < 3:
            requests.packages.urllib3.disable_warnings()
        session = requests.Session()
        session.auth = OAuth2OOo(self)
        session.codes = requests.codes
        return session

    def _checkSSL(self):
        try:
            import ssl
        except ImportError:
            self.Error = "Can't load module: 'ssl.py'. Your Python SSL configuration is broken..."

    def _isAuthorized(self):
        print("OAuth2Service._isAuthorized() 1")
        msg = "OAuth2 initialization ..."
        if not self.IsAuthorized:
            msg += " Done ... AuthorizationCode needed ..."
            print("OAuth2Service._isAuthorized() 2")
            if not self.getAuthorization(self.ResourceUrl, self.UserName, True):
                print("OAuth2Service._isAuthorized() 3")
                msg += " ERROR: Wizard Aborted!!!"
                self.Logger.logp(SEVERE, 'OAuth2Service', '_isAuthorized()', msg)
                return False
        msg += " Done"
        self.Logger.logp(INFO, 'OAuth2Service', '_isAuthorized()', msg)
        return True

    def _isAuthorized1(self, user):
        print("OAuth2Service._isAuthorized() 1")
        msg = "OAuth2 initialization ..."
        if self._hasProviderUser(user):
            return True
        msg += " Done ... AuthorizationCode needed ..."
        print("OAuth2Service._isAuthorized() 2")
        if self.getAuthorization(self._Url, user, True):
            print("OAuth2Service._isAuthorized() 3")
            msg += " Done"
            self.Logger.logp(SEVERE, 'OAuth2Service', '_isAuthorized()', msg)
            return True
        msg += " ERROR: Wizard Aborted!!!"
        self.Logger.logp(INFO, 'OAuth2Service', '_isAuthorized()', msg)
        return False

    def _initializeUser(self, username):
        self._UserName = username
        self._User = KeyMap()
        if self._Users.hasByName(username):
            user = self._Users.getByName(username)
            if user.hasByName('AccessToken'):
                access = user.getByName('AccessToken')
                self._User.insertValue('AccessToken', access)
            if user.hasByName('RefreshToken'):
                refresh = user.getByName('RefreshToken')
                self._User.insertValue('RefreshToken', refresh)
            if user.hasByName('TimeStamp'):
                timestamp = user.getByName('TimeStamp')
                self._User.insertValue('TimeStamp', timestamp)
            if user.hasByName('NeverExpires'):
                neverexpires = user.getByName('NeverExpires')
                self._User.insertValue('NeverExpires', neverexpires)
            if user.hasByName('Scopes'):
                scopes = user.getByName('Scopes')
                self._User.insertValue('Scopes', scopes)
        return self._UserName != ''

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OAuth2Service,
                                         g_ImplementationName,
                                        (g_ImplementationName,))
