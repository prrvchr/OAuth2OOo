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

from com.sun.star.connection import NoConnectException

from com.sun.star.rest import ConnectionException
from com.sun.star.rest import ConnectTimeoutException
from com.sun.star.rest import ReadTimeoutException

from .requestresponse import RequestResponse
from .requestresponse import execute
from .requestresponse import getDuration

from .unotool import getSimpleFile

import time
import traceback


def download(ctx, logger, session, parameter, url, timeout, chunk, retry, delay):
    sf = getSimpleFile(ctx)
    retry = max(1, retry)
    size = 0
    response = None
    while retry > 0:
        retry -= 1
        stream = sf.openFileWrite(url)
        stream.seek(size)
        try:
            response = execute(ctx, session, parameter, timeout, True)
        except:
            logger.logprb(SEVERE, 'OAuth2Service', 'download()', 121, parameter.Name, traceback.format_exc())
            continue
        else:
            if response.ok:
                try:
                    for buffer in response.iter_content(chunk, False):
                        stream.writeBytes(uno.ByteSequence(buffer))
                except:
                    logger.logprb(SEVERE, 'OAuth2Service', 'download()', 121, parameter.Name, traceback.format_exc())
                    print('request.download() Download ERROR')
                    stream.closeOutput()
                    size = sf.getSize(url)
                    parameter.setHeader('Range', f'bytes={size}-')
                    time.sleep(delay)
                else:
                    stream.closeOutput()
                    d = getDuration(response.elapsed)
                    logger.logprb(INFO, 'OAuth2Service', 'download()', 122, url, d.Hours, d.Minutes, d.Seconds, d.NanoSeconds)
                    retry = 0
    if response is not None:
        return RequestResponse(ctx, parameter, response)
    return None

def upload(ctx, logger, session, parameter, url, timeout):
    sf = getSimpleFile(ctx)
    if sf.exists(url):
        stream = sf.openFileRead(url)
        if parameter.hasHeader('Content-Range'):
            range = parameter.getHeader('Content-Range')
            try:
                start = int(range[6:range.find('-')])
            except:
                logger.logprb(SEVERE, 'OAuth2Service', 'upload()', 131, parameter.Name, traceback.format_exc())
                pass
            else:
                stream.seek(start)
        parameter.DataSink = stream
        try:
            response = execute(ctx, session, parameter, timeout, True)
        except Exception as e:
            logger.logprb(SEVERE, 'OAuth2Service', 'upload()', 131, parameter.Name, traceback.format_exc())
            stream.closeInput()
        else:
            stream.closeInput()
            d = getDuration(response.elapsed)
            logger.logprb(INFO, 'OAuth2Service', 'upload()', 132, url, d.Hours, d.Minutes, d.Seconds, d.NanoSeconds)
            return RequestResponse(ctx, parameter, response)
    return None

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

