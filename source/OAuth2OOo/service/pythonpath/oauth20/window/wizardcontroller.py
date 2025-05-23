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

from com.sun.star.ui.dialogs import XWizardController

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .wizardmodel import WizardModel

from .page1 import OAuth2Manager as WizardPage1
from .page2 import OAuth2Manager as WizardPage2
from .page3 import OAuth2Manager as WizardPage3
from .page4 import OAuth2Manager as WizardPage4

from ..unotool import getStringResource

from ..logger import getLogger

from ..configuration import g_identifier
from ..configuration import g_defaultlog
from ..configuration import g_basename

import traceback


class WizardController(unohelper.Base,
                       XWizardController):
    def __init__(self, ctx, wizard, close, readonly, url, user):
        self._ctx = ctx
        self._wizard = wizard
        self._model = WizardModel(ctx, close, readonly, url, user)
        self._resolver = getStringResource(ctx, g_identifier, 'dialogs', 'WizardController')
        self._logger = getLogger(ctx, g_defaultlog, g_basename)

    @property
    def User(self):
        return self._model.User
    @property
    def Url(self):
        return self._model.Url
    @property
    def Token(self):
        return self._model.getAccessToken(self._wizard)

    def dispose(self):
        self._model.dispose()
        self._wizard.DialogWindow.dispose()

# XWizardController
    def createPage(self, parent, pageid):
        msg = "PageId: %s ..." % pageid
        if pageid == 1:
            page = WizardPage1(self._ctx, self._wizard, self._model, pageid, parent)
        elif pageid == 2:
            page = WizardPage2(self._ctx, self._wizard, self._model, pageid, parent)
        elif pageid == 3:
            page = WizardPage3(self._ctx, self._wizard, self._model, pageid, parent)
        elif pageid == 4:
            page = WizardPage4(self._ctx, self._wizard, self._model, pageid, parent)
        msg += " Done"
        self._logger.logp(INFO, 'WizardController', 'createPage()', msg)
        return page

    def getPageTitle(self, pageid):
        return self._model.getPageStep(self._resolver, pageid)

    def canAdvance(self):
        return True

    def onActivatePage(self, pageid):
        msg = "PageId: %s..." % pageid
        title = self._model.getPageTitle(self._resolver, pageid)
        self._wizard.setTitle(title)
        backward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.PREVIOUS')
        forward = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.NEXT')
        finish = uno.getConstantByName('com.sun.star.ui.dialogs.WizardButton.FINISH')
        msg += " Done"
        self._logger.logp(INFO, 'WizardController', 'onActivatePage()', msg)

    def onDeactivatePage(self, pageid):
        pass

    def confirmFinish(self):
        return True

