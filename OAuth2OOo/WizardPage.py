#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.ui.dialogs import XWizardPage
from com.sun.star.awt import XCallback

import oauth2
from oauth2 import PropertySet, Initialization

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardPage"


class WizardPage(unohelper.Base, XServiceInfo, PropertySet, Initialization, XWizardPage, XCallback):
    def __init__(self, ctx, *namedvalues):
        self.ctx = ctx
        self.listeners = []
        self._Controller = None
        self._PageId = None
        self._Window = None
        self.initialize(namedvalues)
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "__init__()", "PageId: %s... Done" % self.PageId)

    @property
    def Controller(self):
        return self._Controller
    @Controller.setter
    def Controller(self, controller):
        self._Controller = controller
    @property
    def PageId(self):
        return self._PageId
    @PageId.setter
    def PageId(self, id):
        self._PageId = id
    @property
    def Window(self):
        return self._Window
    @Window.setter
    def Window(self, window):
        self._Window = window

    def _getPropertySetInfo(self):
        properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        properties["Controller"] = oauth2.getProperty("Controller", "com.sun.star.ui.dialogs.XWizardController", readonly)
        properties["PageId"] = oauth2.getProperty("PageId", "short", readonly)
        properties["Window"] = oauth2.getProperty("Window", "com.sun.star.awt.XWindow", readonly)
        return properties

    # XWizardPage Methods
    def activatePage(self):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "activatePage()", "PageId: %s..." % self.PageId)
        if self.PageId == 2:
            url = self.Controller.AuthorizationStr
            self.Window.getControl("TextField1").setText(url)
        self.Window.setVisible(True)
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "activatePage()", "PageId: %s... Done" % self.PageId)
    def commitPage(self, reason):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "commitPage()", "PageId: %s..." % self.PageId)
        forward = uno.getConstantByName("com.sun.star.ui.dialogs.WizardTravelType.FORWARD")
        backward = uno.getConstantByName("com.sun.star.ui.dialogs.WizardTravelType.BACKWARD")
        finish = uno.getConstantByName("com.sun.star.ui.dialogs.WizardTravelType.FINISH")
        self.Window.setVisible(False)
        if self.PageId == 1 and reason == forward:
            name = self.Window.getControl("TextField1").getText()
            self.Controller.UserName = name
        elif self.PageId == 4 and reason == finish:
            code = self.Window.getControl("TextField1").getText()
            self.Controller.AuthorizationCode = code
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "commitPage()", "PageId: %s... Done" % self.PageId)
        return True
    def canAdvance(self):
        advance = False
        if self.PageId == 1:
            advance = self.Window.getControl("TextField1").getText() != ""
            url = self.Window.getControl("ComboBox1").getText()
            urls = self.Window.getControl("ComboBox1").Model.StringItemList
            provider = self.Window.getControl("ComboBox2").getText()
            providers = self.Window.getControl("ComboBox2").Model.StringItemList
            scope = self.Window.getControl("ComboBox3").getText()
            scopes = self.Window.getControl("ComboBox3").Model.StringItemList
            advance = advance and (url in urls) and (provider in providers) and (scope in scopes)
        elif self.PageId == 2:
            advance = self.Controller.CheckUrl
        return advance
    def dispose(self):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "dispose()", "PageId: %s..." % self.PageId)
        event = uno.createUnoStruct('com.sun.star.lang.EventObject', self)
        for listener in self.listeners:
            listener.disposing(event)
        self.Window.dispose()
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "dispose()", "PageId: %s... Done" % self.PageId)
    def addEventListener(self, listener):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "addEventListener()", "PageId: %s..." % self.PageId)
        if listener not in self.listeners:
            self.listeners.append(listener)
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "addEventListener()", "PageId: %s... Done" % self.PageId)
    def removeEventListener(self, listener):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "removeEventListener()", "PageId: %s..." % self.PageId)
        if listener in self.listeners:
            self.listeners.remove(listener)
        self.Controller.Configuration.Logger.logp(level, "WizardPage", "removeEventListener()", "PageId: %s... Done" % self.PageId)

    # XCallback
    def notify(self, percent):
        if self.PageId == 3 and self.Window:
            self.Window.getControl("ProgressBar1").setValue(percent)

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)



g_ImplementationHelper.addImplementation(WizardPage,                                # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
