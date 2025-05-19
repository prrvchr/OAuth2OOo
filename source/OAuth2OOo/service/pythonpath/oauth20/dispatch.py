#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from com.sun.star.frame.DispatchResultState import SUCCESS
from com.sun.star.frame.DispatchResultState import FAILURE

from com.sun.star.frame import XNotifyingDispatch

from .wizard import Wizard
from .window import WizardController

from .unotool import createService
from .unotool import getConfiguration

from .configuration import g_wizard_paths
from .configuration import g_wizard_page
from .configuration import g_identifier

import traceback


class Dispatch(unohelper.Base,
               XNotifyingDispatch):
    def __init__(self, ctx, frame):
        self._ctx = ctx
        self._frame = frame
        self._listeners = []

# XNotifyingDispatch
    def dispatchWithNotification(self, uri, arguments, listener):
        state, result = self.dispatch(uri, arguments)
        struct = 'com.sun.star.frame.DispatchResultEvent'
        notification = uno.createUnoStruct(struct, self, state, result)
        listener.dispatchFinished(notification)

    def dispatch(self, uri, arguments):
        state = FAILURE
        result = ()
        if uri.Path == 'Wizard':
            url = user = ''
            readonly = False
            close = True
            for argument in arguments:
                if argument.Name == 'Url':
                    url = argument.Value
                elif argument.Name == 'UserName':
                    user = argument.Value
                elif argument.Name == 'ReadOnly':
                    readonly = argument.Value
                elif argument.Name == 'Close':
                    close = argument.Value
            state, result = self._showOAuth2Wizard(close, readonly, url, user)
        return state, result

    def addStatusListener(self, listener, url):
        pass

    def removeStatusListener(self, listener, url):
        pass

    # Show the OAuth2OOo Wizard
    def _showOAuth2Wizard(self, close, readonly, url, user):
        state = FAILURE
        result = ()
        unowizard = getConfiguration(self._ctx, g_identifier).getByName('UnoWizard')
        if unowizard:
            wizard = createService(self._ctx, 'com.sun.star.ui.dialogs.Wizard')
        else:
            window = self._frame.getContainerWindow().getToolkit().getActiveTopWindow()
            wizard = Wizard(self._ctx, g_wizard_page, True, window)
        controller = WizardController(self._ctx, wizard, close, readonly, url, user)
        if unowizard:
            arguments = ((uno.Any('[][]short', g_wizard_paths), controller), )
            uno.invoke(wizard, 'initialize', arguments)
        else:
            arguments = (g_wizard_paths, controller)
            wizard.initialize(arguments)
        if wizard.execute() == OK:
            state = SUCCESS
            result = (controller.Url, controller.User, controller.Token)
        controller.dispose()
        return state, result

