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

import unohelper

from com.sun.star.awt import XContainerWindowEventHandler

import traceback


class WindowHandler(unohelper.Base,
                    XContainerWindowEventHandler):
    def __init__(self, manager):
        self._manager = manager

    # XContainerWindowEventHandler
    def callHandlerMethod(self, window, event, method):
        try:
            handled = False
            if method == 'SetUser':
                self._manager.setUser(event.Source.Text.strip())
                handled = True
            elif method == 'SetUrl':
                control = event.Source
                item = control.Text.strip()
                # TODO: OpenOffice has strange behavior if StringItemList is empty
                items = control.getItems() if control.getItemCount() > 0 else ()
                self._manager.setUrl(item, item in items)
                handled = True
            elif method == 'AddUrl':
                self._manager.addUrl()
                handled = True
            elif method == 'SaveUrl':
                self._manager.saveUrl()
                handled = True
            elif method == 'RemoveUrl':
                self._manager.removeUrl()
                handled = True
            elif method == 'SetProvider':
                control = event.Source
                item = control.Text.strip()
                # TODO: OpenOffice has strange behavior if StringItemList is empty
                items = control.getItems() if control.getItemCount() > 0 else ()
                self._manager.setProvider(item, item in items)
                handled = True
            elif method == 'AddProvider':
                self._manager.addProvider()
                handled = True
            elif method == 'EditProvider':
                self._manager.editProvider()
                handled = True
            elif method == 'RemoveProvider':
                self._manager.removeProvider()
                handled = True
            elif method == 'SetScope':
                control = event.Source
                item = control.Text.strip()
                # TODO: OpenOffice has strange behavior if StringItemList is empty
                items = control.getItems() if control.getItemCount() > 0 else ()
                self._manager.setScope(item, item in items)
                handled = True
            elif method == 'AddScope':
                self._manager.addScope()
                handled = True
            elif method == 'EditScope':
                self._manager.editScope()
                handled = True
            elif method == 'RemoveScope':
                self._manager.removeScope()
                handled = True
            return handled
        except Exception as e:
            msg = "Error: %s" % traceback.print_exc()
            print(msg)

    def getSupportedMethodNames(self):
        return ('SetUser',
                'SetUrl',
                'AddUrl',
                'SaveUrl',
                'RemoveUrl',
                'SetProvider',
                'AddProvider',
                'EditProvider',
                'RemoveProvider',
                'SetScope',
                'AddScope',
                'EditScope',
                'RemoveScope')
