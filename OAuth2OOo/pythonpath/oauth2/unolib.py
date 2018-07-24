#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XInitialization
from com.sun.star.beans import XPropertySet, XPropertySetInfo
from com.sun.star.task import XInteractionHandler


class PyInteractionHandler(unohelper.Base, XInteractionHandler):
    # XInteractionHandler
    def handle(self, requester):
        pass


class PyPropertySetInfo(unohelper.Base, XPropertySetInfo):
    def __init__(self, properties={}):
        self.properties = properties

    # XPropertySetInfo
    def getProperties(self):
        return tuple(self.properties.values())
    def getPropertyByName(self, name):
        return self.properties[name] if name in self.properties else None
    def hasPropertyByName(self, name):
        return name in self.properties


class PyInitialization(XInitialization):
    # XInitialization
    def initialize(self, namedvalues=()):
        for namedvalue in namedvalues:
            if hasattr(namedvalue, 'Name') and hasattr(namedvalue, 'Value'):
                self.setPropertyValue(namedvalue.Name, namedvalue.Value)


class PyPropertySet(XPropertySet):
    def __init__(self, properties={}):
        self.properties = properties

    # XPropertySet
    def getPropertySetInfo(self):
        return PyPropertySetInfo(self.properties)
    def setPropertyValue(self, name, value):
        if name in self.properties and hasattr(self, name):
            setattr(self, name, value)
    def getPropertyValue(self, name):
        value = None
        if name in self.properties and hasattr(self, name):
            value = getattr(self, name)
        return value
    def addPropertyChangeListener(self, name, listener):
        pass
    def removePropertyChangeListener(self, name, listener):
        pass
    def addVetoableChangeListener(self, name, listener):
        pass
    def removeVetoableChangeListener(self, name, listener):
        pass
