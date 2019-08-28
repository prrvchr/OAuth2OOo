#!
# -*- coding: utf_8 -*-

#from __futur__ import absolute_import

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
        self.watchdog = None

    # XCancellable
    def cancel(self):
        if self.watchdog and self.watchdog.is_alive():
            self.watchdog.cancel()

    # XRequestCallback
    def addCallback(self, page, controller):
        lock = Condition()
        server = Server(self.ctx, controller, lock)
        timeout = controller.Configuration.HandlerTimeout
        self.watchdog = WatchDog(server, page, timeout, lock)
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
        canceled = True
        with self.lock:
            while now < self.end and self.server.is_alive():
                elapsed = now - start
                percent = int(elapsed / self.timeout * 100)
                self.page.notify(percent)
                self.lock.wait(wait)
                now = timer()
            if self.end != 0:
                canceled = False
                self.page.notify(100)
            if self.server.is_alive():
                self.server.cancel(canceled)
            self.lock.notifyAll()

    def cancel(self):
        if self.server.is_alive():
            self.end = 0
            self.server.join()


class Server(Thread):
    def __init__(self, ctx, controller, lock):
        Thread.__init__(self)
        self.ctx = ctx
        self.controller = controller
        self.lock = lock
        self.canceled = False
        self.acceptor = createService(self.ctx, 'com.sun.star.connection.Acceptor')

    def run(self):
        address = self.controller.Configuration.Url.Scope.Provider.RedirectAddress
        port = self.controller.Configuration.Url.Scope.Provider.RedirectPort
        ok = uno.getConstantByName('com.sun.star.ui.dialogs.ExecutableDialogResults.OK')
        connection = self.acceptor.accept('socket,host=%s,port=%s,tcpNoDelay=1' % (address, port))
        with self.lock:
            if connection:
                print("WizardServer.run() 1")
                result = self._getResult(connection)
                basename = getResourceLocation(self.ctx, g_identifier, 'OAuth2OOo')
                location = 'https://prrvchr.github.io/OAuth2OOo/OAuth2OOo/registration'
                location += '/OAuth2Success_%s' if result else '/OAuth2Error_%s'
                basename += '/OAuth2Success_%s.md' if result else '/OAuth2Error_%s.md'
                locale = getCurrentLocale(self.ctx)
                location = location % locale.Language
                #length, body = getFileSequence(self.ctx, basename % locale.Language, basename % 'en')
                header = uno.ByteSequence(b'''\
HTTP/1.1 302 Found
Location: %s
Connection: Closed

''' % location)
                connection.write(header)
                connection.close()
                print("WizardServer.run() 2")
                self.acceptor.stopAccepting()
                print("WizardServer.run() 3")
            if not self.canceled:
                print("WizardServer.run() 4")
                if self.controller.Path:
                    print("WizardServer.run() 5")
                    self.controller.Wizard.updateTravelUI()
                    if self.controller.canAdvance():
                        print("WizardServer.run() 6")
                        self.controller.Wizard.travelNext()
                else:
                    print("WizardServer.run() 7")
                    self.controller.Wizard.DialogWindow.endDialog(ok)
            print("WizardServer.run() 8")
            self.lock.notifyAll()

    def cancel(self, state):
        self.canceled = state
        self.acceptor.stopAccepting()

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
        if 'code' in response and 'state' in response:
            if response['state'] == self.controller.Uuid:
                self.controller.AuthorizationCode.Value = response['code']
                self.controller.AuthorizationCode.IsPresent = True
                return True
        self.controller.Error = '%s' % response
        return False
