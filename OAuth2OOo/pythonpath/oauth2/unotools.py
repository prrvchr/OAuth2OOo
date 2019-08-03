#!
# -*- coding: utf_8 -*-

import uno

import binascii

from com.sun.star.auth import OAuth2Request

from .unolib import InteractionHandler


def getSimpleFile(ctx):
    return ctx.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')

def getFileSequence(ctx, url, default=None):
    length, sequence = 0, uno.ByteSequence(b'')
    fs = getSimpleFile(ctx)
    if fs.exists(url):
        length, sequence = _getSequence(fs.openFileRead(url), fs.getSize(url))
    elif default is not None and fs.exists(default):
        length, sequence = _getSequence(fs.openFileRead(default), fs.getSize(default))
    return length, sequence

def _getSequence(inputstream, length):
    length, sequence = inputstream.readBytes(None, length)
    inputstream.closeInput()
    return length, sequence

def getProperty(name, type=None, attributes=None, handle=-1):
    property = uno.createUnoStruct('com.sun.star.beans.Property')
    property.Name = name
    property.Handle = handle
    if isinstance(type, uno.Type):
        property.Type = type
    elif type is not None:
        property.Type = uno.getTypeByName(type)
    if attributes is not None:
        property.Attributes = attributes
    return property

def getResourceLocation(ctx, identifier, path=None):
    service = '/singletons/com.sun.star.deployment.PackageInformationProvider'
    provider = ctx.getValueByName(service)
    location = provider.getPackageLocation(identifier)
    if path is not None:
        location += '/%s' % path
    return location

def getConfiguration(ctx, nodepath, update=False):
    service = 'com.sun.star.configuration.ConfigurationProvider'
    provider = ctx.ServiceManager.createInstance(service)
    service = 'com.sun.star.configuration.ConfigurationUpdateAccess' if update else \
              'com.sun.star.configuration.ConfigurationAccess'
    arguments = (uno.createUnoStruct('com.sun.star.beans.NamedValue', 'nodepath', nodepath), )
    return provider.createInstanceWithArguments(service, arguments)

def getCurrentLocale(ctx):
    service = '/org.openoffice.Setup/L10N'
    parts = getConfiguration(ctx, service).getByName('ooLocale').split('-')
    locale = uno.createUnoStruct('com.sun.star.lang.Locale', parts[0], '', '')
    if len(parts) > 1:
        locale.Country = parts[1]
    else:
        service = ctx.ServiceManager.createInstance('com.sun.star.i18n.LocaleData')
        locale.Country = service.getLanguageCountryInfo(locale).Country
    return locale

def getStringResource(ctx, identifier, path=None, filename='DialogStrings', locale=None):
    service = 'com.sun.star.resource.StringResourceWithLocation'
    location = getResourceLocation(ctx, identifier, path)
    if locale is None:
        locale = getCurrentLocale(ctx)
    arguments = (location, True, locale, filename, '', InteractionHandler())
    return ctx.ServiceManager.createInstanceWithArgumentsAndContext(service, arguments, ctx)

def generateUuid():
    return binascii.hexlify(uno.generateUuid().value).decode('utf-8')

def getDialog(ctx, window, handler, lib, name):
    service = 'com.sun.star.awt.DialogProvider'
    provider = ctx.ServiceManager.createInstanceWithContext(service, ctx)
    url = 'vnd.sun.star.script:%s.%s?location=application' % (lib, name)
    arguments = getNamedValueSet({'ParentWindow': window, 'EventHandler': handler})
    dialog = provider.createDialogWithArguments(url, arguments)
    return dialog

def createMessageBox(peer, message, title, box='message', buttons=2):
    boxtypes = {'message': 'MESSAGEBOX',
                'info': 'INFOBOX',
                'warning': 'WARNINGBOX',
                'error': 'ERRORBOX',
                'query': 'QUERYBOX'}
    box = uno.Enum('com.sun.star.awt.MessageBoxType', boxtypes.get(box, 'MESSAGEBOX'))
    return peer.getToolkit().createMessageBox(peer, box, buttons, title, message)

def createService(ctx, name, **kwargs):
    if kwargs:
        arguments = getNamedValueSet(kwargs)
        service = ctx.ServiceManager.createInstanceWithArgumentsAndContext(name, arguments, ctx)
    else:
        service = ctx.ServiceManager.createInstanceWithContext(name, ctx)
    return service

def getPropertyValueSet(kwargs):
    properties = []
    for key, value in kwargs.items():
        properties.append(getPropertyValue(key, value))
    return tuple(properties)

def getPropertyValue(name, value, state=None, handle=-1):
    property = uno.createUnoStruct('com.sun.star.beans.PropertyValue')
    property.Name = name
    property.Handle = handle
    property.Value = value
    s = state if state else uno.Enum('com.sun.star.beans.PropertyState', 'DIRECT_VALUE')
    property.State = s
    return property

def getNamedValueSet(kwargs):
    namedvalues = []
    for key, value in kwargs.items():
        namedvalues.append(getNamedValue(key, value))
    return tuple(namedvalues)

def getNamedValue(name, value):
    namedvalue = uno.createUnoStruct('com.sun.star.beans.NamedValue')
    namedvalue.Name = name
    namedvalue.Value = value
    return namedvalue

def getPropertySetInfoChangeEvent(source, name, reason, handle=-1):
    event = uno.createUnoStruct('com.sun.star.beans.PropertySetInfoChangeEvent')
    event.Source = source
    event.Name = name
    event.Handle = handle
    event.Reason = reason

def getInteractionHandler(ctx, message):
    window = ctx.ServiceManager.createInstance('com.sun.star.frame.Desktop').ActiveFrame.ComponentWindow
    args = getPropertyValueSet({'Parent': window, 'Context': message})
    interaction = ctx.ServiceManager.createInstanceWithArguments('com.sun.star.task.InteractionHandler', args)
    return interaction

def getOAuth2Request(source, url, message):
    request = OAuth2Request()
    request.ResourceUrl = url
    request.Classification = uno.Enum('com.sun.star.task.InteractionClassification', 'QUERY')
    request.Context = source
    request.Message = message
    return request
