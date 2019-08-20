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

from oauth2 import OAuth2Configuration
from oauth2 import WizardController
from oauth2 import createService
from oauth2 import getTokenParameters
from oauth2 import getRefreshParameters
from oauth2 import g_identifier
from oauth2 import g_wizard_paths

import sys
import certifi
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
        self.Setting = OAuth2Configuration(self.ctx)
        self.Session = self._getSession()
        self.Error = ''
        self.Parent = None
        self.Logger = getLogger(self.ctx)
        self._checkSSL()

    @property
    def ResourceUrl(self):
        return self.Setting.Url.Id
    @ResourceUrl.setter
    def ResourceUrl(self, url):
        self.Setting.Url.Id = url
    @property
    def UserName(self):
        return self.Setting.Url.Scope.Provider.User.Id
    @UserName.setter
    def UserName(self, name):
        self.Setting.Url.Scope.Provider.User.Id = name
    @property
    def Timeout(self):
        return self.Setting.Timeout

    # XInitialization
    def initialize(self, properties):
        for property in properties:
            if property.Name == 'Parent':
                self.Parent = property.Value

    # XInteractionHandler2, XInteractionHandler
    def handle(self, interaction):
        self.handleInteractionRequest(interaction)
    def handleInteractionRequest(self, interaction):
        handler = DialogHandler()
        dialog = getDialog(self.ctx, self.Parent, handler, 'OAuth2OOo', 'UserDialog')
        # TODO: interaction.getRequest() does not seem to be functional under LibreOffice !!!
        # dialog.setTitle(interaction.getRequest().Message)
        status = dialog.execute()
        approved = status == OK
        continuation = interaction.getContinuations()[status]
        if approved:
            username = dialog.getControl('TextField1').Model.Text
            continuation.setUserName(username)
        continuation.select()
        dialog.dispose()
        return approved

    # XOAuth2Service
    def initializeSession(self, url):
        self.Setting.Url.Id = url

    def initializeUser(self, name):
        if not name or not self.ResourceUrl:
            return False
        self.UserName = name
        return self._isAuthorized()

    def getKeyMap(self):
        return KeyMap()

    def getSessionMode(self, host):
        return getSessionMode(self.ctx, host)

    def getAuthorization(self, url, username):
        code = None
        msg = "Wizard Loading ..."
        wizard = createService(self.ctx, 'com.sun.star.ui.dialogs.Wizard')
        controller = WizardController(self.ctx, wizard, url, username)
        arguments = ((uno.Any('[][]short', (g_wizard_paths)), controller), )
        uno.invoke(wizard, 'initialize', arguments)
        print("OAuth2Service.getAuthorizationCode() 1")
        state = wizard.execute()
        msg += " Done ..."
        if state:
            msg +=  " Retrieving Authorization Code ..."
            print("OAuth2Service._getAuthorizationCode() 2")
            if controller.AuthorizationCode.IsPresent:
                msg += " Done"
                code = controller.AuthorizationCode.Value
                print("OAuth2Service._getAuthorizationCode() 3")
            else:
                msg += " ERROR: cant retrieve Authorization Code"
        else:
            msg +=  " ERROR: Wizard as been aborted"
        #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
        #mri.inspect(controller.Handler.Wizard)
        wizard.DialogWindow.dispose()
        controller.Server.cancel()
        if code is None:
            self.Logger.logp(SEVERE, 'OAuth2Service', 'getAuthorization()', msg)
            return False
        msg += " Done ... Request Token ..."
        if not self._registerTokens(code, controller.CodeVerifier):
            msg += " ERROR: cant retrieve Token"
            self.Logger.logp(SEVERE, 'OAuth2Service', 'getAuthorization()', msg)
            return False
        level = INFO
        msg += " Done"
        controller.Configuration.commit()
        self.ResourceUrl = controller.ResourceUrl
        self.UserName = controller.UserName
        self.Logger.logp(INFO, 'OAuth2Service', 'getAuthorization()', msg)
        return True

    def getToken(self, format=''):
        print("OAuth2Service.getToken() 1")
        level = INFO
        msg = "Request Token ... "
        if not self._isAuthorized():
            print("OAuth2Service.getToken() 2")
            level = SEVERE
            msg += "ERROR: Cannot InitializeSession()..."
            token = ''
        elif self.Setting.Url.Scope.Provider.User.HasExpired:
            print("OAuth2Service.getToken() 3")
            token = self._refreshToken()
            msg += "Refresh needed ... Done"
        else:
            print("OAuth2Service.getToken() 4")
            token = self.Setting.Url.Scope.Provider.User.AccessToken
            msg += "Get from configuration ... Done"
        self.Logger.logp(level, 'OAuth2Service', 'getToken()', msg)
        if format:
            token = format % token
        return token

    def execute(self, parameter):
        return execute(self.Session, parameter, self.Timeout, self.Logger)

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
        if not self.Setting.Url.Scope.Authorized:
            msg += " Done ... AuthorizationCode needed ..."
            print("OAuth2Service._isAuthorized() 2")
            if not self.getAuthorization(self.ResourceUrl, self.UserName):
                print("OAuth2Service._isAuthorized() 3")
                msg += " ERROR: Wizard Aborted!!!"
                self.Logger.logp(SEVERE, 'OAuth2Service', '_isAuthorized()', msg)
                return False
        msg += " Done"
        self.Logger.logp(INFO, 'OAuth2Service', '_isAuthorized()', msg)
        return True

    def _getAuthorizationCode(self, controller):
        print("OAuth2Service._getAuthorizationCode() 1")
        code = None
        msg = "Wizard Loading ..."
        state = controller.Wizard.execute()
        msg += " Done ..."
        if state:
            msg +=  " Retrieving Authorization Code ..."
            print("OAuth2Service._getAuthorizationCode() 2")
            if controller.AuthorizationCode.IsPresent:
                msg += " Done"
                code = controller.AuthorizationCode.Value
                print("OAuth2Service._getAuthorizationCode() 3")
            else:
                msg += " ERROR: cant retrieve Authorization Code"
        else:
            msg +=  " ERROR: Wizard as been aborted"
        #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
        #mri.inspect(controller.Handler.Wizard)
        controller.Wizard.DialogWindow.dispose()
        controller.Server.cancel()
        return code, msg

    def _registerTokens(self, code, codeverifier):
        url = self.Setting.Url.Scope.Provider.TokenUrl
        data = getTokenParameters(self.Setting, code, codeverifier)
        message = "Make Http Request: %s?%s" % (url, data)
        self.Logger.logp(INFO, 'OAuth2Service', '_registerTokens', message)
        response = self._getResponseFromRequest(url, data)
        return self._registerTokenFromResponse(response)

    def _refreshToken(self):
        url = self.Setting.Url.Scope.Provider.TokenUrl
        data = getRefreshParameters(self.Setting)
        message = "Make Http Request: %s?%s" % (url, data)
        self.Logger.logp(INFO, 'OAuth2Service', '_refreshToken', message)
        response = self._getResponseFromRequest(url, data)
        return self._getTokenFromResponse(response)

    def _getCertificat(self):
        verify = True
        if sys.version_info[0] < 3:
            verify = certifi.old_where()
        return verify

    def _getResponseFromRequest(self, url, data):
        response = {}
        #verify = self._getCertificat()
        try:
            with self.Session as s:
                with s.post(url, data=data, timeout=self.Timeout, auth=NoOAuth2()) as r:
                    if r.status_code == s.codes.ok:
                        response = r.json()
                    else:
                        msg = "ERROR: %s" % r.text
                        self.Logger.logp(SEVERE, 'OAuth2Service', '_getResponseFromRequest', msg)
        except Exception as e:
            self.Logger.logp(SEVERE, 'OAuth2Service', '_getResponseFromRequest', "ERROR: %s" % e)
        return response

    def _registerTokenFromResponse(self, response):
        token = self._getTokenFromResponse(response)
        return token != ''

    def _getTokenFromResponse(self, response):
        refresh = response.get('refresh_token', None)
        if refresh:
            self.Setting.Url.Scope.Provider.User.RefreshToken = refresh
        expires = response.get('expires_in', None)
        if expires:
            self.Setting.Url.Scope.Provider.User.ExpiresIn = expires
        token = response.get('access_token', '')
        if token:
            self.Setting.Url.Scope.Provider.User.AccessToken = token
            scope = self.Setting.Url.Scope.Values
            self.Setting.Url.Scope.Provider.User.Scope = scope
            self.Setting.Url.Scope.Provider.User.NeverExpires = expires is None
            self.Setting.Url.Scope.Provider.User.commit()
            level = INFO
        else:
            level = SEVERE
        self.Logger.logp(level, 'OAuth2Service', '_getTokenFromResponse', "%s" % response)
        return token

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
