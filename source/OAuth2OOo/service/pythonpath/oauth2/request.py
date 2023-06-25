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

from com.sun.star.rest import FileNotFoundException
from com.sun.star.rest import HTTPException
from com.sun.star.rest import RequestException

from com.sun.star.rest.ParameterType import JSON
from com.sun.star.rest.ParameterType import HEADER

from com.sun.star.connection import NoConnectException

from com.sun.star.rest import ConnectionException
from com.sun.star.rest import ConnectTimeoutException
from com.sun.star.rest import ReadTimeoutException

from .requestresponse import execute
from .requestresponse import getDuration
from .requestresponse import getExceptionMessage
from .requestresponse import raiseHTTPException
from .requestresponse import raiseRequestException
from .requestresponse import RequestResponse

from .unotool import getSimpleFile

from requests.exceptions import HTTPError
from requests.exceptions import RequestException as RequestError
import time
from datetime import timedelta
import re
import traceback


def download(ctx, source, logger, session, parameter, url, timeout, chunk, retry, delay):
    downloaded = False
    cls, mtd = 'OAuth2Service', 'download()'
    retry = max(1, retry)
    sf = getSimpleFile(ctx)
    stream = sf.openFileWrite(url)
    while retry > 0:
        retry -= 1
        try:
            response = execute(ctx, source, session, cls, mtd, parameter, timeout, True)
        except RequestException as e:
            logger.logprb(SEVERE, cls, mtd, 122, parameter.Name, traceback.format_exc())
            if not retry > 0:
                stream.closeOutput()
                raise e
            time.sleep(delay)
        else:
            if response.ok:
                try:
                    for buffer in response.iter_content(chunk, False):
                        stream.writeBytes(uno.ByteSequence(buffer))
                except RequestError as e:
                    logger.logprb(SEVERE, cls, mtd, 122, parameter.Name, traceback.format_exc())
                    if not retry > 0:
                        stream.closeOutput()
                        raiseRequestException(ctx, source, cls, mtd, parameter.Name, 123, e)
                    print('request.download() Download ERROR')
                    range = 'bytes=%s-' % stream.getLength()
                    parameter.setHeader('Range', range)
                    time.sleep(delay)
                else:
                    d = getDuration(response.elapsed)
                    logger.logprb(INFO, cls, mtd, 121, url, d.Hours, d.Minutes, d.Seconds, d.NanoSeconds)
                    retry = 0
                    downloaded = True
            else:
                if not retry > 0:
                    stream.closeOutput()
                    _raiseResponseException(ctx, source, cls, mtd, 123, parameter, response)
                time.sleep(delay)
    stream.closeOutput()
    return downloaded


def upload(ctx, source, logger, session, parameter, url, timeout, chunk, retry, delay):
    sf = getSimpleFile(ctx)
    if not sf.exists(url):
        e = FileNotFoundException()
        e.Context = source
        e.FileUrl = url
        e.Url = parameter.Url
        raise e
    response = None
    cls, mtd = 'OAuth2Service', 'upload()'
    stream = sf.openFileRead(url)
    # TODO: If the given parameter is resumable we do a resumable upload
    if parameter.isResumable():
        start = 0
        retry = max(1, retry)
        size = sf.getSize(url)
        uploader = Uploader(ctx, source, session, parameter, timeout, size, cls, mtd)
        while retry > 0:
            try:
                stream.seek(start)
                length, data = stream.readBytes(None, chunk)
                if uploader.uploadRange(start, length, data):
                    delta = uploader.Elapsed
                    logger.logprb(INFO, cls, mtd, 131, url, uploader.Count, delta.Hours, delta.Minutes, delta.Seconds, delta.NanoSeconds)
                    retry = 0
                    response = uploader.Response
                else:
                    start = uploader.NextRange
            except RequestException as e:
                retry -= 1
                logger.logprb(SEVERE, cls, mtd, 133, parameter.Name, traceback.format_exc())
                if not retry > 0:
                    stream.closeInput()
                    raise e
                time.sleep(delay)
    # TODO: As the given parameter is not resumable we do a normal upload
    else:
        parameter.DataSink = stream
        try:
            upload = execute(ctx, source, session, cls, mtd, parameter, timeout, True)
        except RequestException as e:
            logger.logprb(SEVERE, cls, mtd, 133, parameter.Name, traceback.format_exc())
            stream.closeInput()
            raise e
        else:
            delta = getDuration(upload.elapsed)
            logger.logprb(INFO, cls, mtd, 131, url, 1, delta.Hours, delta.Minutes, delta.Seconds, delta.NanoSeconds)
            response = RequestResponse(ctx, parameter, upload)
    stream.closeInput()
    return response


class Uploader():
    def __init__(self, ctx, source, session, parameter, timeout, size, cls, mtd):
        self._ctx = ctx
        self._source = source
        self._session = session
        self._parameter = parameter
        self._regex = re.compile(parameter.RangePattern, re.UNICODE)
        self._range = None
        self._timeout = timeout
        self._size = size
        self._cls = cls
        self._mtd = mtd
        self._delta = timedelta()
        self._count = 0
        self._response = None

    @property
    def NextRange(self):
        return self._getNextRange()
    @property
    def Count(self):
        return self._count
    @property
    def Elapsed(self):
        return getDuration(self._delta)
    @property
    def Response(self):
        return self._response

    def uploadRange(self, start, length, data):
        self._parameter.Data = data
        end = start + length -1
        range = 'bytes %s-%s/%s' % (start, end, self._size)
        self._parameter.setHeader('Content-Range', range)
        response = execute(self._ctx, self._source, self._session, self._cls, self._mtd, self._parameter, self._timeout)
        self._status = response.status_code
        self._delta += response.elapsed
        self._count += 1
        if self._status == OK or self._status == CREATED:
            self._response = RequestResponse(self._ctx, self._parameter, response)
            return True
        if self._status == self._parameter.RangeStatus and self._hasRange(response):
            response.close()
            return False
        _raiseResponseException(self._ctx, self._source, self._cls, self._mtd, 134, self._parameter, response)

    def _hasRange(self, response):
        if self._regex is not None:
            if self._parameter.RangeType == HEADER:
                return self._hasDataRange(response.headers)
            if self._parameter.RangeType == JSON:
                return self._hasDataRange(response.json())
        return False

    def _hasDataRange(self, data):
        self._range = matched = None
        if self._parameter.RangeField in data:
            range = data.get(self._parameter.RangeField)
            # FIXME: Some provider like Microsoft give a Range as a JSON list
            # FIXME: if so we only get the first value
            if isinstance(range, list):
                range = range[0]
            matched = self._regex.search(range)
            if matched:
                self._range = matched.group(1)
        return self._range is not None

    def _getNextRange(self):
        return int(self._range) + self._parameter.RangeOffset


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


def getInputStream(ctx, source, session, cls, mtd, parameter, timeout, chunk, decode):
    response = execute(ctx, source, session, cls, mtd, parameter, timeout, True)
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


def _raiseResponseException(ctx, source, cls, mtd, code, parameter, response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        raiseHTTPException(ctx, source, cls, mtd, parameter.Name, code, e)
    else:
        raiseRequestException(ctx, source, cls, mtd, parameter.Name, code, e)

