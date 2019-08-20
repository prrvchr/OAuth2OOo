#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardPage
from com.sun.star.awt import XCallback
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

import traceback


class WizardPage(unohelper.Base,
                 XWizardPage,
                 XCallback):
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
            #if username:
            self.Window.getControl('TextField1').Text = username
            urls = self.Configuration.UrlList
            control = self.Window.getControl('ComboBox1')
            #if urls:
            control.Model.StringItemList = urls
            providers = self.Configuration.Url.ProviderList
            #if providers:
            self.Window.getControl('ComboBox2').Model.StringItemList = providers
            url = self.Configuration.Url.Id
            #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
            #mri.inspect(control)
            #if url:
            print("WizardPage.activatePage() 1 Url %s" % url)
            control.Text = url
            #else:
            #    title = self.stringResource.resolveString('PageWizard1.FrameControl2.Label')
            #    self.Window.getControl('FrameControl2').Model.Label = title % ''


        elif self.PageId == 2:
            url = getAuthorizationStr(self.ctx, self.Configuration, self.Uuid)
            self.Window.getControl('TextField1').Text = url
            #address = self.Configuration.Url.Scope.Provider.RedirectAddress
            #self.Window.getControl('TextField3').setText(address)
            #port = self.Configuration.Url.Scope.Provider.RedirectPort
            #self.Window.getControl('NumericField1').setValue(port)
            #option = 'OptionButton%s' % getActivePath(self.Configuration)
            #self.Window.getControl(option).setState(True)
        elif self.PageId == 3:
            url = getAuthorizationUrl(self.ctx, self.Configuration, self.Uuid)
            openUrl(self.ctx, url)
        elif self.PageId == 4:
            url = getAuthorizationUrl(self.ctx, self.Configuration, self.Uuid)
            openUrl(self.ctx, url)
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
            name = self.Window.getControl('TextField1').Text
            self.Configuration.Url.Scope.Provider.User.Id = name
        elif self.PageId == 2:
            pass
            #address = self.Window.getControl('TextField3').getText()
            #self.Configuration.Url.Scope.Provider.RedirectAddress = address
            #port = int(self.Window.getControl('NumericField1').getValue())
            #self.Configuration.Url.Scope.Provider.RedirectPort = port
        elif self.PageId == 3:
            pass
        elif self.PageId == 4 and reason == finish:
            code = self.Window.getControl('TextField1').getText()
            self.AuthorizationCode.Value = code
            self.AuthorizationCode.IsPresent = True
        msg += " Done"
        self.Logger.logp(INFO, 'WizardPage', 'commitPage()', msg)
        return True

    def canAdvance(self):
        advance = False
        if self.PageId == 1:
            advance = self.Window.getControl('TextField1').Text != ''
            advance &= self.Window.getControl('CommandButton2').Model.Enabled
            advance &= self.Window.getControl('CommandButton5').Model.Enabled
            advance &= self.Window.getControl('CommandButton8').Model.Enabled
            #url = self.Window.getControl('ComboBox1').SelectedText
            #urls = self.Window.getControl('ComboBox1').Model.StringItemList
            #provider = self.Window.getControl('ComboBox2').SelectedText
            #providers = self.Window.getControl('ComboBox2').Model.StringItemList
            #scope = self.Window.getControl('ComboBox3').SelectedText
            #scopes = self.Window.getControl('ComboBox3').Model.StringItemList
            #advance = advance and (url in urls) and (provider in providers) and (scope in scopes)
        elif self.PageId == 2:
            advance = checkUrl(self.ctx, self.Configuration, self.Uuid)
            advance &= bool(self.Window.getControl('CheckBox1').Model.State)
        print("WizardPage.canAdvance(): %s - %s" % (self.PageId, advance))
        return advance

    # XCallback
    def notify(self, percent):
        if self.PageId == 3 and self.Window:
            self.Window.getControl('ProgressBar1').setValue(percent)

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
        return properties
