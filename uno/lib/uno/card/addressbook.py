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

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .dbtool import getSqlException

from .unotool import createService

from .logger import getLogger

from .configuration import g_errorlog
from .configuration import g_basename

from collections import OrderedDict
import traceback


class AddressBooks(unohelper.Base):
    def __init__(self, ctx, metadata, new):
        self._ctx = ctx
        print("AddressBooks.__init__() 1")
        self._addressbooks = self._getAddressbooks(metadata, new)
        print("AddressBooks.__init__() 2")

    def initAddressbooks(self, database, user, addressbooks):
        #mri = createService(self._ctx, 'mytools.Mri')
        #mri.inspect(addressbooks)
        changed = False
        for abook in addressbooks:
            name, url, tag, token = self._getAddressbookData(abook)
            print("AddressBooks.initAddressbooks() 1 Name: %s - Url: %s - Tag: %s - Token: %s" % (name, url, tag, token))
            if self._hasAddressbook(url):
                addressbook = self._getAddressbook(url)
                if addressbook.hasNameChanged(name):
                    database.updateAddressbookName(addressbook.Id, name)
                    addressbook.setName(name)
                    changed = True
                    print("AddressBooks.initAddressbooks() 2 %s" % (name, ))
            else:
                index = database.insertAddressbook(user, url, name, tag, token)
                addressbook = AddressBook(self._ctx, index, url, name, tag, token, True)
                self._addressbooks[url] = addressbook
                changed = True
                print("AddressBooks.initAddressbooks() 3 %s - %s - %s" % (index, name, url))
        print("AddressBooks.initAddressbooks() 4")
        return changed

    def getAddressbooks(self):
        return self._addressbooks.values()

    # Private methods
    def _getAddressbookData(self, abook):
        return abook.getValue('Name'), abook.getValue('Url'), abook.getValue('Tag'), abook.getValue('Token')

    def _hasAddressbook(self, url):
        return url in self._addressbooks

    def _getAddressbook(self, url):
        return self._addressbooks[url]

    def _getAddressbooks(self, metadata, new):
        i = 0
        addressbooks = OrderedDict()
        indexes, names, tags, tokens = self._getAddressbookMetaData(metadata)
        for url in metadata.getValue('Paths'):
            # FIXME: If url is None we don't add this addressbook
            if url is None:
                continue
            print("AddressBook._getAddressbooks() Url: %s - Name: %s - Index: %s - Tag: %s - Token: %s" % (url, names[i], indexes[i], tags[i], tokens[i]))
            addressbooks[url] = AddressBook(self._ctx, indexes[i], url, names[i], tags[i], tokens[i], new)
            i += 1
        return addressbooks

    def _getAddressbookMetaData(self, data):
        return data.getValue('Addressbooks'), data.getValue('Names'), data.getValue('Tags'), data.getValue('Tokens')


class AddressBook(unohelper.Base):
    def __init__(self, ctx, index, url, name, tag, token, new=False):
        self._ctx = ctx
        self._index = index
        self._url = url
        self._name = name
        self._tag = tag
        self._token = token
        self._new = new

    @property
    def Id(self):
        return self._index
    @property
    def Path(self):
        return self._url
    @property
    def Name(self):
        return self._name
    @property
    def Tag(self):
        return self._tag
    @property
    def Token(self):
        return self._token

    def isNew(self):
        new = self._new
        self._new = False
        return new

    def hasNameChanged(self, name):
        return self.Name != name

    def setName(self, name):
        self.Name = name
