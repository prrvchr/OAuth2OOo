#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardController
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .unolib import PropertySet

from .wizardconfiguration import WizardConfiguration
from .wizardhandler import WizardHandler
from .wizardserver import WizardServer
from .wizardpage import WizardPage

from .unotools import createService
from .unotools import generateUuid
from .unotools import getCurrentLocale
from .unotools import getProperty
from .unotools import getStringResource
from .unotools import getContainerWindow
from .unotools import getDialogUrl

from .logger import getLogger

from .oauth2tools import getActivePath
from .oauth2tools import getTokenParameters
from .oauth2tools import getResponseFromRequest
from .oauth2tools import registerTokenFromResponse
from .oauth2tools import g_identifier
from .oauth2tools import g_wizard_paths
from .oauth2tools import g_advance_to

import traceback


class WizardController(unohelper.Base,
                       PropertySet,
                       XWizardController):
    def __init__(self, ctx, session, url, username, path):
        self.ctx = ctx
        self.Session = session
        self.Configuration = WizardConfiguration(self.ctx)
        self.ResourceUrl = url
        self.UserName = username
        self.AuthorizationCode = uno.createUnoStruct('com.sun.star.beans.Optional<string>')
        self.Server = WizardServer(self.ctx)
        self.Uuid = generateUuid()
        self.advanceTo = g_advance_to # 0 to disable
        self.Wizard = createService(self.ctx, 'com.sun.star.ui.dialogs.Wizard')
        self.Path = path
        arguments = ((uno.Any('[][]short', (g_wizard_paths[path])), self), )
        uno.invoke(self.Wizard, 'initialize', arguments)
        self.Error = ''
        self.Logger = getLogger(self.ctx)
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo')
        service = 'com.sun.star.awt.ContainerWindowProvider'
        self.provider = self.ctx.ServiceManager.createInstanceWithContext(service, self.ctx)

    @property
    def ResourceUrl(self):
        return self.Configuration.Url.Id
    @ResourceUrl.setter
    def ResourceUrl(self, url):
        self.Configuration.Url.Id = url
    @property
    def UserName(self):
        return self.Configuration.Url.Scope.Provider.User.Id
    @UserName.setter
    def UserName(self, name):
        self.Configuration.Url.Scope.Provider.User.Id = name
    @property
    def ActivePath(self):
        return getActivePath(self.Configuration)
    @property
    def CodeVerifier(self):
        return self.Uuid + self.Uuid

    # XWizardController
    def createPage(self, parent, id):
        try:
            print("WizardController.createPage() %s" % id)
            msg = "PageId: %s ..." % id
            handler = WizardHandler(self.ctx, self.Configuration, self.Wizard)
            url = getDialogUrl('OAuth2OOo', 'PageWizard%s' % id)
            window = self.provider.createContainerWindow(url, '', parent, handler)
            #window = getContainerWindow(self.ctx, parent, handler, 'OAuth2OOo', xdl)
            #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
            #mri.inspect(handler)
            page = WizardPage(self.ctx,
                              self.Configuration,
                              id,
                              window,
                              self.Uuid,
                              self.AuthorizationCode)
            #if id == 3:
            #    self.Server.addCallback(page, self)
            msg += " Done"
            self.Logger.logp(INFO, "WizardController", "createPage()", msg)
            print("WizardController.createPage() %s Done" % id)
            return page
        except Exception as e:
            print("WizardController.createPage() ERROR: %s - %s" % (e, traceback.print_exc()))
    def getPageTitle(self, id):
        title = self.stringResource.resolveString('PageWizard%s.Step' % (id, ))
        return title
    def canAdvance(self):
        return self.Wizard.CurrentPage.canAdvance()
    def onActivatePage(self, id):
        print("WizardController.onActivatePage(): %s" % id)
        msg = "PageId: %s..." % id
        title = self.stringResource.resolveString('PageWizard%s.Title' % (id, ))
        self.Wizard.setTitle(title)
        backward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.PREVIOUS')
        forward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.NEXT')
        finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.FINISH')
        self.Wizard.enableButton(finish, False)
        if id == 1:
            pass
            #self.Wizard.activatePath(self.ActivePath, True)
            #self.Wizard.updateTravelUI()
        #travel = self.advanceTo - id
        #if not self.canAdvance():
        #    self.advanceTo = 0
        #elif travel > 0:
        #    if travel == 1:
        #        self.advanceTo = 0
        #    self.Wizard.travelNext()
        elif id == 3:
            self.Server.addCallback(self.Wizard.CurrentPage, self)
            self.Wizard.enableButton(backward, False)
            self.Wizard.enableButton(forward, False)
            self.Wizard.enableButton(finish, False)
        elif id == 4:
            self.Wizard.enableButton(backward, False)
            self.Wizard.enableButton(forward, False)
            self.Wizard.enableButton(finish, False)
        msg += " Done"
        self.Logger.logp(INFO, "WizardController", "onActivatePage()", msg)
    def onDeactivatePage(self, id):
        if id in (3, 4):
            self._registerTokens()
            #self.Server.cancel()
        print("WizardController.onDeactivatePage(): %s" % id)
    def confirmFinish(self):
        return True

    def _registerTokens(self):
        code = self.AuthorizationCode.Value
        url = self.Configuration.Url.Scope.Provider.TokenUrl
        data = getTokenParameters(self.Configuration, code, self.CodeVerifier)
        message = "Make Http Request: %s?%s" % (url, data)
        self.Logger.logp(INFO, 'WizardController', '_registerTokens', message)
        timeout = self.Configuration.Timeout
        response = getResponseFromRequest(self.Session, url, data, timeout)
        return registerTokenFromResponse(self.Configuration, response)

    def _getPropertySetInfo(self):
        properties = {}
        interface = 'com.sun.star.uno.XInterface'
        optional = 'com.sun.star.beans.Optional<string>'
        bound = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.BOUND')
        readonly = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        transient = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.TRANSIENT')
        properties['Wizard'] = getProperty('Wizard', 'com.sun.star.ui.dialogs.XWizard', readonly)
        properties['ResourceUrl'] = getProperty('ResourceUrl', 'string', transient)
        properties['UserName'] = getProperty('UserName', 'string', transient)
        properties['Path'] = getProperty('Path', 'short', readonly)
        properties['ActivePath'] = getProperty('ActivePath', 'short', readonly)
        properties['AuthorizationCode'] = getProperty('AuthorizationCode', optional, bound)
        properties['Uuid'] = getProperty('Uuid', 'string', readonly)
        properties['CodeVerifier'] = getProperty('CodeVerifier', 'string', readonly)
        properties['Configuration'] = getProperty('Configuration', interface, readonly)
        properties['Server'] = getProperty('Server', interface, bound | readonly)
        properties['Error'] = getProperty('Error', 'string', transient)
#        properties['Handler'] = getProperty('Handler', interface, readonly)
        return properties
