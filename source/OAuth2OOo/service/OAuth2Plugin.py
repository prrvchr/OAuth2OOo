#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-24 https://prrvchr.github.io                                  ║
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

from com.sun.star.lang import EventObject
from com.sun.star.lang import XComponent
from com.sun.star.lang import XServiceInfo
from com.sun.star.auth import XOAuth2Plugin

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.rest import RequestException

from oauth20 import Browsers

from oauth20 import clickButton
from oauth20 import sendKey

from oauth20 import getResponse
from oauth20 import raiseForStatus

from oauth20 import getConfiguration
from oauth20 import getLogger
from oauth20 import getResourceLocation

from oauth20 import createService

from oauth20 import extract2Json
from oauth20 import flattenJson
from oauth20 import javaScript2Json
from oauth20 import javaScript2Xml
from oauth20 import parseData
from oauth20 import parseJson
from oauth20 import splitJson
from oauth20 import xml2Json

from oauth20 import g_identifier
from oauth20 import g_defaultlog
from oauth20 import g_errorlog
from oauth20 import g_basename

import requests
import json
from six import string_types, text_type
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Plugin' % g_identifier


class OAuth2Plugin(unohelper.Base,
                   XComponent,
                   XServiceInfo,
                   XOAuth2Plugin):
    def __init__(self, ctx):
        print("OAuth2Plugin.__init__() 1")
        self._ctx = ctx
        self._session = self._getHttpSession()
        self._config = getConfiguration(ctx, g_identifier, False)
        #path = uno.fileUrlToSystemPath(getResourceLocation(ctx, g_identifier))
        self._browsers = Browsers()
        self._listeners = []
        self._logger = getLogger(ctx, g_defaultlog, g_basename)
        self._errorlog = None
        self._default = 'xpath'
        self._path = '/*'
        self._sep = '::'
        self._logger.logp(INFO, 'OAuth2Plugin', '__init__()', 'Init Done')
        print("OAuth2Plugin.__init__() 2")

    # XOAuth2Plugin
    def browserOpen(self, document, name, path, init, options):
        print("OAuth2Plugin.browserOpen() 1 Init: %s" % init)
        cls, mtd = 'OAuth2Plugin', 'browserOpen'
        try:
            print("OAuth2Plugin.browserOpen() 2 Browser: %s - Path: %s" % (name, path))
            #driver = getWebDriver(browser, path, '--headless')
            init = self._getInt(init)
            session = self._browsers.openBrowser(document, mtd, name, path, init, options)
        except Exception as e:
            self._logger.logp(SEVERE, cls, mtd, 'ERROR..... \n%s' % traceback.format_exc())
            #self._logException(cls, mtd, e)
            #print("OAuth2Plugin.browserOpen() Error: %s" % text_type(traceback.format_exc()))
            session = "OAuth2Plugin.browserOpen() Error: %s" % text_type(e).strip()
            print(session)
        print("OAuth2Plugin.browserOpen() 4 Session: %s" % session)
        return session

    def browserClick(self, session, by, path, url, init, wait):
        print("OAuth2Plugin.browserClick() 1")
        cls, mtd = 'OAuth2Plugin', 'browserClick'
        try:
            driver, session = self._browsers.getBrowser(session, mtd, init)
            if driver is None:
                print("OAuth2Plugin.browserClick() 2")
                return session
            print("OAuth2Plugin.browserClick() 2 Url: %s" % (url, ))
            by = self._getBy(by)
            if isinstance(url, string_types) and url and url != driver.current_url:
                driver.get(url)
            wait = self._getInt(wait)
            clickButton(driver, wait, by, path)
        except Exception as e:
            self._logException(cls, mtd, e)
            session = "OAuth2Plugin.browserClick() Error: %s" % text_type(e).strip()
            print(session)
        print("OAuth2Plugin.browserClick() 3")
        return session

    def browserField(self, session, by, path, value, url, init, wait):
        print("OAuth2Plugin.browserField() 1")
        cls, mtd = 'OAuth2Plugin', 'browserField'
        try:
            driver, session = self._browsers.getBrowser(session, mtd, init)
            if driver is None:
                return session
            print("OAuth2Plugin.browserField() 2 Url: %s" % (url, ))
            if isinstance(url, string_types) and url and url != driver.current_url:
                driver.get(url)
            by = self._getBy(by)
            wait = self._getInt(wait)
            sendKey(driver, wait, by, path, value)
        except Exception as e:
            self._logException(cls, mtd, e)
            session = "OAuth2Plugin.browserField() Error: %s" % text_type(e).strip()
            print(session)
        return session

    def browserForm(self, session, form, url, init, wait):
        print("OAuth2Plugin.browserForm() 1")
        cls, mtd = 'OAuth2Plugin', 'browserForm'
        try:
            driver, session = self._browsers.getBrowser(session, mtd, init)
            if driver is None:
                return session
            print("OAuth2Plugin.browserForm() 2 Url: %s" % (url, ))
            if isinstance(url, string_types) and url and url != driver.current_url:
                driver.get(url)
            wait = self._getInt(wait)
            if isinstance(form, tuple) and 0 < len(form) and isinstance(form[0], tuple) and 1 < len(form[0]):
                for row in form:
                    by = self._getBy() if 3 > len(row) else self._getBy(row[0])
                    path = row[0] if 3 > len(row) else row[1]
                    value = row[1] if 3 > len(row) else row[2]
                    sendKey(driver, wait, by, path, value)
        except Exception as e:
            self._logException(cls, mtd, e)
            session = "OAuth2Plugin.browserForm() Error: %s" % text_type(e).strip()
            print(session)
        return session

    def browserContent(self, session, url, encoding):
        print("OAuth2Plugin.browserContent() 1")
        cls, mtd = 'OAuth2Plugin', 'browserContent'
        try:
            driver, session = self._browsers.getBrowser(mtd, document)
            if driver is None:
                return session
            encoding = encoding if isinstance(encoding, string_types) and encoding else 'utf-8'
            print("OAuth2Plugin.browserContent() 2")
            content = ''
            if isinstance(url, string_types) and url and url != driver.current_url:
                driver.get(url)
            content = driver.page_source.encode(encoding)
        except Exception as e:
            self._logException(cls, mtd, e)
            content = "OAuth2Plugin.browserContent() Error: %s" % text_type(e).strip()
            print(content)
        print("OAuth2Plugin.browserContent() 4")
        return content

    def httpAuth(self, name, pwd):
        if pwd is None:
            pass
            #user = getOAuth2UserName(self._ctx, self, url, message)
            #auth = '{"auth": ["%s","%s"]}' % name, pwd
        return json.dumps({'auth': [name, pwd]})

    def httpContent(self, url, method, encoding, parameters):
        cls, mtd = 'OAuth2Plugin', 'httpContent'
        decode = True
        method = 'GET' if method is None or not isinstance(method, string_types) else method
        apply = parameters and isinstance(parameters, string_types)
        with self._session as session:
            try:
                kwargs = json.loads(parameters) if apply else {}
                print("OAuth2Plugin.httpContent() 1 Kwargs: %s" % (kwargs, ))
                response = getResponse(self._ctx, self, session, cls, mtd, mtd, method, url, self._getTimeout(), kwargs)
                raiseForStatus(self._ctx, self, cls, mtd, mtd, response)
            except RequestException as e:
                body = e.Message
            except Exception as e:
                self._logException(cls, mtd, e)
                body = "OAuth2Plugin.httpContent() Error: %s" % traceback.format_exc()
            else:
                print("OAuth2Plugin.httpContent() 2 Encoding: '%s' - Type: %s" % (encoding, type(encoding)))
                if encoding is not None:
                    apply = isinstance(encoding, string_types)
                    if not apply:
                        decode = bool(encoding)
                    if decode and apply:
                        response.encoding = encoding if encoding else response.apparent_encoding
                if decode:
                    body = response.text
                else:
                    print("OAuth2Plugin.httpContent() Content *****************")
                    body = response.content
                response.close()
        return body

    def parseHtml(self, data, path, baseurl):
        return parseData(data, path, baseurl, 'html', self._path)

    def parseXml(self, data, path, baseurl):
        return parseData(data, path, baseurl, 'xml', self._path)

    def parseJson(self, data, path):
        return parseJson(data, path)

    def javaScript2Xml(self, data, path):
        return javaScript2Xml(data, path, self._path)

    def xml2Json(self, data, path):
        return xml2Json(data, path, self._path)

    def javaScript2Json(self, data, path):
        return javaScript2Json(data, path, self._path)

    def dublinCore2Json(self, data, baseurl):
        return extract2Json(data, baseurl, 'dublincore')

    def jsonLd2Json(self, data, baseurl):
        return extract2Json(data, baseurl, 'json-ld')

    def microData2Json(self, data, baseurl):
        return extract2Json(data, baseurl, 'microdata')

    def microFormat2Json(self, data, baseurl):
        return extract2Json(data, baseurl, 'microformat')

    def openGraph2Json(self, data, baseurl):
        return extract2Json(data, baseurl, 'opengraph')

    def rdfa2Json(self, data, baseurl):
        return extract2Json(data, baseurl, 'rdfa')

    def splitJson(self, data, typename, path, separator):
        return splitJson(data, typename, path, separator, self._sep)

    def flattenJson(self, data, typename, path, separator):
        return flattenJson(data, typename, path, separator, self._sep)

    # Private method
    def _getHttpSession(self):
        session = requests.Session()
        session.codes = requests.codes
        return session

    def _getTimeout(self):
        return self._getConnectTimeout(), self._getReadTimeout()

    def _getConnectTimeout(self):
        return self._config.getByName('ConnectTimeout')

    def _getReadTimeout(self):
        return self._config.getByName('ReadTimeout')

    def _getBy(self, by=False):
        default = self._default
        if by and isinstance(by, string_types):
            default = by.lower()
        return default

    def _getInt(self, wait):
        return int(wait) if isinstance(wait, float) else 0

    def _logException(self, cls, mtd, e):
        logger = self._getErrorLogger()
        logger.logp(SEVERE, cls, mtd, text_type(e).strip())
        logger.logp(SEVERE, cls, mtd, text_type(traceback.format_exc()).strip())

    def _getErrorLogger(self):
        if self._errorlog is None:
            self._errorlog = getLogger(self._ctx, g_errorlog, g_basename)
        return self._errorlog

    # XComponent
    def dispose(self):
        source = EventObject(self)
        for listener in self._listeners:
            listener.disposing(source)
    def addEventListener(self, listener):
        self._listeners.append(listener)
    def removeEventListener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


g_ImplementationHelper.addImplementation(OAuth2Plugin,
                                         g_ImplementationName,
                                        (g_ImplementationName,))

