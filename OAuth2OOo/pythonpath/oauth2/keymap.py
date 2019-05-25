#!
# -*- coding: utf_8 -*-

import unohelper

from com.sun.star.container import NoSuchElementException
from com.sun.star.lang import IndexOutOfBoundsException

from com.sun.star.auth import XRestKeyMap

from collections import OrderedDict
import json


class KeyMap(unohelper.Base,
             XRestKeyMap):
    def __init__(self, **kwargs):
        self._value = OrderedDict(kwargs)

    def _getValue(self, key):
        value = self._value[key]
        if isinstance(value, dict):
            return KeyMap(**value)
        elif isinstance(value, list):
            return tuple(value)
        return value

    # XStringKeyMap
    @property
    def Count(self):
        return len(self._value)

    def getValue(self, key):
        if key in self._value:
            return self._getValue(key)
        print("KeyMap.getValue() Error: %s  **************************************" % key)
        raise NoSuchElementException()

    def hasValue(self, key):
        return key in self._value

    def insertValue(self, key, value):
        self._value[key] = value

    def getKeyByIndex(self, i):
        if 0 <= i < self.Count:
            return list(self._value.keys())[i]
        raise IndexOutOfBoundsException()

    def getValueByIndex(self, i):
        key = self.getKeyByIndex(i)
        return self._getValue(key)

    # XRestKeyMap
    def getDefaultValue(self, key, default=None):
        if key in self._value:
            return self._getValue(key)
        else:
            return default

    def fromJson(self, jsonstr):
        self._value = json.loads(jsonstr)
    def fromJsonKey(self, jsonstr, key):
        self._value[key] = json.loads(jsonstr)

    def toJson(self):
        return json.dumps(self._value)
    def toJsonKey(self, key):
        return json.dumps(self._value[key])
