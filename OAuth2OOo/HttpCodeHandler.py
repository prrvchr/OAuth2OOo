#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.lang import XServiceInfo
from com.sun.star.awt import XRequestCallback
from com.sun.star.util import XCancellable

import oauth2
import time
from threading import Thread, RLock
from timeit import default_timer as timer
from requests.compat import unquote_plus

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.HttpCodeHandler"


class HttpCodeHandler(unohelper.Base, XServiceInfo, XCancellable, XRequestCallback):
    def __init__(self, ctx):
        self.ctx = ctx
        self.watchdog = None

    # XCancellable
    def cancel(self):
        if self.watchdog is not None:
            self.watchdog.cancel()

    # XRequestCallback
    def addCallback(self, page, controller):
        server = HttpServer(self.ctx, controller)
        timeout = controller.Configuration.HandlerTimeout
        self.watchdog = WatchDog(server, page, timeout)
        server.start()
        self.watchdog.start()

    # XServiceInfo
    def supportsService(self, service):
        return g_ImplementationHelper.supportsService(g_ImplementationName, service)
    def getImplementationName(self):
        return g_ImplementationName
    def getSupportedServiceNames(self):
        return g_ImplementationHelper.getSupportedServiceNames(g_ImplementationName)


class WatchDog(Thread):
    def __init__(self, server, page, timeout):
        Thread.__init__(self)
        self.server = server
        self.page = page
        self.timeout = timeout
        self.end = 0
        self.step = 20
        self.lock = RLock()

    def run(self):
        wait = self.timeout/self.step
        start = now = timer()
        self.end = start + self.timeout
        self.page.notify(0)
        while now < self.end and self.server.is_alive():
            time.sleep(wait)
            now = timer()
            elapsed = now - start
            percent = int(elapsed / self.timeout * 100)
            self.page.notify(percent)
        with self.lock:
            if self.server.is_alive():
                self.server.cancel()
        if self.end != 0:
            result = uno.getConstantByName("com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL")
            self.server.controller.Wizard.DialogWindow.endDialog(result)

    def cancel(self):
        self.end = 0


class HttpServer(Thread):
    def __init__(self, ctx, controller):
        Thread.__init__(self)
        self.ctx = ctx
        self.controller = controller
        self.lock = RLock()
        self.acceptor = oauth2.createService(self.ctx, "com.sun.star.connection.Acceptor")

    def run(self):
        address = self.controller.Configuration.Url.Provider.RedirectAddress
        port = self.controller.Configuration.Url.Provider.RedirectPort
        connection = self.acceptor.accept("socket,host=%s,port=%s,tcpNoDelay=1" % (address, port))
        with self.lock:
            if connection:
                result = self._getResult(connection)
                basename = oauth2.getResourceLocation(self.ctx)
                basename += "/OAuth2Success_%s.html" if result else "/OAuth2Error_%s.html"
                locale = oauth2.getCurrentLocale(self.ctx)
                length, body = oauth2.getFileSequence(self.ctx, basename % locale.Language, basename % "en")
                header = uno.ByteSequence(b'''\
HTTP/1.1 200 OK
Content-Length: %d
Content-Type: text/html; charset=utf-8
Connection: Closed

''' % length)
                connection.write(header + body)
                connection.close()
                self.acceptor.stopAccepting()
                wait = self.controller.Configuration.RequestTimeout
                time.sleep(wait)
                self.controller.Wizard.DialogWindow.endDialog(result)

    def cancel(self):
        with self.lock:
            if self.is_alive():
                self.acceptor.stopAccepting()

    def _readString(self, connection, length):
        length, sequence = connection.read(None, length)
        return sequence.value.decode()

    def _readLine(self, connection, eol="\r\n"):
        line = ""
        while not line.endswith(eol):
            line += self._readString(connection, 1)
        return line.strip()

    def _getRequest(self, connection):
        method, url, version = None, "/", "HTTP/0.9"
        line = self._readLine(connection)
        parts = line.split(" ")
        if len(parts) > 1:
            method = parts[0].strip()
            url = parts[1].strip()
        if len(parts) > 2:
            version = parts[2].strip()
        return method, url, version

    def _getHeaders(self, connection):
        headers = {"Content-Length": 0}
        while True:
            line = self._readLine(connection)
            if not line:
                break
            parts = line.split(":")
            if len(parts) > 1:
                headers[parts[0].strip()] = ":".join(parts[1:]).strip()
        return headers

    def _getContentLength(self, headers):
        return int(headers["Content-Length"])

    def _getParameters(self, connection):
        parameters = ""
        method, url, version = self._getRequest(connection)
        headers = self._getHeaders(connection)
        if method == "GET":
            parts = url.split("?")
            if len(parts) > 1:
                parameters = "?".join(parts[1:]).strip()
        elif method == "POST":
            length = self._getContentLength(headers)
            parameters = self._readString(connection, length).strip()
        return unquote_plus(parameters)

    def _getResponse(self, parameters):
        response = {}
        for parameter in parameters.split("&"):
            parts = parameter.split("=")
            if len(parts) > 1:
                name = parts[0].strip()
                value = "=".join(parts[1:]).strip()
                response[name] = value
        return response

    def _getResult(self, connection):
        parameters = self._getParameters(connection)
        response = self._getResponse(parameters)
        level = uno.getConstantByName("com.sun.star.logging.LogLevel.SEVERE")
        result = uno.getConstantByName("com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL")
        if "code" in response and "state" in response:
            if response["state"] == self.controller.State:
                self.controller.AuthorizationCode = response["code"]
                level = uno.getConstantByName("com.sun.star.logging.LogLevel.INFO")
                result = uno.getConstantByName("com.sun.star.ui.dialogs.ExecutableDialogResults.OK")
        self.controller.Configuration.Logger.logp(level, "HttpServer", "_getResult", "%s" % response)
        return result


g_ImplementationHelper.addImplementation(HttpCodeHandler,                           # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
