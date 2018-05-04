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
        self.LogLevels = unotools.getLogLevels()

    # XContainerWindowEventHandler
    def callHandlerMethod(self, dialog, event, method):
        handled = False
        if method == "external_event":
            if event == "ok":
                print("PyOptionsDialog.callHandlerMethod.ok")
                self._saveSetting(dialog)
                handled = True
            elif event == "back":
                print("PyOptionsDialog.callHandlerMethod.back")
                self._loadSetting(dialog)
                handled = True
            elif event == "initialize":
                print("PyOptionsDialog.callHandlerMethod.initialize")
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
        token = self.service.Setting.Url.Provider.Scope.User.AccessToken
        self._updateUI(dialog, token != "")

    def _doConnect(self, dialog):
#        logger = unotools.getLoggerSettings(self.ctx, "org.openoffice.logging.DefaultLogger")
#        mri = self.ctx.ServiceManager.createInstance("mytools.Mri")
#        mri.inspect(logger)
        token = self.service.execute(())
        self._updateUI(dialog, token != "")

    def _doLogger(self, dialog, enabled):
        self._updateLogUI(dialog, enabled)

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

    def _doView(self, window):
        text = ""
        url = unotools.getLogUrl(self.ctx)
        fileservice = self.ctx.ServiceManager.createInstance("com.sun.star.ucb.SimpleFileAccess")
        if fileservice.exists(url):
            inputstream = fileservice.openFileRead(url)
            length, seq = inputstream.readBytes(None, fileservice.getSize(url))
            inputstream.closeInput()
            text = seq.value.decode("utf-8")
        title = self.stringResource.resolveString("MessageBox.Title") % url
        dialog = unotools.createMessageBox(window.Peer, text, title, "message", 1)
        dialog.execute()
        dialog.dispose()

    def _loadSetting(self, dialog):
        dialog.getControl("NumericField1").setValue(self.service.Setting.RequestTimeout)
        dialog.getControl("NumericField2").setValue(self.service.Setting.HandlerTimeout)
        dialog.getControl("ComboBox2").Model.StringItemList = self.service.Setting.UrlList
        level = unotools.getLogLevel(self.ctx)
        enabled = level in self.LogLevels
        dialog.getControl("CheckBox1").State = int(enabled)
        dialog.getControl("ComboBox1").Text = self._getComboBoxText("ComboBox1", level)
        dialog.getControl("OptionButton%s" % unotools.getLogHandler(self.ctx)).State = 1
        self._updateLogUI(dialog, enabled)

    def _getComboBoxText(self, name, level):
        text = self.stringResource.resolveString("OptionsDialog.%s.StringItemList.%s" % (name, 7))
        if level in self.LogLevels:
            index = self.LogLevels.index(level)
            text = self.stringResource.resolveString("OptionsDialog.%s.StringItemList.%s" % (name, index))
        return text

    def _getComboBoxLevel(self, control):
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.OFF")
        for index in range(control.ItemCount):
            text = self.stringResource.resolveString("OptionsDialog.%s.StringItemList.%s" % (control.Model.Name, index))
            if text == control.Text:
                level = self.LogLevels[index]
                break
        return level

    def _saveSetting(self, dialog):
        self.service.Setting.RequestTimeout = int(dialog.getControl("NumericField1").getValue())
        self.service.Setting.HandlerTimeout = int(dialog.getControl("NumericField2").getValue())
        self.service.Setting.commit()
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.OFF")
        if dialog.getControl("CheckBox1").State:
            level = self._getComboBoxLevel(dialog.getControl("ComboBox1"))
            if dialog.getControl("OptionButton1").State:
                unotools.logToConsole(self.ctx)
            else:
                unotools.logToFile(self.ctx)
        unotools.setLogLevel(self.ctx, level)

    def _updateUI(self, dialog, enabled):
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
