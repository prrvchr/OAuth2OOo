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
from .oauth2tools import getAuthorizationUrl
from .oauth2tools import checkUrl
from .oauth2tools import openUrl 

import traceback


class WizardPage(unohelper.Base,
                 PropertySet,
                 XWizardPage,
                 XCallback):
    def __init__(self, ctx, configuration, id, parent, handler, code, state, result):
        self.ctx = ctx
        self.Configuration = configuration
        self.PageId = id
        provider = createService(self.ctx, 'com.sun.star.awt.ContainerWindowProvider')
        url = 'vnd.sun.star.script:OAuth2OOo.PageWizard%s?location=application' % id
        self.Window = provider.createContainerWindow(url, '', parent, handler)
        self.CodeVerifier = code
        self.State = state
        self.AuthorizationCode = result
        self.listeners = []
        self.Logger = getLogger(self.ctx)
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
        self.Logger.logp(level, 'WizardPage', '__init__()', 'PageId: %s... Done' % self.PageId)

    # XWizardPage Methods
    def activatePage(self):
        try:
            print("WizardPage.activatePage()")
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
            self.Logger.logp(level, 'WizardPage', 'activatePage()', 'PageId: %s...' % self.PageId)
            if self.PageId == 1:
                username = self.Configuration.Url.Provider.Scope.User.Id
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
                url = getAuthorizationStr(self.ctx, self.Configuration, self.CodeVerifier, self.State)
                self.Window.getControl('TextField1').setText(url)
                address = self.Configuration.Url.Provider.RedirectAddress
                self.Window.getControl('TextField2').setText(address)
                port = self.Configuration.Url.Provider.RedirectPort
                self.Window.getControl('NumericField1').setValue(port)
                option = 'OptionButton%s' % getActivePath(self.Configuration)
                self.Window.getControl(option).setState(True)
            elif self.PageId == 3:
                openUrl(self.ctx, self.Configuration, self.CodeVerifier, self.State)
            elif self.PageId == 4:
                openUrl(self.ctx, self.Configuration, self.CodeVerifier, self.State)
            self.Window.setVisible(True)
            self.Logger.logp(level, 'WizardPage', 'activatePage()', 'PageId: %s... Done' % self.PageId)
        except Exception as e:
            print("WizardPage.activatePage().Error: %s - %s" % (e, traceback.print_exc()))
    def commitPage(self, reason):
        try:
            print("WizardPage.commitPage()")
            level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
            self.Logger.logp(level, 'WizardPage', 'commitPage()', 'PageId: %s...' % self.PageId)
            forward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.FORWARD')
            backward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.BACKWARD')
            finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardTravelType.FINISH')
            self.Window.setVisible(False)
            if self.PageId == 1 and reason == forward:
                name = self.Window.getControl('TextField1').getText()
                self.Configuration.Url.Provider.Scope.User.Id = name
            elif self.PageId == 3:
                pass
            elif self.PageId == 4 and reason == finish:
                code = self.Window.getControl('TextField1').getText()
                self.AuthorizationCode.Value = code
                self.AuthorizationCode.IsPresent = True
            self.Logger.logp(level, 'WizardPage', 'commitPage()', 'PageId: %s... Done' % self.PageId)
            return True
        except Exception as e:
            print("WizardPage.commitPage().Error: %s - %s" % (e, traceback.print_exc()))
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
#    def dispose(self):
#        print("WizardPage.dispose()")
#        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
#        self.Logger.logp(level, 'WizardPage', 'dispose()', 'PageId: %s...' % self.PageId)
#        event = uno.createUnoStruct('com.sun.star.lang.EventObject', self)
#        for listener in self.listeners:
#            listener.disposing(event)
#        self.Window.dispose()
#        self.Logger.logp(level, 'WizardPage', 'dispose()', 'PageId: %s... Done' % self.PageId)
#    def addEventListener(self, listener):
#        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
#        self.Logger.logp(level, 'WizardPage', 'addEventListener()', 'PageId: %s...' % self.PageId)
#        if listener not in self.listeners:
#            self.listeners.append(listener)
#        self.Logger.logp(level, 'WizardPage', 'addEventListener()', 'PageId: %s... Done' % self.PageId)
#    def removeEventListener(self, listener):
#        level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
#        self.Logger.logp(level, 'WizardPage', 'removeEventListener()', 'PageId: %s...' % self.PageId)
#        if listener in self.listeners:
#            self.listeners.remove(listener)
#        self.Logger.logp(level, 'WizardPage', 'removeEventListener()', 'PageId: %s... Done' % self.PageId)

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
        properties['CodeVerifier'] = getProperty('CodeVerifier', 'string', readonly)
        properties['State'] = getProperty('State', 'string', readonly)
        properties['AuthorizationCode'] = getProperty('AuthorizationCode', 'com.sun.star.beans.Optional<string>', transient)
        return properties
