#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-24 https://prrvchr.github.io                                  ║
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

import unohelper

from com.sun.star.logging.LogLevel import INFO
from com.sun.star.logging.LogLevel import SEVERE

from .optionsmodel import OptionsModel
from .optionsview import OptionsView
from .optionshandler import OptionsListener

from ..logger import LogManager

from ..unotool import executeFrameDispatch
from ..unotool import getDesktop
from ..unotool import getPropertyValueSet

from ..oauth2 import getOAuth2UserName

from ..configuration import g_identifier
from ..configuration import g_defaultlog

import traceback


class OptionsManager(unohelper.Base):
    def __init__(self, ctx, window, logger):
        self._ctx = ctx
        self._logger = logger
        self._model = OptionsModel(ctx)
        window.addEventListener(OptionsListener(self))
        self._view = OptionsView(window)
        self._view.initView(OptionsManager._restart, *self._model.getOptionsData())
        self._logmanager = LogManager(ctx, window.getPeer(), 'requirements.txt', g_defaultlog)
        self._logger.logprb(INFO, 'OptionsManager', '__init__()', 151)

    _restart = False

    def dispose(self):
        self._logmanager.dispose()

    def loadSetting(self):
        self._view.initView(OptionsManager._restart, *self._model.getOptionsData())
        self._logmanager.loadSetting()
        self._logger.logprb(INFO, 'OptionsManager', 'loadSetting()', 161)

    def saveSetting(self):
        connect, read, handler = self._view.getViewData()
        self._model.setOptionsData(connect, read, handler)
        option = self._model.commit()
        if self._logmanager.saveSetting():
            OptionsManager._restart = True
            self._view.setRestart(True)
        self._logger.logprb(INFO, 'OptionsManager', 'saveSetting()', 171, option, OptionsManager._restart)

    def connect(self):
        user = url = ''
        try:
            url = self._view.getUrl()
            if url != '':
                message = self._model.getProviderName(url)
                user = getOAuth2UserName(self._ctx, self, url, message)
            close = self._view.getAutoClose()
            args = getPropertyValueSet({'Url': url, 'UserName': user, 'Close': close})
            frame = getDesktop(self._ctx).getCurrentFrame()
            if frame is not None:
                executeFrameDispatch(self._ctx, frame, 'oauth2:wizard', args)
                self._logger.logprb(INFO, 'OptionsManager', 'connect()', 181, user, url)
            else:
                self._logger.logprb(INFO, 'OptionsManager', 'connect()', 182, user, url)
        except Exception as e:
            print("OptionsManager.connect() ERROR: %s - %s" % (e, traceback.format_exc()))
            self._logger.logprb(SEVERE, 'OptionsManager', 'connect()', 183, user, url, e, traceback.format_exc())

