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

from com.sun.star.frame.DispatchResultState import FAILURE

from com.sun.star.frame import FeatureStateEvent

from com.sun.star.frame import XNotifyingDispatch

from .wizard import showOAuth2Wizard

from .unotool import createMessageBox
from .unotool import getStringResource

from .configuration import State
from .configuration import g_identifier

import traceback


class Dispatch(unohelper.Base,
               XNotifyingDispatch):
    def __init__(self, ctx, frame):
        self._ctx = ctx
        self._frame = frame
        self._listeners = []
        self._resources = {'Title': 'Dispatch.ErrorBox.Title',
                           'Message': 'Dispatch.ErrorBox.Message'}

# XNotifyingDispatch
    def dispatchWithNotification(self, uri, arguments, listener):
        state, result = self.dispatch(uri, arguments)
        struct = 'com.sun.star.frame.DispatchResultEvent'
        notification = uno.createUnoStruct(struct, self, state, result)
        listener.dispatchFinished(notification)

    def dispatch(self, uri, arguments):
        state = FAILURE
        result = ()
        if State.restart:
            self._showMessageBox()
        elif uri.Path == 'Wizard':
            state, result = showOAuth2Wizard(self._ctx, **arguments)
        return state, result

    def addStatusListener(self, listener, url):
        state = FeatureStateEvent()
        state.FeatureURL = url
        state.IsEnabled = True
        #state.State = True
        listener.statusChanged(state)
        self._listeners.append(listener)

    def removeStatusListener(self, listener, url):
        if listener in self._listeners:
            self._listeners.remove(listener)

    # Show MessageBox Error
    def _showMessageBox(self):
        resolver = getStringResource(self._ctx, g_identifier, 'dialogs', 'MessageBox')
        title = resolver.resolveString(self._resources.get('Title'))
        message = resolver.resolveString(self._resources.get('Message'))
        dialog = createMessageBox(self._ctx, title, message)
        dialog.execute()
        dialog.dispose()

