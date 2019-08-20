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
from .oauth2tools import g_identifier
from .oauth2tools import g_wizard_paths
from .oauth2tools import g_advance_to

import traceback


class WizardController(unohelper.Base,
                       PropertySet,
                       XWizardController):
    def __init__(self, ctx, wizard, url, username):
        self.ctx = ctx
        self.Configuration = WizardConfiguration(self.ctx)
        self.ResourceUrl = url
        self.UserName = username
        self.AuthorizationCode = uno.createUnoStruct('com.sun.star.beans.Optional<string>')
        self.Server = WizardServer(self.ctx)
        self.Uuid = generateUuid()
        self.advanceTo = g_advance_to # 0 to disable
        self.Wizard = wizard
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
            print("WizardController.createPage() 1")
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
            print("WizardController.createPage() 2")
            if id == 3:
                self.Server.addCallback(page, self)
            msg += " Done"
            self.Logger.logp(INFO, "WizardController", "createPage()", msg)
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
        msg += " Done"
        self.Logger.logp(INFO, "WizardController", "onActivatePage()", msg)
    def onDeactivatePage(self, id):
        pass
    def confirmFinish(self):
        return True

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
        properties['ActivePath'] = getProperty('ActivePath', 'short', readonly)
        properties['AuthorizationCode'] = getProperty('AuthorizationCode', optional, bound)
        properties['Uuid'] = getProperty('Uuid', 'string', readonly)
        properties['CodeVerifier'] = getProperty('CodeVerifier', 'string', readonly)
        properties['Configuration'] = getProperty('Configuration', interface, readonly)
        properties['Server'] = getProperty('Server', interface, bound | readonly)
#        properties['Handler'] = getProperty('Handler', interface, readonly)
        return properties
