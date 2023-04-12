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

from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.ucb.ConnectionMode import OFFLINE
from com.sun.star.ucb.ConnectionMode import ONLINE

from .unotool import getConnectionMode

from .dbtool import getSqlException

from .logger import getLogger

from .configuration import g_path
from .configuration import g_errorlog
from .configuration import g_basename

import traceback


class ProviderBase(unohelper.Base):

    @property
    def Host(self):
        return self._server
    @property
    def BaseUrl(self):
        return self._scheme + self._server + g_path

    def isOnLine(self):
        return getConnectionMode(self._ctx, self.Host) != OFFLINE
    def isOffLine(self):
        return getConnectionMode(self._ctx, self.Host) != ONLINE

    def getSqlException(self, state, code, method, *args):
        logger = getLogger(self._ctx, g_errorlog, g_basename)
        state = logger.resolveString(state)
        msg = logger.resolveString(code, *args)
        logger.logp(SEVERE, g_basename, method, msg)
        error = getSqlException(state, code, msg, self)
        return error

    # Need to be implemented method
    def insertUser(self, database, request, scheme, server, name, pwd):
        raise NotImplementedError

    def initAddressbooks(self, database, user, request):
        raise NotImplementedError

    def getAddressbookUrl(self, request, addressbook, user, password, url):
        raise NotImplementedError

    def firstCardPull(self, database, user, addressbook):
        raise NotImplementedError

    def getModifiedCardByToken(self, request, user, password, url, token):
        raise NotImplementedError

    def getModifiedCard(self, request, user, password, url, urls):
        raise NotImplementedError

