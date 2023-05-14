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

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from com.sun.star.io import XInputStream

from com.sun.star.ucb.ConnectionMode import ONLINE
from com.sun.star.ucb.ConnectionMode import OFFLINE

from com.sun.star.rest.HTTPStatusCode import CREATED
from com.sun.star.rest.HTTPStatusCode import OK
from com.sun.star.rest.HTTPStatusCode import PERMANENT_REDIRECT

from com.sun.star.connection import NoConnectException

from com.sun.star.rest import ConnectionException
from com.sun.star.rest import ConnectTimeoutException
from com.sun.star.rest import ReadTimeoutException

from .requestresponse import RequestResponse
from .requestresponse import execute
from .requestresponse import getDuration

from .unotool import getSimpleFile

import time
from datetime import timedelta
import traceback


def download(ctx, logger, session, parameter, url, timeout, chunk, retry, delay):
    downloaded = False
    retry = max(1, retry)
    sf = getSimpleFile(ctx)
    stream = sf.openFileWrite(url)
    while retry > 0:
        retry -= 1
        try:
            response = execute(ctx, session, parameter, timeout, True)
        except:
            logger.logprb(SEVERE, 'OAuth2Service', 'download()', 121, parameter.Name, traceback.format_exc())
            time.sleep(delay)
        else:
            if response.ok:
                try:
                    for buffer in response.iter_content(chunk, False):
                        stream.writeBytes(uno.ByteSequence(buffer))
                except:
                    logger.logprb(SEVERE, 'OAuth2Service', 'download()', 121, parameter.Name, traceback.format_exc())
                    print('request.download() Download ERROR')
                    range = 'bytes=%s-' % stream.getLength()
                    parameter.setHeader('Range', range)
                    time.sleep(delay)
                else:
                    d = getDuration(response.elapsed)
                    logger.logprb(INFO, 'OAuth2Service', 'download()', 122, url, d.Hours, d.Minutes, d.Seconds, d.NanoSeconds)
                    retry = 0
                    downloaded = True
            else:
                time.sleep(delay)
    stream.closeOutput()
    return downloaded


def upload(ctx, logger, session, parameter, url, timeout, chunk, retry, delay):
    uploaded = False
    sf = getSimpleFile(ctx)
    if sf.exists(url):
        start = 0
        delta = timedelta()
        retry = max(1, retry)
        size = sf.getSize(url)
        stream = sf.openFileRead(url)
        while retry > 0:
            try:
                while retry > 0 and start < size:
                    stream.seek(start)
                    length, parameter.Data = stream.readBytes(None, chunk)
                    end = start + length -1
                    range = 'bytes %s-%s/%s' % (start, end, size)
                    parameter.setHeader('Content-Range', range)
                    response = execute(ctx, session, parameter, timeout)
                    if response.status_code == OK or response.status_code == CREATED:
                        d = getDuration(delta + response.elapsed)
                        logger.logprb(INFO, 'OAuth2Service', 'upload()', 132, url, d.Hours, d.Minutes, d.Seconds, d.NanoSeconds)
                        retry = 0
                        uploaded = True
                    elif response.status_code != PERMANENT_REDIRECT or 'Range' not in response.headers:
                        logger.logprb(SEVERE, 'OAuth2Service', 'upload()', 131, parameter.Name, response.text)
                        retry -= 1
                        time.sleep(delay)
                    else:
                        dummy, sep, range = response.headers.get('Range').rpartition('-')
                        start = int(range) +1
                        delta += response.elapsed
                    response.close()
            except:
                logger.logprb(SEVERE, 'OAuth2Service', 'upload()', 131, parameter.Name, traceback.format_exc())
                retry -= 1
                time.sleep(delay)
        stream.closeInput()
    return uploaded


def getSessionMode(ctx, host, port=80):
    connector = ctx.ServiceManager.createInstance('com.sun.star.connection.Connector')
    try:
        connection = connector.connect('socket,host=%s,port=%s' % (host, port))
    except NoConnectException:
        mode = OFFLINE
    else:
        connection.close()
        mode = ONLINE
    return mode


def getInputStream(session, parameter, timeout, chunk, decode):
    response = execute(session, parameter, timeout, True)
    return InputStream(response, chunk, decode)


class InputStream(unohelper.Base,
                  XInputStream):
    def __init__(self, response, chunk, decode):
        self._response = response
        self._iterator = response.iter_content(chunk, decode)
        self._chunk = chunk
        self._buffer = b''

    #XInputStream
    def readBytes(self, sequence, length):
        sequence = uno.ByteSequence(self._readBytes(length))
        return len(sequence), sequence

    def readSomeBytes(self, sequence, length):
        return self.readBytes(sequence, length)

    def skipBytes(self, length):
        self._readBytes(length)

    def available(self):
        return self._chunk

    def closeInput(self):
        self._response.close()

    def _readBytes(self, length):
        buffer = self._buffer
        size = len(buffer)
        if size < length:
            try:
                while size < length:
                    chunk = next(self._iterator)
                    buffer += chunk
                    size += len(chunk)
            except StopIteration:
                pass
        self._buffer = buffer[length:]
        return buffer[:length]

