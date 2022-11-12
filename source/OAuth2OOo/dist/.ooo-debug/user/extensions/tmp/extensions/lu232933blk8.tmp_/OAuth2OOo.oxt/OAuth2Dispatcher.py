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

from com.sun.star.frame import XDispatchProvider

from com.sun.star.lang import XInitialization
from com.sun.star.lang import XServiceInfo

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from oauth2 import OAuth2Dispatch

from oauth2 import getMessage
from oauth2 import logMessage
from oauth2 import g_identifier

from unolib import createService
from unolib import getDesktop

import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Dispatcher' % g_identifier


class OAuth2Dispatcher(unohelper.Base,
                       XDispatchProvider,
                       XInitialization,
                       XServiceInfo):
    def __init__(self, ctx):
        self._ctx = ctx
        self._frame = None
        logMessage(self._ctx, INFO, "Loading ... Done", 'OAuth2Dispatcher', '__init__()')

# XInitialization
    def initialize(self, args):
        if len(args) > 0:
            self._frame = args[0]

# XDispatchProvider
    def queryDispatch(self, url, frame, flags):
        dispatch = None
        if url.Path == 'wizard':
            desktop = getDesktop(self._ctx)
            #mri = createService(self._ctx, 'mytools.Mri')
            #mri.inspect(desktop)
            parent = self._frame.getContainerWindow()
            #mri.inspect(self._frame)
            dispatch = OAuth2Dispatch(self._ctx, parent)
        return dispatch

    def queryDispatches(self, requests):
        dispatches = []
        for request in requests:
            dispatch = self.queryDispatch(request.FeatureURL, request.FrameName, request.SearchFlags)
            dispatches.append(dispatch)
        return tuple(dispatches)

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OAuth2Dispatcher,                            # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName,))                    # List of implemented services