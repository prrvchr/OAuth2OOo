#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler

import unotools
from unotools import PyServiceInfo

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.OptionsDialog"


class PyOptionsDialog(unohelper.Base, PyServiceInfo, XContainerWindowEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        self.stringResource = unotools.getStringResource(self.ctx, None, "OptionsDialog")
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
        elif method == "Logger":
            self._doLogger(dialog, bool(event.Source.State))
            handled = True
        elif method == "Remove":
            self._doRemove(dialog)
            handled = True
        elif method == "Reset":
            self._doReset(dialog)
            handled = True
        elif method == "View":
            self._doView(dialog)
            handled = True
        return handled
    def getSupportedMethodNames(self):
        return ("external_event", "Changed", "Connect", "Logger", "Remove", "Reset", "View")

    def _doChanged(self, dialog, control):
        item = control.Model.Tag
        text = control.getText()
        if item == "UserName":
            self.service.UserName = text
        elif item == "Url":
            self.service.ResourceUrl = text
            dialog.getControl("CommandButton2").Model.Enabled = text != ""
        self._updateUI(dialog)

    def _doConnect(self, dialog):
        token = self.service.execute(())
        self._updateUI(dialog)

    def _doLogger(self, dialog, enabled):
        self._updateLogUI(dialog, enabled)

    def _doRemove(self, dialog):
        user = self.service.Setting.Url.Provider.Scope.User
        user.Scope = ""
        user.commit()
        self._updateUI(dialog)

    def _doReset(self, dialog):
        user = self.service.Setting.Url.Provider.Scope.User
        user.ExpiresIn = 0
        user.commit()
        self._updateUI(dialog)

    def _doView(self, window):
        title = unotools.getLogUrl(self.ctx)
        length, sequence = unotools.getFileSequence(self.ctx, title)
        text = sequence.value.decode("utf-8")
        url = "vnd.sun.star.script:OAuth2OOo.LogDialog?location=application"
        dialog = unotools.createService(self.ctx, "com.sun.star.awt.DialogProvider").createDialog(url)
        dialog.Title = title
        dialog.getControl("TextField1").Text = text
        dialog.execute()
        dialog.dispose()

    def _loadSetting(self, dialog):
        dialog.getControl("NumericField1").setValue(self.service.Setting.RequestTimeout)
        dialog.getControl("NumericField2").setValue(self.service.Setting.HandlerTimeout)
        dialog.getControl("ComboBox2").Model.StringItemList = self.service.Setting.UrlList
        level = unotools.getLogLevel(self.ctx)
        levels = unotools.getLogLevels()
        enabled = level in levels
        dialog.getControl("CheckBox1").State = int(enabled)
        control = dialog.getControl("ComboBox1")
        control.Text = self._getControlText(control, levels, level)
        dialog.getControl("OptionButton%s" % unotools.getLogHandler(self.ctx)).State = 1
        self._updateLogUI(dialog, enabled)

    def _getControlText(self, control, levels, level):
        name = control.Model.Name
        index = control.ItemCount -1
        text = self.stringResource.resolveString("OptionsDialog.%s.StringItemList.%s" % (name, index))
        if level in levels:
            index = levels.index(level)
            text = self.stringResource.resolveString("OptionsDialog.%s.StringItemList.%s" % (name, index))
        return text

    def _getControlLevel(self, control):
        name = control.Model.Name
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.OFF")
        levels = unotools.getLogLevels()
        for index in range(control.ItemCount):
            text = self.stringResource.resolveString("OptionsDialog.%s.StringItemList.%s" % (name, index))
            if text == control.Text:
                level = levels[index]
                break
        return level

    def _saveSetting(self, dialog):
        self.service.Setting.RequestTimeout = int(dialog.getControl("NumericField1").getValue())
        self.service.Setting.HandlerTimeout = int(dialog.getControl("NumericField2").getValue())
        self.service.Setting.commit()
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.OFF")
        if dialog.getControl("CheckBox1").State:
            level = self._getControlLevel(dialog.getControl("ComboBox1"))
            if dialog.getControl("OptionButton1").State:
                unotools.logToConsole(self.ctx)
            else:
                unotools.logToFile(self.ctx)
        unotools.setLogLevel(self.ctx, level)

    def _updateUI(self, dialog):
        enabled = self.service.Setting.Url.Provider.Scope.Authorized
        if enabled:
            dialog.getControl("Label8").setText(self.service.Setting.Url.Provider.Scope.User.RefreshToken)
            dialog.getControl("Label10").setText(self.service.Setting.Url.Provider.Scope.User.AccessToken)
            dialog.getControl("Label12").setText(self.service.Setting.Url.Provider.Scope.User.ExpiresIn)
        else:
            dialog.getControl("Label8").setText(self.stringResource.resolveString("OptionsDialog.Label8.Label"))
            dialog.getControl("Label10").setText(self.stringResource.resolveString("OptionsDialog.Label10.Label"))
            dialog.getControl("Label12").setText(self.stringResource.resolveString("OptionsDialog.Label12.Label"))
        dialog.getControl("CommandButton3").Model.Enabled = enabled
        dialog.getControl("CommandButton4").Model.Enabled = enabled

    def _updateLogUI(self, dialog, enabled):
        dialog.getControl("Label4").Model.Enabled = enabled
        dialog.getControl("ComboBox1").Model.Enabled = enabled
        dialog.getControl("OptionButton1").Model.Enabled = enabled
        dialog.getControl("OptionButton2").Model.Enabled = enabled
        dialog.getControl("CommandButton1").Model.Enabled = enabled


g_ImplementationHelper.addImplementation(PyOptionsDialog,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services
