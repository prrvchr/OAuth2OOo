#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.awt import XRequestCallback
from com.sun.star.util import XCancellable

from .unotools import createService
from .unotools import getResourceLocation
from .unotools import getCurrentLocale
from .unotools import getFileSequence
from .oauth2tools import g_identifier

from .requests.compat import unquote_plus

import time
from threading import Thread
from threading import Condition
from timeit import default_timer as timer


class WizardServer(unohelper.Base,
                   XCancellable,
                   XRequestCallback):
    def __init__(self, ctx):
        self.ctx = ctx
        self.lock = Condition()
        self.watchdog = None

    # XCancellable
    def cancel(self):
        print("HttpCodeHandler.cancel()")
        with self.lock:
            if self.watchdog and self.watchdog.is_alive():
                self.watchdog.cancel()
                print("HttpCodeHandler.wait()")
                #self.lock.wait()

    # XRequestCallback
    def addCallback(self, page, controller):
        server = Server(self.ctx, controller, self.lock)
        timeout = controller.Configuration.HandlerTimeout
        self.watchdog = WatchDog(server, page, timeout, self.lock)
        server.start()
        self.watchdog.start()


class WatchDog(Thread):
    def __init__(self, server, page, timeout, lock):
        Thread.__init__(self)
        self.server = server
        self.page = page
        self.timeout = timeout
        self.end = 0
        self.step = 50
        self.lock = lock

    def run(self):
        wait = self.timeout/self.step
        start = now = timer()
        self.end = start + self.timeout
        self.page.notify(0)
        with self.lock:
            while now < self.end and self.server.is_alive():
                elapsed = now - start
                percent = int(elapsed / self.timeout * 100)
                self.page.notify(percent)
                self.lock.wait(wait)
                now = timer()
            if self.server.is_alive():
                self.server.cancel()
                print("WatchDog.server.cancel()")
            if self.end:
                self.page.notify(100)
                result = uno.getConstantByName('com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL')
                self.server.controller.Handler.Wizard.DialogWindow.endDialog(result)
            self.lock.notifyAll()

    def cancel(self):
        print("WatchDog.cancel()")
        self.end = 0


class Server(Thread):
    def __init__(self, ctx, controller, lock):
        Thread.__init__(self)
        self.ctx = ctx
        self.controller = controller
        self.lock = lock
        self.acceptor = createService(self.ctx, 'com.sun.star.connection.Acceptor')

    def run(self):
        address = self.controller.Configuration.Url.Provider.RedirectAddress
        port = self.controller.Configuration.Url.Provider.RedirectPort
        result = uno.getConstantByName('com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL')
        connection = self.acceptor.accept('socket,host=%s,port=%s,tcpNoDelay=1' % (address, port))
        with self.lock:
            if connection:
                result = self._getResult(connection)
                basename = getResourceLocation(self.ctx, g_identifier, 'OAuth2OOo')
                basename += '/OAuth2Success_%s.html' if result else '/OAuth2Error_%s.html'
                locale = getCurrentLocale(self.ctx)
                length, body = getFileSequence(self.ctx, basename % locale.Language, basename % 'en')
                header = uno.ByteSequence(b'''\
HTTP/1.1 200 OK
Content-Length: %d
Content-Type: text/html; charset=utf-8
Connection: Closed

''' % length)
                connection.write(header + body)
                connection.close()
                self.acceptor.stopAccepting()
                print("HttpServer.acceptor.stopAccepting()")
                self.controller.Handler.Wizard.DialogWindow.endDialog(result)
            self.lock.notifyAll()
        print("HttpServer.run() end")

    def cancel(self):
        print("HttpServer.cancel()")
        self.acceptor.stopAccepting()
        print("HttpServer.stop()")

    def _readString(self, connection, length):
        length, sequence = connection.read(None, length)
        return sequence.value.decode()

    def _readLine(self, connection, eol='\r\n'):
        line = ''
        while not line.endswith(eol):
            line += self._readString(connection, 1)
        return line.strip()

    def _getRequest(self, connection):
        method, url, version = None, '/', 'HTTP/0.9'
        line = self._readLine(connection)
        parts = line.split(' ')
        if len(parts) > 1:
            method = parts[0].strip()
            url = parts[1].strip()
        if len(parts) > 2:
            version = parts[2].strip()
        return method, url, version

    def _getHeaders(self, connection):
        headers = {'Content-Length': 0}
        while True:
            line = self._readLine(connection)
            if not line:
                break
            parts = line.split(':')
            if len(parts) > 1:
                headers[parts[0].strip()] = ':'.join(parts[1:]).strip()
        return headers

    def _getContentLength(self, headers):
        return int(headers['Content-Length'])

    def _getParameters(self, connection):
        parameters = ''
        method, url, version = self._getRequest(connection)
        headers = self._getHeaders(connection)
        if method == 'GET':
            parts = url.split('?')
            if len(parts) > 1:
                parameters = '?'.join(parts[1:]).strip()
        elif method == 'POST':
            length = self._getContentLength(headers)
            parameters = self._readString(connection, length).strip()
        return unquote_plus(parameters)

    def _getResponse(self, parameters):
        response = {}
        for parameter in parameters.split('&'):
            parts = parameter.split('=')
            if len(parts) > 1:
                name = parts[0].strip()
                value = '='.join(parts[1:]).strip()
                response[name] = value
        return response

    def _getResult(self, connection):
        parameters = self._getParameters(connection)
        response = self._getResponse(parameters)
        level = uno.getConstantByName('com.sun.star.logging.LogLevel.SEVERE')
        result = uno.getConstantByName('com.sun.star.ui.dialogs.ExecutableDialogResults.CANCEL')
        if 'code' in response and 'state' in response:
            if response['state'] == self.controller.Uuid:
                self.controller.AuthorizationCode.Value = response['code']
                self.controller.AuthorizationCode.IsPresent = True
                level = uno.getConstantByName('com.sun.star.logging.LogLevel.INFO')
                result = uno.getConstantByName('com.sun.star.ui.dialogs.ExecutableDialogResults.OK')
        self.controller.Configuration.Logger.logp(level, 'HttpServer', '_getResult', '%s' % response)
        return result
