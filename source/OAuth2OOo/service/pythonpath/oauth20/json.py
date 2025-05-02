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

from com.sun.star.container import XEnumeration
from com.sun.star.container import NoSuchElementException

from com.sun.star.json.JsonType import ARRAY
from com.sun.star.json.JsonType import BOOLEAN
from com.sun.star.json.JsonType import NULL
from com.sun.star.json.JsonType import NUMBER
from com.sun.star.json.JsonType import OBJECT
from com.sun.star.json.JsonType import STRING

from com.sun.star.json import XJsonValue
from com.sun.star.json import XJsonNumber
from com.sun.star.json import XJsonStructure
from com.sun.star.json import XJsonArray
from com.sun.star.json import XJsonObject
from com.sun.star.json import XJsonBuilder
from com.sun.star.json import XJsonArrayBuilder
from com.sun.star.json import XJsonObjectBuilder

from collections import OrderedDict
from six import string_types
from six import integer_types
import json
import traceback


def getJsonStructure(data, null=True):
    if isinstance(data, dict):
        return JsonObject(data)
    elif isinstance(data, (list, tuple)):
        return JsonArray(data)
    elif not null:
        return data
    else:
        return None


class JsonBuilder(unohelper.Base,
                  XJsonBuilder):

    #XJsonBuilder
    def createArray(self):
        return JsonArrayBuilder()

    def createObject(self):
        return JsonObjectBuilder()


class JsonValue(unohelper.Base,
                XJsonValue):
    def __init__(self, data, jsontype):
        self._data = data
        self._type = jsontype

    #XJsonValue
    def getValueType(self):
        return self._type


class JsonNumber(JsonValue,
                 XJsonNumber):
    def __init__(self, data):
        super(XJsonNumber, self).__init__(data, NUMBER)

    #XJsonNumber
    def isIntegral(self):
        return isinstance(self._data, int)

    def getShort(self):
        return int(self._data)

    def getLong(self):
        return int(self._data)

    def getHyper(self):
        return int(self._data)

    def getFloat(self):
        return float(self._data)

    def getDouble(self):
        return float(self._data)


class JsonStructure(JsonValue,
                    XJsonStructure):
    def __init__(self, data, jsontype):
        super(JsonValue, self).__init__(data, jsontype)

    #XJsonStructure
    def toJson(self):
        return json.dumps(self._data)

    def _getElementType(self, data):
        jsontype = NULL
        if isinstance(data, dict):
            jsontype = OBJECT
        elif isinstance(data, (list, tuple)):
            jsontype = ARRAY
        elif isinstance(data, string_types):
            jsontype = STRING
        elif isinstance(data, (integer_types, float)):
            jsontype = NUMBER
        elif isinstance(data, bool):
            jsontype = BOOLEAN
        return jsontype


class JsonArray(JsonStructure,
                XJsonArray):
    def __init__(self, data):
        super(JsonStructure, self).__init__(data, ARRAY)

    #XJsonArray
    @property
    def Count(self):
        return len(self._data)

    def getBoolean(self, index):
        return bool(self._data[index])

    def getString(self, index):
        return self._data[index]

    def getNumber(self, index):
        return JsonNumber(self._data[index])

    def getStructure(self, index):
        return getJsonStructure(self._data[index])

    def isNull(self, index):
        return self._data[index] is None

    def getElementType(self, index):
        return _getElementType(self._data[index])

    def createEnumeration(self):
        return Enumerator(self._data)


class JsonObject(JsonStructure,
                 XJsonObject):
    def __init__(self, data):
        super(JsonStructure, self).__init__(data, OBJECT)

    #XJsonObject
    def getBoolean(self, key):
        return bool(self._data[key])

    def getString(self, key):
        return self._data[key]

    def getNumber(self, key):
        return JsonNumber(self._data[key])

    def getStructure(self, key):
        return getJsonStructure(self._data[key])

    def isNull(self, key):
        return self._data[key] is None

    def getElementType(self, index):
        return _getElementType(self._data[key])

    def getElementNames(self):
        return tuple(self._data.keys())


class Enumerator(unohelper.Base,
                 XEnumeration):
    def __init__(self, data):
        self._data = data
        self._count = len(data)
        self._index = 0

    #XEnumeration
    def hasMoreElements(self):
        return self._index < self._count
    def nextElement(self):
        if not self.hasMoreElements():
            raise NoSuchElementException('Error: no more elements exist', self)
        index = self._index
        self._index += 1
        return getJsonStructure(self._data[index], False)


class JsonArrayBuilder(unohelper.Base,
                       XJsonArrayBuilder):
    def __init__(self):
        self._builders = []
        self._values = []

    #XJsonArrayBuilder
    def addShort(self, value):
        return self._addValue(value)

    def addLong(self, value):
        return self._addValue(value)

    def addHyper(self, value):
        return self._addValue(value)

    def addFloat(self, value):
        return self._addValue(value)

    def addDouble(self, value):
        return self._addValue(value)

    def addBoolean(self, value):
        return self._addValue(value)

    def addString(self, value):
        return self._addValue(value)

    def addArray(self, builder):
        return self._addBuilder(builder)

    def addObject(self, builder):
        return self._addBuilder(builder)

    def addNull(self):
        return self._addValue(None)

    def build(self):
        while len(self._builders) > 0:
            # FIXME: We need to build all builders only once
            index = self._builders.pop()
            builder = self._values[index]
            self._values[index] = json.loads(builder.build().toJson())
        return JsonArray(self._values)

    # Private method
    def _addBuilder(self, builder):
        self._builders.insert(0, len(self._values))
        return self._addValue(builder)

    def _addValue(self, value):
        self._values.append(value)
        return self


class JsonObjectBuilder(unohelper.Base,
                        XJsonObjectBuilder):
    def __init__(self):
        self._builders = []
        self._values = OrderedDict()

    #XJsonObjectBuilder
    def addShort(self, key, value):
        return self._addValue(key, value)

    def addLong(self, key, value):
        return self._addValue(key, value)

    def addHyper(self, key, value):
        return self._addValue(key, value)

    def addFloat(self, key, value):
        return self._addValue(key, value)

    def addDouble(self, key, value):
        return self._addValue(key, value)

    def addBoolean(self, key, value):
        return self._addValue(key, value)

    def addString(self, key, value):
        return self._addValue(key, value)

    def addArray(self, key, builder):
        return self._addBuilder(key, builder)

    def addObject(self, key, builder):
        return self._addBuilder(key, builder)

    def addNull(self, key):
        return self._addValue(key, None)

    def build(self):
        while len(self._builders) > 0:
            # FIXME: We need to build all builders only once
            key = self._builders.pop()
            builder = self._values[key]
            self._values[key] = json.loads(builder.build().toJson())
        return JsonObject(self._values)

    # Private getter method
    def _addBuilder(self, key, builder):
        self._builders.insert(0, key)
        return self._addValue(key, builder)

    def _addValue(self, key, value):
        self._values[key] = value
        return self

