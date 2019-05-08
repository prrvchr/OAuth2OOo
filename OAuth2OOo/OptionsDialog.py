#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from oauth2 import createService
from oauth2 import getFileSequence
from oauth2 import getLogger
from oauth2 import getLoggerUrl
from oauth2 import getLoggerSetting
from oauth2 import setLoggerSetting
from oauth2 import getStringResource
from oauth2 import g_identifier

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OptionsDialog' % g_identifier


class OptionsDialog(unohelper.Base,
                    XServiceInfo,
                    XContainerWindowEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo', 'OptionsDialog')
        self.service = createService(self.ctx, '%s.OAuth2Service' % g_identifier)
        self.Logger = getLogger(self.ctx)

    # XContainerWindowEventHandler
    def callHandlerMethod(self, dialog, event, method):
        handled = False
        if method == 'external_event':
            if event == 'ok':
                self._saveSetting(dialog)
                handled = True
            elif event == 'back':
                self._loadSetting(dialog)
                handled = True
            elif event == 'initialize':
                self._loadSetting(dialog)
                handled = True
        elif method == 'Changed':
            self._doChanged(dialog, event.Source)
            handled = True
        elif method == 'Connect':
            self._doConnect(dialog)
            handled = True
        elif method == 'Logger':
            self._doLogger(dialog, bool(event.Source.State))
            handled = True
        elif method == 'Remove':
            self._doRemove(dialog)
            handled = True
        elif method == 'Reset':
            self._doReset(dialog)
            handled = True
        elif method == 'View':
            self._doView(dialog)
            handled = True
        return handled
    def getSupportedMethodNames(self):
        return ('external_event', 'Changed', 'Connect', 'Logger', 'Remove', 'Reset', 'View')

    def _doChanged(self, dialog, control):
        item = control.Model.Tag
        text = control.getText()
        if item == 'UserName':
            self.service.UserName = text
        elif item == 'Url':
            self.service.ResourceUrl = text
        self._updateUI(dialog)

    def _doConnect(self, dialog):
        try:
            token = self.service.getToken('%s')
            self._updateUI(dialog)
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            self.Logger.logp(SEVERE, "OptionsDialog", "_doConnect()", msg)
            print("OptionsDialog._doConnect() %s" % msg)

    def _doRemove(self, dialog):
        user = self.service.Setting.Url.Scope.Provider.User
        user.Scope = ''
        user.commit()
        self._updateUI(dialog)

    def _doReset(self, dialog):
        user = self.service.Setting.Url.Scope.Provider.User
        user.ExpiresIn = 0
        user.commit()
        self._updateUI(dialog)

    def _loadSetting(self, dialog):
        dialog.getControl('NumericField1').setValue(self.service.Setting.RequestTimeout)
        dialog.getControl('NumericField2').setValue(self.service.Setting.HandlerTimeout)
        dialog.getControl('ComboBox2').Model.StringItemList = self.service.Setting.UrlList
        self._loadLoggerSetting(dialog)

    def _saveSetting(self, dialog):
        self.service.Setting.RequestTimeout = int(dialog.getControl('NumericField1').getValue())
        self.service.Setting.HandlerTimeout = int(dialog.getControl('NumericField2').getValue())
        self.service.Setting.commit()
        self._saveLoggerSetting(dialog)

    def _updateUI(self, dialog):
        enabled = self.service.ResourceUrl != '' and self.service.UserName != ''
        dialog.getControl('CommandButton2').Model.Enabled = enabled
        enabled = enabled and self.service.Setting.Url.Scope.Authorized
        if enabled:
            dialog.getControl('Label8').setText(self.service.Setting.Url.Scope.Provider.User.RefreshToken)
            dialog.getControl('Label10').setText(self.service.Setting.Url.Scope.Provider.User.AccessToken)
            dialog.getControl('Label12').setText(self.service.Setting.Url.Scope.Provider.User.ExpiresIn)
        else:
            dialog.getControl('Label8').setText(self.stringResource.resolveString('OptionsDialog.Label8.Label'))
            dialog.getControl('Label10').setText(self.stringResource.resolveString('OptionsDialog.Label10.Label'))
            dialog.getControl('Label12').setText(self.stringResource.resolveString('OptionsDialog.Label12.Label'))
        dialog.getControl('CommandButton3').Model.Enabled = enabled
        dialog.getControl('CommandButton4').Model.Enabled = enabled

    def _doLogger(self, dialog, enabled):
        dialog.getControl('Label4').Model.Enabled = enabled
        dialog.getControl('ComboBox1').Model.Enabled = enabled
        dialog.getControl('OptionButton1').Model.Enabled = enabled
        dialog.getControl('OptionButton2').Model.Enabled = enabled
        dialog.getControl('CommandButton1').Model.Enabled = enabled

    def _doView(self, window):
        url = getLoggerUrl(self.ctx)
        length, sequence = getFileSequence(self.ctx, url)
        text = sequence.value.decode('utf-8')
        dialog = self._getLogDialog()
        dialog.Title = url
        dialog.getControl('TextField1').Text = text
        dialog.execute()
        dialog.dispose()

    def _getLogDialog(self):
        url = 'vnd.sun.star.script:OAuth2OOo.LogDialog?location=application'
        return createService(self.ctx, 'com.sun.star.awt.DialogProvider').createDialog(url)

    def _loadLoggerSetting(self, dialog):
        enabled, index, handler = getLoggerSetting(self.ctx)
        dialog.getControl('CheckBox1').State = int(enabled)
        self._setLoggerLevel(dialog.getControl('ComboBox1'), index)
        dialog.getControl('OptionButton%s' % handler).State = 1
        self._doLogger(dialog, enabled)

    def _setLoggerLevel(self, control, index):
        name = control.Model.Name
        text = self.stringResource.resolveString('OptionsDialog.%s.StringItemList.%s' % (name, index))
        control.Text = text

    def _getLoggerLevel(self, control):
        name = control.Model.Name
        for index in range(control.ItemCount):
            text = self.stringResource.resolveString('OptionsDialog.%s.StringItemList.%s' % (name, index))
            if text == control.Text:
                break
        return index

    def _saveLoggerSetting(self, dialog):
        enabled = bool(dialog.getControl('CheckBox1').State)
        index = self._getLoggerLevel(dialog.getControl('ComboBox1'))
        handler = dialog.getControl('OptionButton1').State
        setLoggerSetting(self.ctx, enabled, index, handler)

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OptionsDialog,
                                         g_ImplementationName,
                                        (g_ImplementationName,))
