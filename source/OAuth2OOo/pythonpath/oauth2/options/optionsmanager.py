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

from .optionsview import OptionsView
from .optionshandler import OptionsHandler

from ..oauth2model import OAuth2Model
from ..logger import LogManager

from ..unotool import createService
from ..unotool import getExceptionMessage

from ..oauth2lib import getOAuth2UserName
from ..oauth2lib import g_oauth2

from ..logger import logMessage
from ..logger import getMessage
g_message = 'OptionsDialog'

import os
import sys
import traceback


class OptionsManager(unohelper.Base):
    def __init__(self, ctx, parent):
        self._ctx = ctx
        self._model = OAuth2Model(ctx)
        self._view = OptionsView(ctx, OptionsHandler(self), parent)
        loggers = {'Logger': 'Logger'}
        self._logger = LogManager(ctx, self._view.getParent(), loggers, self.getInfos)
        self._view.initView(*self._model.getOptionsDialogData())

    def saveSetting(self):
        self._model.ConnectTimeout = self._view.getConnectTimeout()
        self._model.ReadTimeout = self._view.getReadTimeout()
        self._model.HandlerTimeout = self._view.getHandlerTimeout()
        self._model.commit()
        self._logger.saveSetting()

    def reloadSetting(self):
        self._view.initView(*self._model.getOptionsDialogData())
        self._logger.reloadSetting()

    def getInfos(self):
        infos = []
        version  = ' '.join(sys.version.split())
        infos.append(getMessage(self._ctx, g_message, 111, version))
        path = os.pathsep.join(sys.path)
        infos.append(getMessage(self._ctx, g_message, 112, path))
        try:
            import requests
        except ImportError as e:
            infos.append(getMessage(self._ctx, g_message, 114, getExceptionMessage(e)))
        else:
            infos.append(getMessage(self._ctx, g_message, 113, requests.__version__))
        try:
            import urllib3
        except ImportError as e:
            infos.append(getMessage(self._ctx, g_message, 114, getExceptionMessage(e)))
        else:
            infos.append(getMessage(self._ctx, g_message, 115, urllib3.__version__))
        try:
            import chardet
        except ImportError as e:
            infos.append(getMessage(self._ctx, g_message, 116, getExceptionMessage(e)))
        else:
            infos.append(getMessage(self._ctx, g_message, 117, chardet.__version__))
        try:
            import ssl
        except ImportError as e:
            infos.append(getMessage(self._ctx, g_message, 118, e.args[0]))
        else:
            infos.append(getMessage(self._ctx, g_message, 119, ssl.OPENSSL_VERSION))
        return infos

    def connect(self):
        try:
            user = ''
            url = self._view.getUrl()
            if url != '':
                message = self._model.getProviderName(url)
                user = getOAuth2UserName(self._ctx, self, url, message)
            autoclose = self._view.getAutoClose()
            service = createService(self._ctx, g_oauth2)
            enabled = service.getAuthorization(url, user, autoclose, self._view.getParent())
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.print_exc())
            logMessage(self._ctx, SEVERE, msg, "OptionsManager", "doConnect()")

