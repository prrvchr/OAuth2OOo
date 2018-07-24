#!
# -*- coding: utf_8 -*-

import uno
import binascii

from .unolib import PyInteractionHandler


def getFileSequence(ctx, url, default=None):
    length = 0
    sequence = uno.ByteSequence(b'')
    fileservice = ctx.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')
    if fileservice.exists(url):
        inputstream = fileservice.openFileRead(url)
        length, sequence = inputstream.readBytes(None, fileservice.getSize(url))
        inputstream.closeInput()
    elif default is not None and fileservice.exists(default):
        inputstream = fileservice.openFileRead(default)
        length, sequence = inputstream.readBytes(None, fileservice.getSize(default))
        inputstream.closeInput()
    return length, sequence

def getProperty(name, typename, attributes, handle=-1):
    return uno.createUnoStruct('com.sun.star.beans.Property',
                               name,
                               handle,
                               uno.getTypeByName(typename),
                               attributes)

def getResourceLocation(ctx, path='OAuth2OOo'):
    identifier = 'com.gmail.prrvchr.extensions.OAuth2OOo'
    service = '/singletons/com.sun.star.deployment.PackageInformationProvider'
    provider = ctx.getValueByName(service)
    return '%s/%s' % (provider.getPackageLocation(identifier), path)

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

def getStringResource(ctx, locale=None, filename='DialogStrings'):
    service = 'com.sun.star.resource.StringResourceWithLocation'
    location = getResourceLocation(ctx)
    if locale is None:
        locale = getCurrentLocale(ctx)
    arguments = (location, True, locale, filename, '', PyInteractionHandler())
    return ctx.ServiceManager.createInstanceWithArgumentsAndContext(service, arguments, ctx)

def generateUuid():
    return binascii.hexlify(uno.generateUuid().value).decode('utf-8')

def createMessageBox(peer, message, title, box='message', buttons=2):
    boxtypes = {'message': 'MESSAGEBOX', 'info': 'INFOBOX', 'warning': 'WARNINGBOX',
                'error': 'ERRORBOX', 'query': 'QUERYBOX'}
    box = uno.Enum('com.sun.star.awt.MessageBoxType', boxtypes[box] if box in boxtypes else 'MESSAGEBOX')
    return peer.getToolkit().createMessageBox(peer, box, buttons, title, message)

def createService(ctx, name, **kwargs):
    if kwargs:
        arguments = []
        for key, value in kwargs.items():
            arguments.append(uno.createUnoStruct('com.sun.star.beans.NamedValue', key, value))
        service = ctx.ServiceManager.createInstanceWithArgumentsAndContext(name, tuple(arguments), ctx)
    else:
        service = ctx.ServiceManager.createInstanceWithContext(name, ctx)
    return service
