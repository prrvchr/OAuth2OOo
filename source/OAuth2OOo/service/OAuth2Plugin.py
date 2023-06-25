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

from com.sun.star.lang import XComponent
from com.sun.star.lang import XServiceInfo
from com.sun.star.auth import XOAuth2Plugin

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.rest import RequestException

from oauth2 import getResponse
from oauth2 import raiseForStatus

from oauth2 import getConfiguration
from oauth2 import getLogger

from oauth2 import extract2Json
from oauth2 import flattenJson
from oauth2 import javaScript2Json
from oauth2 import javaScript2Xml
from oauth2 import parseData
from oauth2 import parseJson
from oauth2 import splitJson
from oauth2 import xml2Json

from oauth2 import g_identifier
from oauth2 import g_defaultlog
from oauth2 import g_basename


import requests
import json
from six import string_types
import traceback

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = '%s.OAuth2Plugin' % g_identifier


class OAuth2Plugin(unohelper.Base,
                   XComponent,
                   XServiceInfo,
                   XOAuth2Plugin):
    def __init__(self, ctx):
        self._ctx = ctx
        self._session = self._getSession()
        self._config = getConfiguration(ctx, g_identifier, False)
        self._listeners = []
        self._logger = getLogger(ctx, g_defaultlog, g_basename)
        self._path = '/*'
        self._sep = '::'

    # XOAuth2Plugin
    def getHttpBody(self, url, method, encoding, parameters):
        cls, mtd = 'OAuth2Plugin', 'getHttpBody'
        method = 'GET' if method is None or not isinstance(method, string_types) else method
        apply = parameters and isinstance(parameters, string_types)
        with self._session as session:
            try:
                kwargs = json.loads(parameters) if apply else {}
                response = getResponse(self._ctx, self, session, cls, mtd, mtd, method, url, self._getTimeout(), kwargs)
                raiseForStatus(self._ctx, self, cls, mtd, mtd, response)
            except RequestException as e:
                body = e.Message
            except Exception as e:
                body = "OAuth2Plugin.getHttpBody() Error: %s" % traceback.format_exc()
            else:
                if encoding:
                    apply = isinstance(encoding, string_types)
                    response.encoding = encoding if apply else response.apparent_encoding
                body = response.text
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
    def _getSession(self):
        session = requests.Session()
        session.codes = requests.codes
        return session

    def _getTimeout(self):
        return self._getConnectTimeout(), self._getReadTimeout()

    def _getConnectTimeout(self):
        return self._config.getByName('ConnectTimeout')

    def _getReadTimeout(self):
        return self._config.getByName('ReadTimeout')


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

