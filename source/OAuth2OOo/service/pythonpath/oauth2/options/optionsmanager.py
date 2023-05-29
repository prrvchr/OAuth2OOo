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

from six import PY34
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
        # Required modules for cryptography
        try:
            import cffi
        except Exception as e:
            infos[113] = self._getExceptionMsg(e)
        else:
            infos[114] = (cffi.__version__, cffi.__file__)
        # FIXME: Only the backported enum34 has version (ie: python < 3.4)
        if not PY34:
            try:
                import enum
            except Exception as e:
                infos[115] = self._getExceptionMsg(e)
            else:
                infos[116] = '%s.%s.%s' % enum.version, enum.__file__
        try:
            import ipaddress
        except Exception as e:
            infos[117] = self._getExceptionMsg(e)
        else:
            infos[118] = ipaddress.__version__, ipaddress.__file__
        try:
            import six
        except Exception as e:
            infos[119] = self._getExceptionMsg(e)
        else:
            infos[120] = six.__version__, six.__file__
        try:
            import pycparser
        except Exception as e:
            infos[121] = self._getExceptionMsg(e)
        else:
            infos[122] = pycparser.__version__, pycparser.__file__
        try:
            import cryptography
        except Exception as e:
            infos[123] = self._getExceptionMsg(e)
        else:
            infos[124] = cryptography.__version__, cryptography.__file__
        try:
            import ssl
        except Exception as e:
            infos[125] = self._getExceptionMsg(e)
        else:
            infos[126] = ssl.OPENSSL_VERSION, ssl.__file__
        # Required modules for Requests
        try:
            import idna
        except Exception as e:
            infos[127] = self._getExceptionMsg(e)
        else:
            infos[128] = idna.__version__, idna.__file__
        try:
            import chardet
        except Exception as e:
            infos[129] = self._getExceptionMsg(e)
        else:
            infos[130] = chardet.__version__, chardet.__file__
        try:
            import certifi
        except Exception as e:
            infos[131] = self._getExceptionMsg(e)
        else:
            infos[132] = certifi.__version__, certifi.__file__
        try:
            import urllib3
        except Exception as e:
            infos[133] = self._getExceptionMsg(e)
        else:
            infos[134] = urllib3.__version__, urllib3.__file__
        try:
            import requests
        except Exception as e:
            infos[135] = self._getExceptionMsg(e)
        else:
            infos[136] = requests.__version__, requests.__file__
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
        error = repr(e)
        trace = repr(traceback.format_exc())
        return error, trace
