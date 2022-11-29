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

from com.sun.star.frame.DispatchResultState import SUCCESS
from com.sun.star.frame.DispatchResultState import FAILURE

from com.sun.star.ui.dialogs.ExecutableDialogResults import OK

from .wizard import Wizard
from .wizard import WizardController

from .configuration import g_wizard_page
from .configuration import g_wizard_paths

import traceback


# Show the OAuth2OOo Wizard
def showOAuth2Wizard(ctx, model, parent):
    try:
        state = FAILURE
        result = ()
        msg = "Retrieving Authorization Code ..."
        print("OAuth2Helper.showOAuth2Wizard() 1")
        wizard = Wizard(ctx, g_wizard_page, True, parent)
        print("OAuth2Helper.showOAuth2Wizard() 2")
        controller = WizardController(ctx, wizard, model)
        print("OAuth2Helper.showOAuth2Wizard() 3")
        arguments = (g_wizard_paths, controller)
        print("OAuth2Helper.showOAuth2Wizard() 4")
        wizard.initialize(arguments)
        print("OAuth2Helper.showOAuth2Wizard() 5")
        if wizard.execute() == OK:
            msg +=  " Retrieving Authorization Code ... Done"
            state = SUCCESS
            result = (controller.Url, controller.User, controller.Token)
        else:
            msg +=  " ERROR: Wizard as been aborted"
        controller.dispose()
        print("OAuth2Helper.showOAuth2Wizard() 6 %s" % msg)
        return state, result
    except Exception as e:
        msg = "Error: %s - %s" % (e, traceback.print_exc())
        print(msg)
