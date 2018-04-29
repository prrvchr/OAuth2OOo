#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.awt import XRequestCallback
from com.sun.star.util import XCancellable

import unotools
from unotools import PyServiceInfo
import time
from threading import Thread, RLock
from timeit import default_timer as timer
from requests.compat import unquote_plus

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationName = "com.gmail.prrvchr.extensions.OAuth2OOo.HttpCodeHandler"


class PyHttpCodeHandler(unohelper.Base, PyServiceInfo, XCancellable, XRequestCallback):
    def __init__(self, ctx):
        self.ctx = ctx
        self.watchdog = None

    # XCancellable
    def cancel(self):
        if self.watchdog is not None:
            self.watchdog.cancel()

    # XRequestCallback
    def addCallback(self, page, controller):
        server = PyHttpServer(self.ctx, controller)
        timeout = controller.Configuration.HandlerTimeout
        self.watchdog = PyWatchDog(server, page, timeout)
        server.start()
        self.watchdog.start()


class PyWatchDog(Thread):
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
            pourcent = int(elapsed / self.timeout * 100)
            self.page.notify(pourcent)
        with self.lock:
            if self.server.is_alive():
                self.server.cancel()
        if self.end != 0:
            result = uno.getConstantByName("com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL")
            self.server.controller.Wizard.DialogWindow.endDialog(result)

    def cancel(self):
        self.end = 0


class PyHttpServer(Thread):
    def __init__(self, ctx, controller):
        Thread.__init__(self)
        self.ctx = ctx
        self.controller = controller
        resource = unotools.getStringResource(self.ctx)
        self.success = resource.resolveString("HttpCodeHandler.Message.Success")
        self.error = resource.resolveString("HttpCodeHandler.Message.Error")
        self.lock = RLock()
        self.acceptor = unotools.createService(self.ctx, "com.sun.star.connection.Acceptor")

    def run(self):
        address = self.controller.Configuration.Url.Provider.RedirectAddress
        port = self.controller.Configuration.Url.Provider.RedirectPort
        connection = self.acceptor.accept("socket,host=%s,port=%s,tcpNoDelay=1" % (address, port))
        with self.lock:
            if connection:
                result = self._getResult(connection)
                basename = unotools.getResourceLocation(self.ctx)
                basename += "/OAuth2Success_%s.html" if result else "/OAuth2Error_%s.html"
                locale = unotools.getCurrentLocale(self.ctx)
                fileservice = self.ctx.ServiceManager.createInstance("com.sun.star.ucb.SimpleFileAccess")
                if fileservice.exists(basename % locale.Language):
                    filename = basename % locale.Language
                else:
                    filename = basename % "en"
                inputstream = fileservice.openFileRead(filename)
                length, body = inputstream.readBytes(None, fileservice.getSize(filename))
                inputstream.closeInput()
                header = uno.ByteSequence(b'''\
HTTP/1.1 200 OK
Content-Length: %d
Content-Type: text/html; charset=utf-8
Connection: Closed

''' % length)
                connection.write(header + body)
                connection.close()
                self.acceptor.stopAccepting()
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

    def _getResults(self, parameters):
        results = {}
        for parameter in parameters.split("&"):
            parts = parameter.split("=")
            if len(parts) > 1:
                name = parts[0].strip()
                value = "=".join(parts[1:]).strip()
                results[name] = value
        return results

    def _getResult(self, connection):
        parameters = self._getParameters(connection)
        results = self._getResults(parameters)
        result = uno.getConstantByName("com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL")
        if "code" in results and "state" in results:
            if results["state"] == self.controller.State:
                self.controller.AuthorizationCode = results["code"]
                result = uno.getConstantByName("com.sun.star.ui.dialogs.ExecutableDialogResults.OK")
        return result


g_ImplementationHelper.addImplementation(PyHttpCodeHandler,                         # UNO object class
                                         g_ImplementationName,                      # Implementation name
                                        (g_ImplementationName, ))                   # List of implemented services
