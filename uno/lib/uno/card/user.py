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

from .addressbook import AddressBooks

from .provider import Provider

from .oauth2 import getRequest
from .oauth2 import g_oauth2

from .dbconfig import g_user
from .dbconfig import g_schema

import traceback


def getUserUri(server, name):
    return server + '/' + name


class User(unohelper.Base):
    def __init__(self, ctx, database, scheme, server, name, pwd=''):
        self._ctx = ctx
        self._password = pwd
        self.Request = getRequest(ctx, server, name)
        self._metadata = database.selectUser(server, name)
        self._sessions = []
        new = self._metadata is None
        if new:
            provider = Provider(ctx, scheme, server)
            self._metadata = self._getNewUser(database, provider, scheme, server, name, pwd)
            self._initNewUser(database, provider)
        else:
            provider = Provider(ctx, self.Scheme, self.Server)
        self._provider = provider
        self._addressbooks = AddressBooks(ctx, self._metadata, new)

    @property
    def Id(self):
        return self._metadata.getValue('User')
    @property
    def Scheme(self):
        return self._metadata.getValue('Scheme')
    @property
    def Server(self):
        return self._metadata.getValue('Server')
    @property
    def Path(self):
        return self._metadata.getValue('Path')
    @property
    def Name(self):
        return self._metadata.getValue('Name')
    @property
    def Password(self):
        return self._password
    @property
    def Addressbooks(self):
        return self._addressbooks

# Procedures called by DataSource
    def getUri(self):
        return getUserUri(self.Server, self.Name)

    def getName(self):
        return g_user % self.Id

    def getPassword(self):
        password = ''
        return password

    def getSchema(self):
        return self.Name.replace('.','-')

    def hasSession(self):
        return len(self._sessions) > 0

    def addSession(self, session):
        self._sessions.append(session)

    def removeSession(self, session):
        if session in self._sessions:
            self._sessions.remove(session)

    def initAddressbooks(self, database):
        self._provider.initAddressbooks(database, self)

    def unquoteUrl(self, url):
        return self.Request.unquoteUrl(url)

    def addAddressbook(self, aid):
        pass
        #if aid not in self._addressbooks:
        #    self._addressbooks.append(aid)

    def removeAddressbook(self, aid):
        pass
        #if aid in self._addressbooks:
        #    print("User.removeAddressbook() 1 %s" % (self._addressbooks, ))
        #    self._addressbooks.remove(aid)

    def getAddressbooks(self):
        return self._addressbooks.getAddressbooks()

    def isOffLine(self):
        return self._provider.isOffLine()

    def firstCardPull(self, database, addressbook):
        return self._provider.firstCardPull(database, self, addressbook)

    def pullCardByToken(self, database, addressbook, dltd, mdfd):
        token, deleted, modified = self._provider.getCardByToken(self, addressbook)
        if addressbook.Token != token:
            if deleted:
                dltd += database.deleteCard(addressbook.Id, deleted)
            if modified:
                mdfd += self._provider.mergeCardByToken(database, self, addressbook)
            database.updateAddressbookToken(addressbook.Id, token)
        return dltd, mdfd

    def getModifiedCard(self, path, urls):
        return self._provider.getModifiedCard(self.Request, self.Name, self.Password, path, urls)

    def _isNewUser(self):
        return self._metadata is None

    def _getNewUser(self, database, provider, scheme, server, name, pwd):
        if self.Request is None:
            raise self._provider.getSqlException(1003, 1105, '_getNewUser', g_oauth2)
        if provider.isOffLine():
            raise self._provider.getSqlException(1004, 1108, '_getNewUser', name)
        return provider.insertUser(database, self.Request, scheme, server, name, pwd)

    def _initNewUser(self, database, provider):
        name = self.getName()
        if not database.createUser(name, self.getPassword()):
            raise provider.getSqlException(1005, 1106, '_initNewUser', name)
        database.createUserSchema(self.getSchema(), name)

