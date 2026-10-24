#!
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   Copyright (c) 2020-25 https://prrvchr.github.io                                  ║
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

from .logger import LogManager

from ..runner import DispatchListener

from ..setup import SetupCheck

from ..setup import showSetup

from ..unotool import executeDispatch
from ..unotool import getDesktop

from ..oauth20 import getOAuth2UserName
from ..oauth20 import showOAuth2

from ..configuration import State
from ..configuration import g_defaultlog
from ..configuration import g_identifier

import traceback


class OptionsManager(unohelper.Base):
    def __init__(self, ctx, window, logger):
        self._ctx = ctx
        self._disposed = False
        self._model = OptionsModel(ctx)
        window.addEventListener(OptionsListener(self))
        self._view = OptionsView(window, *self._model.getViewData())
        self._logmanager = LogManager(ctx, window, 'requirements.txt', g_defaultlog)
        self._logmanager.initView()
        self._logger = logger
        self._logger.logprb(INFO, 'OptionsManager', '__init__()', 151)
        self._loadView(self.init)

    def init(self, state):
        if not self._disposed:
            self._view.initView(*self._model.getInitData(state))
            self._logmanager.loadSetting()
            self._logger.logprb(INFO, 'OptionsManager', 'init()', 161)

    def refresh(self, state):
        if not self._disposed:
            self._view.refreshView(state)

    def dispose(self):
        self._disposed = True
        self._logmanager.dispose()
        self._view.dispose()

    def loadSetting(self):
        self._loadView(self.init)

    def saveSetting(self):
        self._model.setOptionsData(*self._view.getViewData())
        option = self._model.commit()
        if self._logmanager.saveSetting():
            State.restart = True
            self._loadView(self.refresh)
        self._logger.logprb(INFO, 'OptionsManager', 'saveSetting()', 171, option, State.restart)

    def connect(self):
        user = url = ''
        try:
            url = self._view.getUrl()
            if url != '':
                message = self._model.getProviderName(url)
                user = getOAuth2UserName(self._ctx, self, url, message)
            readonly = user and url
            parent = self._view.getWindow()
            close = self._view.getAutoClose()
            showOAuth2(self._ctx, Url=url, User=user, ReadOnly=readonly, Parent=parent, Close=close)
            self._logger.logprb(INFO, 'OptionsManager', 'connect()', 181, user, url)
        except Exception as e:
            print("OptionsManager.connect() ERROR: %s - %s" % (e, traceback.format_exc()))
            self._logger.logprb(SEVERE, 'OptionsManager', 'connect()', 182, user, url, e, traceback.format_exc())

    def showSetup(self):
        mode = self._view.getSetup()
        showSetup(self._ctx, Dispatch=DispatchListener(self), Mode=mode)

    def dispatchFinished(self, notification):
        if not self._disposed:
            self._loadView(self.refresh)

    def _loadView(self, callback):
        mode = self._view.getSetup()
        setup = SetupCheck(self._ctx, callback, database=None, java=None, agent=None, python=True, mode=mode)
        setup.start()
