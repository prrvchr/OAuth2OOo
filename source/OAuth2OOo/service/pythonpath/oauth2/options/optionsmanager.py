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

from .optionsmodel import OptionsModel
from .optionsview import OptionsView
from .optionshandler import OptionsListener

from ..logger import LogManager

from ..unotool import createService
from ..unotool import executeFrameDispatch
from ..unotool import getDesktop
from ..unotool import getExceptionMessage
from ..unotool import getPropertyValueSet

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
        self._model = OptionsModel(ctx)
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
        infos['six'] =                ('__version__',     '1.16.0')
        infos['ssl'] =                ('OPENSSL_VERSION', None)
        infos['idna'] =               ('__version__',     '3.4')
        infos['charset_normalizer'] = ('__version__',     '3.1.0')
        infos['certifi'] =            ('__version__',     '2023.05.07')
        infos['urllib3'] =            ('__version__',     '2.0.3')
        infos['requests'] =           ('__version__',     '2.31.0')
        infos['lxml'] =               ('__version__',     '4.9.2')
        infos['ijson'] =              ('__version__',     '3.2.2')
        infos['selenium'] =           ('__version__',     '4.10.0')
        infos['webdriver_manager'] =  ('__version__',     '3.8.6')
        infos['rdflib'] =             ('__version__',     '7.0.0')
        infos['pyRdfa'] =             ('__version__',     '3.5.3')
        infos['parsel'] =             ('__version__',     '1.8.1')
        infos['cssselect'] =          ('__version__',     '1.2.0')
        return infos

    def connect(self):
        try:
            user = ''
            url = self._view.getUrl()
            if url != '':
                message = self._model.getProviderName(url)
                user = getOAuth2UserName(self._ctx, self, url, message)
                print("OptionsManager.connect() 1 %s" % user)
            close = self._view.getAutoClose()
            args = getPropertyValueSet({'Url': url, 'UserName': user, 'Close': close})
            frame = getDesktop(self._ctx).getCurrentFrame()
            if frame is not None:
                executeFrameDispatch(self._ctx, frame, 'oauth2:wizard', args)
        except Exception as e:
            msg = "Error: %s - %s" % (e, traceback.format_exc())
            print(msg)
            getLogger(self._ctx, g_errorlog).logp(SEVERE, 'OptionsManager', 'connect()', msg)

    def _getExceptionMsg(self, e):
        error = str(e)
        trace = str(traceback.format_exc())
        return error, trace

