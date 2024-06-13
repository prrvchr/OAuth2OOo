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

from com.sun.star.lang import EventObject
from com.sun.star.lang import XComponent
from com.sun.star.lang import XServiceInfo

from com.sun.star.sheet import XVolatileResult

from com.sun.star.util import XCloseListener

from .configuration import g_identifier

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import uuid
from six import string_types, text_type
from threading import Thread
import traceback


def sendKey(driver, wait, by, path, value):
    if wait:
        wait = WebDriverWait(driver, wait)
        element = wait.until(EC.visibility_of_element_located((by, path)))
    else:
        element = driver.find_element(by, path)
    element.send_keys(value)

def clickButton(driver, wait, by, path):
    if wait:
        wait = WebDriverWait(driver, wait)
        element = wait.until(EC.element_to_be_clickable((by, path)))
    else:
        element = driver.find_element(by, path)
    element.click()


class CloseListener(unohelper.Base,
                    XCloseListener):
    def __init__(self, browser):
        self._browser = browser

    # XCloseListener
    def queryClosing(self, source, ownership):
        self._browser.close(source.Source)
    def notifyClosing(self, source):
        pass
    def disposing(self, source):
        pass


class Browsers():
    def __init__(self, path=None):
        self._path = path
        self._listener = CloseListener(self)
        self._browsers = {}

    def close(self, document):
        uid = self._getDocumentUid(document)
        browser = self._browsers.pop(uid, None)
        if browser and not browser.isClosed():
            browser.Driver.quit()
        document.removeCloseListener(self._listener)

    def openBrowser(self, document, mtd, name, path, init, options):
        uid = self._getDocumentUid(document)
        if uid in self._browsers:
            browser = self._browsers.get(uid)
            if browser.isClosed():
                browser = self._getBrowser(uid, mtd, name, path, init, options)
        else:
            browser = self._getBrowser(uid, mtd, name, path, init, options)
            document.addCloseListener(self._listener)
        return browser.getSession()

    def getBrowser(self, session, mtd, init=False):
        driver = None
        browser = self._getSession(session)
        if browser is not None:
            if browser.isClosed():
                session = 'OAuth2Plugin.%s()  Error: WebDriver has been closed' % mtd
            else:
                driver = browser.getDriver(init)
        return driver, session

    def _getDocumentUid(self, document):
        # FIXME: I'm not sure that Runtime UID is a satisfactory document unique identifier
        # FIXME: ie: independent of changing the document url
        return document.RuntimeUID

    def _getBrowser(self, uid, mtd, name, path, init, options):
        browser = Browser(self._path, mtd, name, path, init, options)
        self._browsers[uid] = browser
        return browser

    def _getSession(self, session):
        for browser in self._browsers.values():
            if browser.Session == session:
                return browser
        return None


class Browser():
    def __init__(self, location, mtd, name, path, init, options):
        self._driver = self._getWebDriver(location, name, path, options)
        self._init = init
        self._count = 0
        self._session = 'OAuth2Plugin.%s() Error: WebDriver has not been initialized' % mtd

    @property
    def Driver(self):
        return self._driver
    @property
    def Session(self):
        return self._session

    def getDriver(self, init):
        if init:
            if self._init <= self._count:
                return None
            self._count += 1
        return self.Driver

    def getSession(self):
        self._session = text_type(uuid.uuid4())
        return self._session

    def isClosed(self):
        try:
            self.Driver.title
            return False
        except:
            return True

    def _getWebDriver(self, location, name, path, options):
        option = None
        name = name.title()
        if path or options:
            option = self._getWebOptionClass(name, path)
            if option:
                for o in options:
                    option.add_argument(o)
        return self._getWebDriverClass(location, name, option)
    
    def _getWebOptionClass(self, name, path):
        options = None
        if name in ('Brave', 'Chrome', 'Chromium'):
            options = webdriver.ChromeOptions()
        elif name == 'Edge':
            options = webdriver.EdgeOptions()
        elif name == 'Firefox':
            options = webdriver.FirefoxOptions()
        elif name == 'Ie':
            options = webdriver.IeOptions()
        elif name == 'Opera':
            options = webdriver.ChromeOptions()
            options.add_experimental_option('w3c', True)
        elif name == 'Safari':
            options = webdriver.SafariOptions()
        if path and isinstance(path, string_types):
            options.binary_location = path
        return options

    def _getWebDriverClass(self, path, name, options):
        driver = None
        kwargs = {}
        if path and isinstance(path, string_types):
            kwargs['path'] = path
        if name == 'Brave':
            from selenium.webdriver.chrome.service import Service as BraveService
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.utils import ChromeType
            kwargs['chrome_type'] = ChromeType.BRAVE
            driver = webdriver.Chrome(service=BraveService(ChromeDriverManager(**kwargs).install()), options=options)
        elif name == 'Chrome':
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(**kwargs).install()), options=options)
        elif name == 'Chromium':
            from selenium.webdriver.chrome.service import Service as ChromiumService
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.utils import ChromeType
            kwargs['chrome_type'] = ChromeType.CHROMIUM
            driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(**kwargs).install()), options=options)
        elif name == 'Edge':
            from selenium.webdriver.edge.service import Service as EdgeService
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager(**kwargs).install()), options=options)
        elif name == 'Firefox':
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager(**kwargs).install()), options=options)
        elif name == 'Ie':
            from selenium.webdriver.ie.service import Service as IEService
            from webdriver_manager.microsoft import IEDriverManager
            driver = webdriver.Ie(service=IEService(IEDriverManager(**kwargs).install()), options=options)
        elif name == 'Opera':
            from selenium.webdriver.chrome import service as OperaService
            from webdriver_manager.opera import OperaDriverManager
            service = OperaService.Service(OperaDriverManager(**kwargs).install())
            service.start()
            driver = webdriver.Remote(service.service_url, options=options)
        elif name == 'Safari':
            from selenium.webdriver.safari import service as SafariService
            driver = webdriver.Safari(service=SafariService(), options=options)
        return driver


class VolatileResult(unohelper.Base,
                     XComponent,
                     XServiceInfo,
                     XVolatileResult):
    def __init__(self):
        self._name = '%s.VolatileResult' % g_identifier
        self._service = 'com.sun.star.sheet.VolatileResult'
        self._listeners = []
        self._rlisteners = []

    def set(self, value):
        result = uno.createUnoStruct('com.sun.star.sheet.ResultEvent')
        result.Value = value
        result.Source = self
        for listener in self._rlisteners:
            print("VolatileResult.set()")
            listener.modified(result)

    # XVolatileResult
    def addResultListener(self, listener):
        print("VolatileResult.addResultListener()")
        self._rlisteners.append(listener)
    def removeResultListener(self, listener):
        print("VolatileResult.removeResultListener()")
        if listener in self._rlisteners:
            self._rlisteners.remove(listener)

    # XComponent
    def dispose(self):
        print("VolatileResult.dispose()")
        source = EventObject(self)
        for listener in self._listeners:
            listener.disposing(source)
    def addEventListener(self, listener):
        print("VolatileResult.addEventListener()")
        self._listeners.append(listener)
    def removeEventListener(self, listener):
        print("VolatileResult.removeEventListener()")
        if listener in self._listeners:
            self._listeners.remove(listener)

    # XServiceInfo
    def supportsService(self, service):
        print("VolatileResult.supportsService()")
        return service == self._service
    def getImplementationName(self):
        print("VolatileResult.getImplementationName()")
        return self._name
    def getSupportedServiceNames(self):
        print("VolatileResult.getSupportedServiceNames()")
        return (self._service, )

