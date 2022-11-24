#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020 https://prrvchr.github.io                                     ║
║                                                                                    ║
║   Permission is hereby granted, free of charge, to any person obtaining            ║
║   a copy of this software and associated documentation files (the "Software"),     ║
║   to deal in the Software without restriction, including without limitation        ║
║   the rights to use, copy, modify, merge, publish, distribute, sublicense,         ║
║   and/or sell copies of the Software, and to permit persons to whom the Software   ║
║   is furnished to do so, subject to the following conditions:                      ║
║                                                                                    ║
║   The above copyright notice and this permission notice shall be included in       ║
║   all copies or substantial portions of the Software.                              ║
║                                                                                    ║
║   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,                  ║
║   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES                  ║
║   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.        ║
║   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY             ║
║   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,             ║
║   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE       ║
║   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                    ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import uno
import unohelper

from com.sun.star.lang import XServiceInfo

from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.awt import XDialogEventHandler

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from oauth2 import OAuth2Model

from oauth2 import InteractionRequest
from oauth2 import getOAuth2UserName

from oauth2 import createService
from oauth2 import getFileSequence
from oauth2 import getConfiguration
from oauth2 import getInteractionHandler
from oauth2 import getDialog
from oauth2 import getExceptionMessage

from oauth2 import getLoggerUrl
from oauth2 import getLoggerSetting
from oauth2 import setLoggerSetting
from oauth2 import clearLogger
from oauth2 import logMessage
from oauth2 import getMessage
g_message = 'OptionsDialog'

from oauth2 import g_identifier
from oauth2 import g_oauth2

import requests
import os
import sys
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OptionsDialog' % g_identifier


