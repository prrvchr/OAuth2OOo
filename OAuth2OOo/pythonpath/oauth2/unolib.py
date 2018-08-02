#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XInitialization
from com.sun.star.beans import XPropertySet, XPropertySetInfo, UnknownPropertyException
from com.sun.star.task import XInteractionHandler


class InteractionHandler(unohelper.Base, XInteractionHandler):
    # XInteractionHandler
    def handle(self, requester):
        pass


class PropertySetInfo(unohelper.Base, XPropertySetInfo):
    def __init__(self, properties={}):
        self.properties = properties

    # XPropertySetInfo
    def getProperties(self):
        return tuple(self.properties.values())
    def getPropertyByName(self, name):
        return self.properties[name] if name in self.properties else None
    def hasPropertyByName(self, name):
        return name in self.properties


class Initialization(XInitialization):
    # XInitialization
    def initialize(self, namedvalues=()):
        for namedvalue in namedvalues:
            if hasattr(namedvalue, 'Name') and hasattr(namedvalue, 'Value'):
                self.setPropertyValue(namedvalue.Name, namedvalue.Value)


class PropertySet(XPropertySet):
    def _getPropertySetInfo(self):
        raise NotImplementedError

    # XPropertySet
    def getPropertySetInfo(self):
        properties = self._getPropertySetInfo()
        return PropertySetInfo(properties)
    def setPropertyValue(self, name, value):
        properties = self._getPropertySetInfo()
        if name in properties and hasattr(self, name):
            setattr(self, name, value)
        else:
            message = 'Cant setPropertyValue, UnknownProperty: %s - %s' % (name, value)
            raise UnknownPropertyException(message, self)
    def getPropertyValue(self, name):
        if name in self._getPropertySetInfo() and hasattr(self, name):
            return getattr(self, name)
        else:
            message = 'Cant getPropertyValue, UnknownProperty: %s' % name
            raise UnknownPropertyException(message, self)
    def addPropertyChangeListener(self, name, listener):
        pass
    def removePropertyChangeListener(self, name, listener):
        pass
    def addVetoableChangeListener(self, name, listener):
        pass
    def removeVetoableChangeListener(self, name, listener):
        pass
