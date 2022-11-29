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

from com.sun.star.frame import XNotifyingDispatch

from com.sun.star.frame.DispatchResultState import SUCCESS
from com.sun.star.frame.DispatchResultState import FAILURE

from .oauth2model import OAuth2Model
from .oauth2helper import showOAuth2Wizard

import traceback


class OAuth2Dispatch(unohelper.Base,
                     XNotifyingDispatch):
    def __init__(self, ctx, parent):
        self._ctx = ctx
        self._parent = parent
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
        if uri.Path == 'wizard':
            url = user = ''
            close = True
            for argument in arguments:
                if argument.Name == 'Url':
                    url = argument.Value
                elif argument.Name == 'UserName':
                    user = argument.Value
                elif argument.Name == 'Close':
                    close = argument.Value
            model = OAuth2Model(self._ctx, close, url, user)
            state, result = showOAuth2Wizard(self._ctx, model, self._parent)
        return state, result

    def addStatusListener(self, listener, url):
        pass

    def removeStatusListener(self, listener, url):
        pass