class OptionsDialog(unohelper.Base,
                    XServiceInfo,
                    XContainerWindowEventHandler,
                    XDialogEventHandler):
    def __init__(self, ctx):
        try:
            self._ctx = ctx
            self._model = OAuth2Model(ctx)
            logMessage(self._ctx, INFO, "Loading ... Done", 'OptionsDialog', '__init__()')
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, 'OptionsDialog', '__init__()')

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
        elif method == 'Remove':
            self._doRemove(dialog)
            handled = True
        elif method == 'Reset':
            self._doReset(dialog)
            handled = True
        elif method == 'AutoClose':
            handled = True
        elif method == 'ToggleLogger':
            enabled = event.Source.State == 1
            self._toggleLogger(dialog, enabled)
            handled = True
        elif method == 'EnableViewer':
            self._toggleViewer(dialog, True)
            handled = True
        elif method == 'DisableViewer':
            self._toggleViewer(dialog, False)
            handled = True
        elif method == 'ViewLog':
            self._viewLog(dialog)
            handled = True
        elif method == 'ClearLog':
            self._clearLog(dialog)
            handled = True
        elif method == 'LogInfo':
            self._logInfo(dialog)
            handled = True
        return handled
    def getSupportedMethodNames(self):
        return ('external_event', 'TextChanged', 'SelectionChanged', 'Connect',
                'Remove', 'Reset','AutoClose', 'ToggleLogger', 'EnableViewer',
                'DisableViewer', 'ViewLog', 'ClearLog', 'LogInfo')

    def _doTextChanged(self, dialog, control):
        enabled = control.Text != ''
        dialog.getControl('CommandButton2').Model.Enabled = True

    def _doSelectionChanged(self, dialog, control):
        enabled = control.SelectedText != ''
        dialog.getControl('CommandButton2').Model.Enabled = enabled

    def _doConnect(self, dialog):
        try:
            user = ''
            print("OptionDialog._doConnect() 1")
            url = dialog.getControl('ComboBox2').SelectedText
            if url != '':
                message = self._model.getProviderName(url)
                print("OptionDialog._doConnect() 2 %s" % url)
                user = getOAuth2UserName(self._ctx, self, url, message)
            autoclose = bool(dialog.getControl('CheckBox2').State)
            print("OptionDialog._doConnect() 3 %s - %s - %s" % (user, url, autoclose))
            service = createService(self._ctx, g_oauth2)
            enabled = service.getAuthorization(url, user, autoclose, dialog.getPeer())
            print("OptionDialog._doConnect() 4")
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, "OptionsDialog", "_doConnect()")

    def _loadSetting(self, dialog):
        try:
            dialog.getControl('NumericField1').setValue(self._model.ConnectTimeout)
            dialog.getControl('NumericField2').setValue(self._model.ReadTimeout)
            dialog.getControl('NumericField3').setValue(self._model.HandlerTimeout)
            dialog.getControl('ComboBox2').Model.StringItemList = self._model.UrlList
            self._loadLoggerSetting(dialog)
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, "OptionsDialog", "_loadSetting()")

    def _saveSetting(self, dialog):
        try:
            self._saveLoggerSetting(dialog)
            self._model.ConnectTimeout = int(dialog.getControl('NumericField1').getValue())
            self._model.ReadTimeout = int(dialog.getControl('NumericField2').getValue())
            self._model.HandlerTimeout = int(dialog.getControl('NumericField3').getValue())
            self._model.commit()
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, "OptionsDialog", "_saveSetting()")

    def _toggleLogger(self, dialog, enabled):
        dialog.getControl('Label1').Model.Enabled = enabled
        dialog.getControl('ListBox1').Model.Enabled = enabled
        dialog.getControl('OptionButton1').Model.Enabled = enabled
        control = dialog.getControl('OptionButton2')
        control.Model.Enabled = enabled
        self._toggleViewer(dialog, enabled and control.State)

    def _toggleViewer(self, dialog, enabled):
        dialog.getControl('CommandButton1').Model.Enabled = enabled

    def _viewLog(self, window):
        dialog = getDialog(self._ctx, 'OAuth2OOo', 'LogDialog', self, window.Peer)
        url = getLoggerUrl(self._ctx)
        dialog.Title = url
        self._setDialogText(dialog, url)
        dialog.execute()
        dialog.dispose()

    def _clearLog(self, dialog):
        try:
            clearLogger()
            msg = getMessage(self._ctx, g_message, 101)
            logMessage(self._ctx, INFO, msg, 'OptionsDialog', '_clearLog()')
            url = getLoggerUrl(self._ctx)
            self._setDialogText(dialog, url)
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, "OptionsDialog", "_clearLog()")

    def _logInfo(self, dialog):
        version  = ' '.join(sys.version.split())
        msg = getMessage(self._ctx, g_message, 111, version)
        logMessage(self._ctx, INFO, msg, "OptionsDialog", "_logInfo()")
        path = os.pathsep.join(sys.path)
        msg = getMessage(self._ctx, g_message, 112, path)
        logMessage(self._ctx, INFO, msg, "OptionsDialog", "_logInfo()")
        msg = getMessage(self._ctx, g_message, 113, requests.__version__)
        logMessage(self._ctx, INFO, msg, "OptionsDialog", "_logInfo()")
        try:
            import urllib3
        except ImportError as e:
            msg = getMessage(self._ctx, g_message, 114, getExceptionMessage(e))
        else:
            msg = getMessage(self._ctx, g_message, 115, urllib3.__version__)
        logMessage(self._ctx, INFO, msg, "OptionsDialog", "_logInfo()")
        try:
            import chardet
        except ImportError as e:
            msg = getMessage(self._ctx, g_message, 116, getExceptionMessage(e))
        else:
            msg = getMessage(self._ctx, g_message, 117, chardet.__version__)
        logMessage(self._ctx, INFO, msg, "OptionsDialog", "_logInfo()")
        try:
            import ssl
        except ImportError as e:
            msg = getMessage(self._ctx, g_message, 118, getExceptionMessage(e))
        else:
            msg = getMessage(self._ctx, g_message, 119, ssl.OPENSSL_VERSION)
        logMessage(self._ctx, INFO, msg, "OptionsDialog", "_logInfo()")
        url = getLoggerUrl(self._ctx)
        self._setDialogText(dialog, url)

    def _setDialogText(self, dialog, url):
        control = dialog.getControl('TextField1')
        length, sequence = getFileSequence(self._ctx, url)
        control.Text = sequence.value.decode('utf-8')
        selection = uno.createUnoStruct('com.sun.star.awt.Selection', length, length)
        control.setSelection(selection)

    def _loadLoggerSetting(self, dialog):
        enabled, index, handler = getLoggerSetting(self._ctx)
        dialog.getControl('CheckBox1').State = int(enabled)
        dialog.getControl('ListBox1').selectItemPos(index, True)
        dialog.getControl('OptionButton%s' % handler).State = 1
        self._toggleLogger(dialog, enabled)

    def _saveLoggerSetting(self, dialog):
        enabled = bool(dialog.getControl('CheckBox1').State)
        index = dialog.getControl('ListBox1').getSelectedItemPos()
        handler = dialog.getControl('OptionButton1').State
        setLoggerSetting(self._ctx, enabled, index, handler)

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
