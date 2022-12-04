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

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.connection import AlreadyAcceptingException
from com.sun.star.connection import ConnectionSetupException
from com.sun.star.lang import IllegalArgumentException
from com.sun.star.io import IOException

from requests.compat import unquote_plus
from requests.compat import urlencode


from ..unotool import createService

from ..logger import logMessage

import time
from threading import Thread
from timeit import default_timer as timer
import traceback


class WatchDog(Thread):
    def __init__(self, ctx, server, notify, register, scopes, provider, user, timeout, lock):
        Thread.__init__(self)
        self._ctx = ctx
        self._server = server
        self._notify = notify
        self._register = register
        self._scopes = scopes
        self._provider = provider
        self._user = user
        self._timeout = timeout
        self._lock = lock
        self._step = 50
        self._end = 0

    def run(self):
        wait = self._timeout/self._step
        start = now = timer()
        self._end = start + self._timeout
        self._notify(0)
        with self._lock:
            while now < self._end and self._server.is_alive():
                elapsed = now - start
                percent =  min(99, int(elapsed * 100 / self._timeout))
                if self._server.is_alive():
                    self._notify(percent)
                self._lock.wait(wait)
                now = timer()
            if self._server.is_alive():
                self._server.stopAccepting()
            elif self._server.hasAuthorizationCode():
                self._notify(100)
                self._register(self._scopes, self._provider, self._user, self._server.getAuthorizationCode())
            self._lock.notifyAll()
            logMessage(self._ctx, INFO, "WatchDog Running ... Done", 'WatchDog', 'run()')

    def cancel(self):
        if self._server.is_alive():
            self._end = 0
            self._server.join()


class Server(Thread):
    def __init__(self, ctx, user, url, provider, address, port, uuid, lock):
        Thread.__init__(self)
        self._ctx = ctx
        self._user = user
        self._url = url
        self._provider = provider
        self._address = address
        self._port = port
        self._uuid = uuid
        self._code = None
        self._lock = lock
        self._acceptor = createService(ctx, 'com.sun.star.connection.Acceptor')

    def hasAuthorizationCode(self):
        return self._code is not None

    def getAuthorizationCode(self):
        return self._code

    def stopAccepting(self):
        self._acceptor.stopAccepting()

    def run(self):
        connection = None
        try:
            argument = 'socket,host=%s,port=%s,tcpNoDelay=1' % (self._address, self._port)
            connection = self._acceptor.accept(argument)
        except AlreadyAcceptingException as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, 'Server', 'run()')
        except ConnectionSetupException as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, 'Server', 'run()')
        except IllegalArgumentException as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, 'Server', 'run()')
        if connection:
            with self._lock:
                result = self._getResult(connection)
                location = self._getLocation(result)
                location += '?%s' % urlencode({'provider': self._provider, 'user': self._user})
                header = '''\
HTTP/1.1 302 Found
Location: %s
Connection: Closed

''' % location
                try:
                    connection.write(uno.ByteSequence(header.encode('utf8')))
                except IOException as e:
                    msg = "Error: %s - %s" % (e, traceback.print_exc())
                    logMessage(self._ctx, SEVERE, msg, 'Server', 'run()')
                connection.flush()
                connection.close()
                self._acceptor.stopAccepting()
                self._lock.notifyAll()
                logMessage(self._ctx, INFO, "Server Running ... Done", 'Server', 'run()')

# Server private getter methods
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
            if response['state'] == self._uuid:
                self._code = response['code']
                return True
        msg = 'Request response Error: %s - %s' % (parameters, response)
        logMessage(self._ctx, SEVERE, msg, 'Server', '_getResult()')
        return False

    def _getLocation(self, result):
        basename = 'OAuth2Success' if result else 'OAuth2Error'
        return self._url % basename

