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


# Get the OAuth2 Token, show Wizard or refresh Token if needed
def getAccessToken(ctx, model, parent):
    token = ''
    if not model.isAuthorized():
        token = _getTokenFromWizard(ctx, model, parent)
    elif model.isAccessTokenExpired():
        token = model.getRefreshedToken()
    else:
        token = model.getToken()
    return token

# Show the OAuth2OOo Wizard
def showOAuth2Wizard(ctx, model, parent):
    state = FAILURE
    result = ()
    print("oauth2helper.showOAuth2Wizard() 1")
    wizard = Wizard(ctx, g_wizard_page, True, parent)
    print("oauth2helper.showOAuth2Wizard() 2")
    controller = WizardController(ctx, wizard, model)
    print("oauth2helper.showOAuth2Wizard() 3")
    arguments = (g_wizard_paths, controller)
    wizard.initialize(arguments)
    print("oauth2helper.showOAuth2Wizard() 4")
    if wizard.execute() == OK:
        state = SUCCESS
        result = (controller.Url, controller.User, controller.Token)
    controller.dispose()
    print("oauth2helper.showOAuth2Wizard() 5")
    return state, result

def _getTokenFromWizard(ctx, model, parent):
    token = ''
    state, result = showOAuth2Wizard(ctx, model, parent)
    if state == SUCCESS:
        url, user, token = result
    return token

