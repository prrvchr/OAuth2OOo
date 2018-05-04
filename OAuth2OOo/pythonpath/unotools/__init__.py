#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo, XInitialization
from com.sun.star.beans import XPropertySet, XPropertySetInfo
from com.sun.star.task import XInteractionHandler
from com.sun.star.logging import XLogHandler, XLogFormatter
from com.sun.star.awt import XRequestCallback

import binascii


def getLogger(ctx, logger="org.openoffice.logging.DefaultLogger"):
    pool = ctx.getValueByName("/singletons/com.sun.star.logging.LoggerPool")
    return pool.getNamedLogger(logger)

def getLoggerSettings(ctx, logger="org.openoffice.logging.DefaultLogger"):
    nodepath = "/org.openoffice.Office.Logging/Settings"
    configuration = getConfiguration(ctx, nodepath, True)
    if not configuration.hasByName(logger):
        configuration.insertByName(logger, configuration.createInstance())
        configuration.commitChanges()
    nodepath += "/%s" % logger
    return getConfiguration(ctx, nodepath, True)

def getLogLevel(ctx, logger="org.openoffice.logging.DefaultLogger"):
    settings = getLoggerSettings(ctx, logger)
    level = settings.LogLevel
    return level

def getLogLevels():
    levels = (uno.getConstantByName("com.sun.star.logging.LogLevel.SEVERE"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.WARNING"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.INFO"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.CONFIG"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.FINE"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.FINER"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.FINEST"),
              uno.getConstantByName("com.sun.star.logging.LogLevel.ALL"))
    return levels

def getLogHandler(ctx, logger="org.openoffice.logging.DefaultLogger"):
    settings = getLoggerSettings(ctx, logger)
    handler = settings.DefaultHandler
    return 1 if handler != "com.sun.star.logging.FileHandler" else 2

def getLogUrl(ctx, logger="org.openoffice.logging.DefaultLogger"):
    url = "$(userurl)/$(loggername).log"
    configuration = getLoggerSettings(ctx, logger)
    settings = configuration.getByName("HandlerSettings")
    if settings.hasByName("FileURL"):
        url = settings.getByName("FileURL")
    service = ctx.ServiceManager.createInstance("com.sun.star.util.PathSubstitution")
    return service.substituteVariables(url.replace("$(loggername)", logger), True)

def setLogLevel(ctx, level, logger="org.openoffice.logging.DefaultLogger"):
    settings = getLoggerSettings(ctx, logger)
    settings.LogLevel = level
    settings.commitChanges()

def logToConsole(ctx, threshold=None, logger="org.openoffice.logging.DefaultLogger"):
    configuration = getLoggerSettings(ctx, logger)
    configuration.DefaultHandler = "com.sun.star.logging.ConsoleHandler"
    if threshold is not None:
        settings = configuration.getByName("HandlerSettings")
        if settings.hasByName("Threshold"):
            settings.replaceByName("Threshold", threshold)
        else:
            settings.insertByName("Threshold", threshold)
    configuration.commitChanges()

def logToFile(ctx, url=None, logger="org.openoffice.logging.DefaultLogger"):
    configuration = getLoggerSettings(ctx, logger)
    configuration.DefaultHandler = "com.sun.star.logging.FileHandler"
    if url is not None:
        settings = configuration.getByName("HandlerSettings")
        if settings.hasByName("FileURL"):
            settings.replaceByName("FileURL", url)
        else:
            settings.insertByName("FileURL", url)
    configuration.commitChanges()

def getProperty(name, typename, attributes, handle=-1):
    return uno.createUnoStruct("com.sun.star.beans.Property",
                               name,
                               handle,
                               uno.getTypeByName(typename),
                               attributes)

def getResourceLocation(ctx, path="OAuth2OOo"):
    identifier = "com.gmail.prrvchr.extensions.OAuth2OOo"
    service = "/singletons/com.sun.star.deployment.PackageInformationProvider"
    provider = ctx.getValueByName(service)
    return "%s/%s" % (provider.getPackageLocation(identifier), path)

def getConfiguration(ctx, nodepath, update=False):
    service = "com.sun.star.configuration.ConfigurationProvider"
    provider = ctx.ServiceManager.createInstance(service)
    service = "com.sun.star.configuration.ConfigurationUpdateAccess" if update else \
              "com.sun.star.configuration.ConfigurationAccess"
    arguments = (uno.createUnoStruct("com.sun.star.beans.NamedValue", "nodepath", nodepath), )
    return provider.createInstanceWithArguments(service, arguments)

def getCurrentLocale(ctx):
    service = "/org.openoffice.Setup/L10N"
    parts = getConfiguration(ctx, service).getByName("ooLocale").split("-")
    locale = uno.createUnoStruct("com.sun.star.lang.Locale", parts[0], "", "")
    if len(parts) > 1:
        locale.Country = parts[1]
    else:
        service = ctx.ServiceManager.createInstance("com.sun.star.i18n.LocaleData")
        locale.Country = service.getLanguageCountryInfo(locale).Country
    return locale

def getStringResource(ctx, locale=None, filename="DialogStrings"):
    service = "com.sun.star.resource.StringResourceWithLocation"
    location = getResourceLocation(ctx)
    if locale is None:
        locale = getCurrentLocale(ctx)
    arguments = (location, True, locale, filename, "", PyInteractionHandler())
    return ctx.ServiceManager.createInstanceWithArgumentsAndContext(service, arguments, ctx)

def generateUuid():
    return binascii.hexlify(uno.generateUuid().value).decode("utf-8")

def createMessageBox(peer, message, title, box="message", buttons=2):
    boxtypes = {"message": "MESSAGEBOX", "info": "INFOBOX", "warning": "WARNINGBOX",
                "error": "ERRORBOX", "query": "QUERYBOX"}
    box = uno.Enum("com.sun.star.awt.MessageBoxType", boxtypes[box] if box in boxtypes else "MESSAGEBOX")
    return peer.getToolkit().createMessageBox(peer, box, buttons, title, message)

def createService(ctx, name, **args):
    if args:
        arguments = []
        for key, value in args.items():
            arguments.append(uno.createUnoStruct("com.sun.star.beans.NamedValue", key, value))
    if args:
        service = ctx.ServiceManager.createInstanceWithArgumentsAndContext(name, tuple(arguments), ctx)
    else:
        service = ctx.ServiceManager.createInstanceWithContext(name, ctx)
    return service


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


class PyServiceInfo(XServiceInfo):
    # XServiceInfo
    def supportsService(self, service):
        return unohelper.ImplementationHelper().supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return unohelper.ImplementationHelper().getSupportedServiceNames(g_ImplementationName)


class PyInitialization(XInitialization):
    # XInitialization
    def initialize(self, namedvalues=()):
        for namedvalue in namedvalues:
            if hasattr(namedvalue, "Name") and hasattr(namedvalue, "Value"):
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
