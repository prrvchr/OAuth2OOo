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
from .optionshandler import OptionsListener

from ..oauth2model import OAuth2Model
from ..logger import LogManager

from ..unotool import createService
from ..unotool import getExceptionMessage

from ..oauth2 import getOAuth2UserName
from ..oauth2 import g_oauth2

from ..configuration import g_identifier
from ..configuration import g_defaultlog
from ..configuration import g_errorlog

from ..logger import getLogger

from collections import OrderedDict
import os
import sys
import traceback


class OptionsManager(unohelper.Base):
    def __init__(self, ctx, window):
        self._ctx = ctx
        self._model = OAuth2Model(ctx)
        self._view = OptionsView(window)
        connect, read, handler, urls = self._model.getOptionsDialogData()
        self._view.initView(connect, read, handler, urls)
        self._logger = LogManager(ctx, window.Peer, self._getInfos(), g_identifier, g_defaultlog)
        window.addEventListener(OptionsListener(self))

    def dispose(self):
        self._logger.dispose()

    def saveSetting(self):
        self._model.ConnectTimeout = self._view.getConnectTimeout()
        self._model.ReadTimeout = self._view.getReadTimeout()
        self._model.HandlerTimeout = self._view.getHandlerTimeout()
        self._model.commit()
        self._logger.saveSetting()

    def loadSetting(self):
        connect, read, handler, urls = self._model.getOptionsDialogData()
        self._view.initView(connect, read, handler, urls)
        self._logger.loadSetting()

    def _getInfos(self):
        infos = OrderedDict()
        version  = ' '.join(sys.version.split())
        infos[111] = version
        path = os.pathsep.join(sys.path)
        infos[112] = path
        # Required modules for Requests
        try:
            import six
        except Exception as e:
            infos[120] = self._getExceptionMsg(e)
        else:
            infos[121] = six.__version__, six.__file__
        try:
            import ssl
        except Exception as e:
            infos[122] = self._getExceptionMsg(e)
        else:
            infos[123] = ssl.OPENSSL_VERSION, ssl.__file__
        try:
            import idna
        except Exception as e:
            infos[124] = self._getExceptionMsg(e)
        else:
            infos[125] = idna.__version__, idna.__file__
        try:
            import charset_normalizer
        except Exception as e:
            infos[126] = self._getExceptionMsg(e)
        else:
            infos[127] = charset_normalizer.__version__, charset_normalizer.__file__
        try:
            import certifi
        except Exception as e:
            infos[128] = self._getExceptionMsg(e)
        else:
            infos[129] = certifi.__version__, certifi.__file__
        try:
            import urllib3
        except Exception as e:
            infos[130] = self._getExceptionMsg(e)
        else:
            infos[131] = urllib3.__version__, urllib3.__file__
        try:
            import requests
        except Exception as e:
            infos[132] = self._getExceptionMsg(e)
        else:
            infos[133] = requests.__version__, requests.__file__
        try:
            import lxml
        except Exception as e:
            infos[134] = self._getExceptionMsg(e)
        else:
            infos[135] = lxml.__version__, lxml.__file__
        try:
            import ijson
        except Exception as e:
            infos[136] = self._getExceptionMsg(e)
        else:
            infos[137] = ijson.__version__, ijson.__file__
        try:
            import selenium
        except Exception as e:
            infos[138] = self._getExceptionMsg(e)
        else:
            infos[139] = selenium.__version__, selenium.__file__
        try:
            import webdriver_manager
        except Exception as e:
            infos[140] = self._getExceptionMsg(e)
        else:
            infos[141] = webdriver_manager.__version__, webdriver_manager.__file__
        return infos

    def connect(self):
        try:
            user = ''
            url = self._view.getUrl()
            if url != '':
                message = self._model.getProviderName(url)
                user = getOAuth2UserName(self._ctx, self, url, message)
                print("OptionsManager.connect() 1 %s" % user)
            autoclose = self._view.getAutoClose()
            service = createService(self._ctx, g_oauth2)
            enabled = service.getAuthorization(url, user, autoclose, self._view.getParent())
            service.dispose()
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.format_exc())
            getLogger(self._ctx, g_errorlog).logp(SEVERE, 'OptionsManager', 'connect()', msg)

    def _getExceptionMsg(self, e):
        error = str(e)
        trace = str(traceback.format_exc())
        return error, trace

