#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-24 https://prrvchr.github.io                                  ║
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

import unohelper

from com.sun.star.ui.dialogs import XWizardPage

from .oauth2handler import WindowHandler

from .oauth2view import OAuth2View

from ...unolib import PropertySet

from ...unotool import executeShell
from ...unotool import getProperty

import traceback


class OAuth2Manager(unohelper.Base,
                    XWizardPage,
                    PropertySet):
    def __init__(self, ctx, wizard, model, pageid, parent):
        self._ctx = ctx
        self._wizard = wizard
        self._model = model
        self._pageid = pageid
        self._view = OAuth2View(ctx, WindowHandler(self), parent)

# XWizardPage
    @property
    def PageId(self):
        return self._pageid
    @property
    def Window(self):
        return self._view.getWindow()

    def activatePage(self):
        self._view.setUrl(self._model.getAuthorizationUrl())

    def commitPage(self, reason):
        return True

    def canAdvance(self):
        return self._view.isAccepted()

# XComponent
    def dispose(self):
        pass
    def addEventListener(self, listener):
        pass
    def removeEventListener(self, listener):
        pass

# OAuth2Manager setter methods
    def acceptTerms(self):
        self._wizard.updateTravelUI()

    def loadTermsOfUse(self):
        executeShell(self._ctx, self._model.getTermsOfUse())

    def loadPrivacyPolicy(self):
        executeShell(self._ctx, self._model.getPrivacyPolicy())

    def _getPropertySetInfo(self):
        properties = {}
        ro = uno.getConstantByName('com.sun.star.beans.PropertyAttribute.READONLY')
        properties['PageId'] = getProperty('PageId', 'short', ro)
        properties['Window'] = getProperty('Window', 'com.sun.star.awt.XWindow', ro)
        return properties

