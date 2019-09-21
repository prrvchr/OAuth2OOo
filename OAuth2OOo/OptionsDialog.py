#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.awt import XDialogEventHandler
from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from oauth2 import createService
from oauth2 import getFileSequence
from oauth2 import getLogger
from oauth2 import getLoggerUrl
from oauth2 import getLoggerSetting
from oauth2 import setLoggerSetting
from oauth2 import getStringResource
from oauth2 import getNamedValueSet
from oauth2 import g_identifier
from oauth2 import getConfiguration
from oauth2 import getInteractionHandler
from oauth2 import InteractionRequest
from oauth2 import getUserNameFromHandler

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OptionsDialog' % g_identifier


class OptionsDialog(unohelper.Base,
                    XServiceInfo,
                    XContainerWindowEventHandler,
                    XDialogEventHandler):
    def __init__(self, ctx):
        self.ctx = ctx
        self.stringResource = getStringResource(self.ctx, g_identifier, 'OAuth2OOo', 'OptionsDialog')
        self.service = createService(self.ctx, '%s.OAuth2Service' % g_identifier)
        self.Logger = getLogger(self.ctx)

    # XContainerWindowEventHandler, XDialogEventHandler
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
        elif method == 'TextChanged':
            self._doTextChanged(dialog, event.Source)
            handled = True
        elif method == 'SelectionChanged':
            self._doSelectionChanged(dialog, event.Source)
            handled = True
        elif method == 'Connect':
            self._doConnect(dialog)
            handled = True
        elif method == 'Logger':
            enabled = event.Source.State == 1
            self._toggleLogger(dialog, enabled)
            handled = True
        elif method == 'Remove':
            self._doRemove(dialog)
            handled = True
        elif method == 'Reset':
            self._doReset(dialog)
            handled = True
        elif method == 'ViewLog':
            self._doViewLog(dialog)
            handled = True
        elif method == 'ClearLog':
            self._doClearLog(dialog)
            handled = True
        elif method == 'AutoClose':
            handled = True
        return handled
    def getSupportedMethodNames(self):
        return ('external_event', 'Logger', 'TextChanged', 'SelectionChanged', 'Connect',
                'Remove', 'Reset', 'ViewLog', 'ClearLog', 'AutoClose')

    def _doTextChanged(self, dialog, control):
        print("OptionsDialog._doTextChanged()")
        enabled = control.Text != ''
        dialog.getControl('CommandButton2').Model.Enabled = True

    def _doSelectionChanged(self, dialog, control):
        print("OptionsDialog._doSelectionChanged()")
        enabled = control.SelectedText != ''
        dialog.getControl('CommandButton2').Model.Enabled = True

    def _doChanged1(self, dialog, control):
        item = control.Model.Tag
        text = control.getText()
        mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
        mri.inspect(control)
        print("OptionsDialog._doChanged() %s - %s" % (item, text))
        if item == 'UserName':
            self.service.UserName = text
        elif item == 'Url':
            self.service.ResourceUrl = text
        print("OptionsDialog._doChanged()")

    def _doConnect(self, dialog):
        try:
            user = ''
            print("OptionDialog._doConnect() 1")
            url = dialog.getControl('ComboBox2').SelectedText
            if url != '':
                message = "Authentication"
                if self.service.initializeSession(url):
                    print("OptionDialog._doConnect() 2")
                    provider = self.service.ProviderName
                    user = getUserNameFromHandler(self.ctx, self, provider, message)
            autoclose = bool(dialog.getControl('CheckBox2').State)
            print("OptionDialog._doConnect() 3 %s - %s - %s" % (user, url, autoclose))
            enabled = self.service.getAuthorization(url, user, autoclose)
            print("OptionDialog._doConnect() 4")
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            self.Logger.logp(SEVERE, "OptionsDialog", "_doConnect()", msg)
            print("OptionsDialog._doConnect() %s" % msg)

    def _loadSetting(self, dialog):
        dialog.getControl('NumericField1').setValue(self.service.Setting.ConnectTimeout)
        dialog.getControl('NumericField2').setValue(self.service.Setting.ReadTimeout)
        dialog.getControl('NumericField3').setValue(self.service.Setting.HandlerTimeout)
        dialog.getControl('ComboBox2').Model.StringItemList = self.service.Setting.UrlList
        self._loadLoggerSetting(dialog)

    def _saveSetting(self, dialog):
        self.service.Setting.ConnectTimeout = int(dialog.getControl('NumericField1').getValue())
        self.service.Setting.ReadTimeout = int(dialog.getControl('NumericField2').getValue())
        self.service.Setting.HandlerTimeout = int(dialog.getControl('NumericField3').getValue())
        self.service.Setting.commit()
        self._saveLoggerSetting(dialog)

    def _toggleLogger(self, dialog, enabled):
        dialog.getControl('Label1').Model.Enabled = enabled
        dialog.getControl('ComboBox1').Model.Enabled = enabled
        dialog.getControl('OptionButton1').Model.Enabled = enabled
        dialog.getControl('OptionButton2').Model.Enabled = enabled
        dialog.getControl('CommandButton1').Model.Enabled = enabled

    def _doViewLog(self, window):
        url = getLoggerUrl(self.ctx)
        length, sequence = getFileSequence(self.ctx, url)
        text = sequence.value.decode('utf-8')
        dialog = self._getDialog(window, 'LogDialog')
        dialog.Title = url
        dialog.getControl('TextField1').Text = text
        dialog.execute()
        dialog.dispose()

    def _doClearLog(self, dialog):
        try:
            print("OptionsDialog._doClearLog() 1")
            #mri = self.ctx.ServiceManager.createInstance('mytools.Mri')
            #c1 = getConfiguration(self.ctx, 'org.openoffice.Interaction/InteractionHandlers')
            #mri.inspect(c1)
            scheme = 'vnd.google-apps'
            message = "Authentication"
            handler = getInteractionHandler(self.ctx, message)
            response = uno.createUnoStruct('com.sun.star.beans.Optional<string>')
            request = getOAuth2Request(self, scheme, message)
            interaction = InteractionRequest(request, response)
            print("OptionsDialog._doClearLog() 2")
            if handler.handleInteractionRequest(interaction):
                print("OptionsDialog._doClearLog() OK: %s - %s" % (response.IsPresent, response.Value))
            else:
                print("OptionsDialog._doClearLog() CANCEL")
            print("OptionsDialog._doClearLog() 3")
        except Exception as e:
            print("OptionsDialog._doClearLog().Error: %s - %s" % (e, traceback.print_exc()))

    def _doClearLog1(self, dialog):
        try:
            url = getLoggerUrl(self.ctx)
            sf = self.ctx.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')
            if sf.exists(url):
                sf.kill(url)
            service = 'org.openoffice.logging.FileHandler'
            args = getNamedValueSet({'FileURL': url})
            handler = self.ctx.ServiceManager.createInstanceWithArgumentsAndContext(service, args, self.ctx)
            logger = getLogger(self.ctx)
            logger.addLogHandler(handler)
            length, sequence = getFileSequence(self.ctx, url)
            text = sequence.value.decode('utf-8')
            dialog.getControl('TextField1').Text = text
            print("OptionsDialog._doClearLog() 1")
        except Exception as e:
            print("OptionsDialog._doClearLog().Error: %s - %s" % (e, traceback.print_exc()))

    def _getDialog(self, window, name):
        url = 'vnd.sun.star.script:OAuth2OOo.%s?location=application' % name
        service = 'com.sun.star.awt.DialogProvider'
        provider = self.ctx.ServiceManager.createInstanceWithContext(service, self.ctx)
        arguments = getNamedValueSet({'ParentWindow': window.Peer, 'EventHandler': self})
        dialog = provider.createDialogWithArguments(url, arguments)
        return dialog

    def _loadLoggerSetting(self, dialog):
        enabled, index, handler = getLoggerSetting(self.ctx)
        dialog.getControl('CheckBox1').State = int(enabled)
        self._setLoggerLevel(dialog.getControl('ComboBox1'), index)
        dialog.getControl('OptionButton%s' % handler).State = 1
        self._toggleLogger(dialog, enabled)

    def _setLoggerLevel(self, control, index):
        control.Text = self._getLoggerLevelText(control.Model.Name, index)

    def _getLoggerLevel(self, control):
        name = control.Model.Name
        for index in range(control.ItemCount):
            if self._getLoggerLevelText(name, index) == control.Text:
                break
        return index

    def _getLoggerLevelText(self, name, index):
        text = 'OptionsDialog.%s.StringItemList.%s' % (name, index)
        return self.stringResource.resolveString(text)

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
