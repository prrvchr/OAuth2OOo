#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler

import unotools
from unotools import PyServiceInfo
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.OptionsDialog"


class PyOptionsDialog(unohelper.Base, PyServiceInfo, XContainerWindowEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        identifier = "com.gmail.prrvchr.extensions.OAuth2OOo"
        self.stringResource = unotools.getStringResource(self.ctx, identifier, "OAuth2OOo", file="OptionsDialog")
        self.service = unotools.createService(self.ctx, "com.gmail.prrvchr.extensions.OAuth2OOo.OAuth2Service")

    # XContainerWindowEventHandler
    def callHandlerMethod(self, dialog, event, method):
        handled = False
        if method == "external_event":
            if event == "ok":
                self._saveSetting(dialog)
                handled = True
            elif event == "back":
                self._loadSetting(dialog)
                handled = True
            elif event == "initialize":
                self._loadSetting(dialog)
                handled = True
        elif method == "Changed":
            self._doChanged(dialog, event.Source)
            handled = True
        elif method == "Connect":
            self._doConnect(dialog)
            handled = True
        elif method == "Remove":
            self._doRemove(dialog)
            handled = True
        elif method == "Reset":
            self._doReset(dialog)
            handled = True
        return handled
    def getSupportedMethodNames(self):
        return ("external_event", "Changed", "Connect", "Remove", "Reset")

    def _doChanged(self, dialog, control):
        item = control.Model.Tag
        if item == "UserName":
            pass
        elif item == "Url":
            url = control.getText()
            self.service.ResourceUrl = url
            dialog.getControl("CommandButton1").Model.Enabled = url != ""
            token = self.service.Setting.Url.Provider.Scope.User.AccessToken
            self._updateUI(dialog, token != "")

    def _doConnect(self, dialog):
        try:
            print("PyOptionsDialog._doConnect:1")
#           mri = self.ctx.ServiceManager.createInstance("mytools.Mri")
#           mri.inspect(wizard)
            self.service.UserName = dialog.getControl("TextField1").getText()
            print("PyOptionsDialog._doConnect:2")
            token = self.service.execute(())
            enabled = True if token != "" else False
            self._updateUI(dialog, enabled)
        except Exception as e:
            print("PyOptionsDialog._doConnect error: %s" % e)
            traceback.print_exc()

    def _doRemove(self, dialog):
        user = self.service.Setting.Url.Provider.Scope.User
        user.AccessToken = ""
        user.commit()
        self._updateUI(dialog, True)

    def _doReset(self, dialog):
        user = self.service.Setting.Url.Provider.Scope.User
        user.ExpiresIn = 0
        user.commit()
        self._updateUI(dialog, True)

    def _loadSetting(self, dialog):
        dialog.getControl("NumericField1").setValue(self.service.Setting.RequestTimeout)
        dialog.getControl("NumericField2").setValue(self.service.Setting.HandlerTimeout)
        dialog.getControl("ComboBox1").Model.StringItemList = self.service.Setting.UrlList
        
    def _saveSetting(self, dialog):
        self.service.Setting.RequestTimeout = int(dialog.getControl("NumericField1").getValue())
        self.service.Setting.HandlerTimeout = int(dialog.getControl("NumericField2").getValue())
        self.service.Setting.commit()

    def _updateUI(self, dialog, state):
        if state:
            dialog.getControl("Label7").setText(self.service.Setting.Url.Provider.Scope.User.RefreshToken)
            dialog.getControl("Label9").setText(self.service.Setting.Url.Provider.Scope.User.AccessToken)
            dialog.getControl("Label11").setText(self.service.Setting.Url.Provider.Scope.User.ExpiresIn)
            dialog.getControl("CommandButton2").Model.Enabled = True
            dialog.getControl("CommandButton3").Model.Enabled = True
        else:
            dialog.getControl("Label7").setText(self.stringResource.resolveString("OptionsDialog.Label7.Label"))
            dialog.getControl("Label9").setText(self.stringResource.resolveString("OptionsDialog.Label9.Label"))
            dialog.getControl("Label11").setText(self.stringResource.resolveString("OptionsDialog.Label11.Label"))
            dialog.getControl("CommandButton2").Model.Enabled = False
            dialog.getControl("CommandButton3").Model.Enabled = False


g_ImplementationHelper.addImplementation(PyOptionsDialog,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services
