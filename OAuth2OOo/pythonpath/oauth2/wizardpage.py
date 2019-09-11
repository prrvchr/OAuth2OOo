#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardPage
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .unolib import PropertySet

from .unotools import createService
from .unotools import getContainerWindow
from .unotools import getProperty
from .unotools import getStringResource

from .logger import getLogger

from .oauth2tools import g_identifier
from .oauth2tools import g_wizard_paths
from .oauth2tools import getActivePath
from .oauth2tools import getAuthorizationStr
from .oauth2tools import getAuthorizationUrl
from .oauth2tools import checkUrl
from .oauth2tools import openUrl
from .oauth2tools import updatePageTokenUI

import traceback


class WizardPage(unohelper.Base,
                 PropertySet,
                 XWizardPage):
    def __init__(self, ctx, configuration, id, window, uuid, result):
        try:
            msg = "PageId: %s ..." % id
            print("WizardPage.__init__() 1")
            self.ctx = ctx
            self.Configuration = configuration
            print("WizardPage.__init__() 2")
            self.PageId = id
            print("WizardPage.__init__() 3")
            self.Window = window
            print("WizardPage.__init__() 4")
            self.Uuid = uuid
            self.AuthorizationCode = result
            self.FirstLoad = True
            print("WizardPage.__init__() 5")
            self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo')
            msg += " Done"
            self.Logger = getLogger(self.ctx)
            self.Logger.logp(INFO, 'WizardPage', '__init__()', msg)
            print("WizardPage.__init__() 6")
        except Exception as e:
            print("WizardPage.__init__() ERROR: %s - %s" % (e, traceback.print_exc()))

    # XWizardPage Methods
    def activatePage(self):
        print("WizardPage.activatePage(): %s" % self.PageId)
        self.Window.setVisible(False)
        msg = "PageId: %s ..." % self.PageId
        if self.PageId == 1:
            username = self.Configuration.Url.Scope.Provider.User.Id
            self.Window.getControl('TextField1').Text = username
            control = self.Window.getControl('ComboBox1')
            control.Model.StringItemList = self.Configuration.UrlList
            providers = self.Configuration.Url.ProviderList
            self.Window.getControl('ComboBox2').Model.StringItemList = providers
            control.Text = self.Configuration.Url.Id
        elif self.PageId == 2:
            url = getAuthorizationStr(self.ctx, self.Configuration, self.Uuid)
            self.Window.getControl('TextField1').Text = url
        elif self.PageId == 3:
            url = getAuthorizationUrl(self.ctx, self.Configuration, self.Uuid)
            openUrl(self.ctx, url)
        elif self.PageId == 4:
            url = getAuthorizationUrl(self.ctx, self.Configuration, self.Uuid)
            openUrl(self.ctx, url)
        elif self.PageId == 5:
            username = self.Configuration.Url.Scope.Provider.User.Id
            provider = self.Configuration.Url.ProviderName
            title = self.stringResource.resolveString('PageWizard5.FrameControl1.Label')
            self.Window.getControl('FrameControl1').Model.Label = title % (username, provider)
            updatePageTokenUI(self.Window, self.Configuration, self.stringResource)
        self.Window.setVisible(True)
        msg += " Done"
        self.Logger.logp(level, 'WizardPage', 'activatePage()', msg)

    def commitPage(self, reason):
        msg = "PageId: %s ..." % self.PageId
        forward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.FORWARD')
        backward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.BACKWARD')
        finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.FINISH')
        self.Window.setVisible(False)
        if self.PageId == 1 and reason == forward:
            pass
        elif self.PageId == 2:
            pass
        elif self.PageId == 3:
            pass
        elif self.PageId == 4:
            code = self.Window.getControl('TextField1').Text
            self.AuthorizationCode.Value = code
            self.AuthorizationCode.IsPresent = True
        msg += " Done"
        self.Logger.logp(INFO, 'WizardPage', 'commitPage()', msg)
        return True

    def canAdvance(self):
        advance = True
        if self.PageId == 1:
            advance = self.Window.getControl('TextField1').Text != ''
            advance &= self.Window.getControl('CommandButton2').Model.Enabled
            advance &= self.Window.getControl('CommandButton5').Model.Enabled
            advance &= self.Window.getControl('CommandButton8').Model.Enabled
        elif self.PageId == 2:
            advance = checkUrl(self.ctx, self.Configuration, self.Uuid)
            advance &= bool(self.Window.getControl('CheckBox1').Model.State)
        elif self.PageId == 3:
            advance = self.AuthorizationCode.IsPresent
            advance = True
        elif self.PageId == 4:
            advance = self.Window.getControl('TextField1').Text != ''
        print("WizardPage.canAdvance(): %s - %s" % (self.PageId, advance))
        return advance

    def _getPropertySetInfo(self):
        properties = {}
        interface = 'com.sun.star.uno.XInterface'
        optional = 'com.sun.star.beans.Optional<string>'
        readonly = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        transient = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.TRANSIENT')
        properties['Configuration'] = getProperty('Configuration', interface, readonly)
        properties['PageId'] = getProperty('PageId', 'short', readonly)
        properties['Window'] = getProperty('Window', 'com.sun.star.awt.XWindow', readonly)
        properties['Uuid'] = getProperty('Uuid', 'string', readonly)
        properties['AuthorizationCode'] = getProperty('AuthorizationCode', optional, transient)
        properties['FirstLoad'] = getProperty('FirstLoad', 'boolean', transient)
        return properties
