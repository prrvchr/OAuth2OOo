#!
# -*- coding: utf_8 -*-

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

from com.sun.star.frame import XNotifyingDispatch

from com.sun.star.frame.DispatchResultState import SUCCESS
from com.sun.star.frame.DispatchResultState import FAILURE

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from oauth2 import Wizard
from oauth2 import WizardController
from oauth2 import g_wizard_page
from oauth2 import g_wizard_paths

import traceback


class OAuth2Dispatch(unohelper.Base,
                     XNotifyingDispatch):
    def __init__(self, ctx, parent):
        self._ctx = ctx
        self._parent = parent
        self._listeners = []

# XNotifyingDispatch
    def dispatchWithNotification(self, url, arguments, listener):
        state, result = self.dispatch(url, arguments)
        notification = uno.createUnoStruct('com.sun.star.frame.DispatchResultEvent')
        notification.Source = self
        notification.State = state
        notification.Result =  result
        listener.dispatchFinished(notification)

    def dispatch(self, url, arguments):
        state = SUCCESS
        result = ()
        if url.Path == 'wizard':
            state, result = self._showWizard(arguments)
        return state, result

    def addStatusListener(self, listener, url):
        pass

    def removeStatusListener(self, listener, url):
        pass

# OAuth2Dispatch private methods
    #Wizard methods
    def _showWizard(self, arguments):
        try:
            state = FAILURE
            result = ()
            close = True
            msg = ''
            for argument in arguments:
                if argument.Name == 'Url':
                    url = argument.Value
                elif argument.Name == 'UserName':
                    name = argument.Value
                elif argument.Name == 'Close':
                    close = argument.Value
            print("OAuth2Dispatch._showWizard() 1")
            wizard = Wizard(self._ctx, g_wizard_page, True, self._parent)
            print("OAuth2Dispatch._showWizard() 2")
            controller = WizardController(self._ctx, wizard, None, url, name, close)
            print("OAuth2Dispatch._showWizard() 3")
            arguments = (g_wizard_paths, controller)
            print("OAuth2Dispatch._showWizard() 4")
            wizard.initialize(arguments)
            print("OAuth2Dispatch._showWizard() 5")
            if wizard.execute() == OK:
                msg +=  " Retrieving Authorization Code ..."
                if controller.Error:
                    msg += " ERROR: cant retrieve Authorization Code: %s" % controller.Error
                else:
                    msg += " Done"
                    state = SUCCESS
                    result = (controller.ResourceUrl, controller.UserName)
            else:
                msg +=  " ERROR: Wizard as been aborted"
                controller.Server.cancel()
            wizard.DialogWindow.dispose()
            print("OAuth2Dispatch._showWizard() 6 %s" % msg)
            return state, result
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            print(msg)
