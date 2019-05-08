#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardController

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

from .logger import getLogger

from .oauth2tools import getActivePath
from .oauth2tools import g_identifier
from .oauth2tools import g_advance_to

import traceback


class WizardController(unohelper.Base,
                       PropertySet,
                       XWizardController):
    def __init__(self, ctx, url, username):
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.ctx = ctx
        self.Configuration = WizardConfiguration(self.ctx)
        self.ResourceUrl = url
        self.UserName = username
        self.AuthorizationCode = uno.createUnoStruct('com.sun.star.beans.Optional<string>')
        self.Server = WizardServer(self.ctx)
        self.Uuid = generateUuid()
        self.advanceTo = g_advance_to # 0 to disable
        self.Pages = {}
        self.Handler = WizardHandler(self.ctx, self.Configuration, self)
        self.Logger = getLogger(self.ctx)
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo')
        self.Provider = createService(self.ctx, 'com.sun.star.awt.ContainerWindowProvider')

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
        if id not in self.Pages:
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
            self.Logger.logp(level, "WizardController", "createPage()", "PageId: %s..." % id)
            page = WizardPage(self.ctx,
                              self.Configuration,
                              id,
                              parent,
                              self.Handler,
                              self.Uuid,
                              self.AuthorizationCode)
            if id == 3:
                self.Server.addCallback(page, self)
            self.Pages[id] = page
        return self.Pages[id]
    def getPageTitle(self, id):
        title = self.stringResource.resolveString('PageWizard%s.Step' % (id, ))
        return title
    def canAdvance(self):
        return True
    def onActivatePage(self, id):
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Logger.logp(level, "WizardController", "onActivatePage()", "PageId: %s..." % id)
        title = self.stringResource.resolveString('PageWizard%s.Title' % (id, ))
        self.Handler.Wizard.setTitle(title)
        finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.FINISH')
        self.Handler.Wizard.enableButton(finish, False)
        if id == 1:
            self.Handler.Wizard.activatePath(self.ActivePath, True)
            self.Handler.Wizard.updateTravelUI()
        if self.advanceTo:
            self.advanceTo = 0
            self.Handler.Wizard.advanceTo(g_advance_to)
        self.Logger.logp(level, "WizardController", "onActivatePage()", "PageId: %s... Done" % id)
    def onDeactivatePage(self, id):
        pass
    def confirmFinish(self):
        return True

    def _getPropertySetInfo(self):
        properties = {}
        bound = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.BOUND')
        readonly = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        transient = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.TRANSIENT')
        maybevoid = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.MAYBEVOID')
        properties['ResourceUrl'] = getProperty('ResourceUrl', 'string', transient)
        properties['UserName'] = getProperty('UserName', 'string', transient)
        properties['ActivePath'] = getProperty('ActivePath', 'short', readonly)
        properties['AuthorizationCode'] = getProperty('AuthorizationCode', 'com.sun.star.beans.Optional<string>', bound)
        properties['AuthorizationStr'] = getProperty('AuthorizationStr', 'string', readonly)
        properties['CheckUrl'] = getProperty('CheckUrl', 'boolean', readonly)
        properties['Uuid'] = getProperty('Uuid', 'string', readonly)
        properties['CodeVerifier'] = getProperty('CodeVerifier', 'string', readonly)
        properties['Configuration'] = getProperty('Configuration', 'com.sun.star.uno.XInterface', readonly)
        properties['Server'] = getProperty('Server', 'com.sun.star.uno.XInterface', bound | readonly)
        properties['Paths'] = getProperty('Paths', '[][]short', readonly)
        properties['Handler'] = getProperty('Handler', 'com.sun.star.uno.XInterface', readonly)
        return properties
