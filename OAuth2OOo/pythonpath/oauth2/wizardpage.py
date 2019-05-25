#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardPage
from com.sun.star.awt import XCallback

from .unolib import PropertySet

from .unotools import createService
from .unotools import getProperty

from .logger import getLogger

from .oauth2tools import g_wizard_paths
from .oauth2tools import getActivePath
from .oauth2tools import getAuthorizationStr
from .oauth2tools import checkUrl
from .oauth2tools import openUrl

import traceback


class WizardPage(unohelper.Base,
                 PropertySet,
                 XWizardPage,
                 XCallback):
    def __init__(self, ctx, configuration, id, parent, handler, uuid, result):
        self.ctx = ctx
        self.Configuration = configuration
        self.PageId = id
        provider = createService(self.ctx, 'com.sun.star.awt.ContainerWindowProvider')
        url = 'vnd.sun.star.script:OAuth2OOo.PageWizard%s?location=application' % id
        self.Window = provider.createContainerWindow(url, '', parent, handler)
        self.Uuid = uuid
        self.AuthorizationCode = result
        self.listeners = []
        self.Logger = getLogger(self.ctx)
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Logger.logp(level, 'WizardPage', '__init__()', 'PageId: %s... Done' % self.PageId)

    # XWizardPage Methods
    def activatePage(self):
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Logger.logp(level, 'WizardPage', 'activatePage()', 'PageId: %s...' % self.PageId)
        if self.PageId == 1:
            username = self.Configuration.Url.Scope.Provider.User.Id
            self.Window.getControl('TextField1').setText(username)
            urls = self.Configuration.UrlList
            control = self.Window.getControl('ComboBox1')
            control.Model.StringItemList = urls
            providers = self.Configuration.Url.ProviderList
            self.Window.getControl('ComboBox2').Model.StringItemList = providers
            url = self.Configuration.Url.Id
            if url:
                control.setText(url)
        elif self.PageId == 2:
            url = getAuthorizationStr(self.ctx, self.Configuration, self.Uuid)
            self.Window.getControl('TextField1').setText(url)
            address = self.Configuration.Url.Scope.Provider.RedirectAddress
            self.Window.getControl('TextField2').setText(address)
            port = self.Configuration.Url.Scope.Provider.RedirectPort
            self.Window.getControl('NumericField1').setValue(port)
            option = 'OptionButton%s' % getActivePath(self.Configuration)
            self.Window.getControl(option).setState(True)
        elif self.PageId == 3:
            openUrl(self.ctx, self.Configuration, self.Uuid)
        elif self.PageId == 4:
            openUrl(self.ctx, self.Configuration, self.Uuid)
        self.Window.setVisible(True)
        self.Logger.logp(level, 'WizardPage', 'activatePage()', 'PageId: %s... Done' % self.PageId)

    def commitPage(self, reason):
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Logger.logp(level, 'WizardPage', 'commitPage()', 'PageId: %s...' % self.PageId)
        forward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.FORWARD')
        backward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.BACKWARD')
        finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.FINISH')
        self.Window.setVisible(False)
        if self.PageId == 1 and reason == forward:
            name = self.Window.getControl('TextField1').getText()
            self.Configuration.Url.Scope.Provider.User.Id = name
        elif self.PageId == 2:
            address = self.Window.getControl('TextField2').getText()
            self.Configuration.Url.Scope.Provider.RedirectAddress = address
            port = int(self.Window.getControl('NumericField1').getValue())
            self.Configuration.Url.Scope.Provider.RedirectPort = port
        elif self.PageId == 3:
            pass
        elif self.PageId == 4 and reason == finish:
            code = self.Window.getControl('TextField1').getText()
            self.AuthorizationCode.Value = code
            self.AuthorizationCode.IsPresent = True
        self.Logger.logp(level, 'WizardPage', 'commitPage()', 'PageId: %s... Done' % self.PageId)
        return True

    def canAdvance(self):
        advance = False
        if self.PageId == 1:
            advance = self.Window.getControl('TextField1').getText() != ''
            url = self.Window.getControl('ComboBox1').getText()
            urls = self.Window.getControl('ComboBox1').Model.StringItemList
            provider = self.Window.getControl('ComboBox2').getText()
            providers = self.Window.getControl('ComboBox2').Model.StringItemList
            scope = self.Window.getControl('ComboBox3').getText()
            scopes = self.Window.getControl('ComboBox3').Model.StringItemList
            advance = advance and (url in urls) and (provider in providers) and (scope in scopes)
        elif self.PageId == 2:
            advance = checkUrl()
        return advance

    # XCallback
    def notify(self, percent):
        if self.PageId == 3 and self.Window:
            self.Window.getControl('ProgressBar1').setValue(percent)

    def _getPropertySetInfo(self):
        properties = {}
        bound = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.BOUND')
        readonly = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        maybevoid = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.MAYBEVOID')
        properties['Configuration'] = getProperty('Configuration', 'com.sun.star.uno.XInterface', readonly)
        properties['PageId'] = getProperty('PageId', 'short', readonly)
        properties['Window'] = getProperty('Window', 'com.sun.star.awt.XWindow', readonly)
        properties['Uuid'] = getProperty('Uuid', 'string', readonly)
        properties['AuthorizationCode'] = getProperty('AuthorizationCode', 'com.sun.star.beans.Optional<string>', transient)
        return properties
