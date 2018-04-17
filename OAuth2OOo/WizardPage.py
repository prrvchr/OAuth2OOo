#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.ui.dialogs import XWizardPage
from com.sun.star.awt import XCallback

import unotools
from unotools import PyPropertySet, PyInitialization
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.WizardPage"


class PyWizardPage(unohelper.Base, PyPropertySet, PyInitialization, XWizardPage, XCallback):
    def __init__(self, ctx, *namedvalues):
        self.ctx = ctx
        self.properties = {}
        readonly = uno.getConstantByName("com.sun.star.beans.PropertyAttribute.READONLY")
        self.properties["Controller"] = unotools.getProperty("Controller", "com.sun.star.ui.dialogs.XWizardController", readonly)
        self.properties["PageId"] = unotools.getProperty("PageId", "short", readonly)
        self.properties["Window"] = unotools.getProperty("Window", "com.sun.star.awt.XWindow", readonly)
        self._Controller = None
        self._PageId = None
        self._Window = None
        self.initialize(namedvalues)

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

    # XWizardPage Methods
    def activatePage(self):
        try:
            print("PyWizardPage.activatePage: %s" % self.PageId)
            if self.PageId == 2:
                url = self.Controller.AuthorizationStr
                self.Window.getControl("TextField1").setText(url)
#            next = uno.getConstantByName("com.sun.star.ui.dialogs.WizardButton.NEXT")
#            self.Controller.Wizard.enableButton(next, False)
            self.Window.setVisible(True)
        except Exception as e:
            print("PyWizardPage.activatePage error: %s" % e)
            traceback.print_exc()
    def commitPage(self, reason):
        try:
            forward = uno.getConstantByName("com.sun.star.ui.dialogs.WizardTravelType.FORWARD")
            backward = uno.getConstantByName("com.sun.star.ui.dialogs.WizardTravelType.BACKWARD")
            finish = uno.getConstantByName("com.sun.star.ui.dialogs.WizardTravelType.FINISH")
            print("PyWizardPage.commitPage %s" % self.PageId)
            self.Window.setVisible(False)
            if self.PageId == 1 and reason == forward:
                name = self.Window.getControl("TextField1").getText()
                self.Controller.UserName = name
#                url = self.Window.getControl("ComboBox1").getText()
#                self.Controller.ResourceUrl = url
#                self.Controller.Configuration.commit()
#            elif self.PageId == 2 and reason == forward:
#                address = self.Window.getControl("TextField2").getText()
#                self.Controller.Configuration.Url.Provider.RedirectAddress = address
#                port = int(self.Window.getControl("NumericField1").getValue())
#                self.Controller.Configuration.Url.Provider.RedirectPort = port
#                handler = self.Window.getControl("OptionButton0").getState()
#                print("PyWizardPage.commitPage.handler: %s" % handler)
#                self.Controller.Configuration.Url.Provider.HttpHandler = handler
#                self.Controller.Configuration.Url.Provider.commit()
            elif self.PageId == 4 and reason == finish:
                code = self.Window.getControl("TextField1").getText()
                self.Controller.AuthorizationCode = code
            return True
        except Exception as e:
            print("PyWizardPage.commitPage error: %s" % e)
            traceback.print_exc()
    def canAdvance(self):
        try:
            print("PyWizardPage.canAdvance %s" % self.PageId)
            advance = False
            if self.PageId == 1:
                advance = self.Window.getControl("TextField1").getText() != ""
                url = self.Window.getControl("ComboBox1").getText()
                urls = self.Window.getControl("ComboBox1").Model.StringItemList
                provider = self.Window.getControl("ComboBox2").getText()
                providers = self.Window.getControl("ComboBox2").Model.StringItemList
                scope = self.Window.getControl("ComboBox3").getText()
                scopes = self.Window.getControl("ComboBox3").Model.StringItemList
#                print("advance: %s \nurl: %s\nurls: %s\nprovider: %s\nproviders: %s\nscope:%s\nscopes: %s" % (advance, url, urls, provider, providers, scope, scopes))
                advance = advance and (url in urls) and (provider in providers) and (scope in scopes)
            elif self.PageId == 2:
                advance = self.Controller.CheckUrl
            return advance
        except Exception as e:
            print("PyWizardPage.canAdvance error: %s" % e)
            traceback.print_exc()

    # XCallback
    def notify(self, percent):
        if self.PageId == 3:
            self.Window.getControl("ProgressBar1").setValue(percent)
        print("WizardPage.notify %s" % percent)


g_ImplementationHelper.addImplementation(PyWizardPage,                              # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
