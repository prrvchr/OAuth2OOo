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

from .logger.logmanager import LogManager

from .setup.setuphandler import SetupHandler

from .setup.setupmanager import SetupManager

from ..runner.listener import DispatchListener

from ..setup.setupcheck import SetupCheck

from ..config.configuration import State

from ..setup.helper import getSetupListener
from ..setup.helper import removeSetupListener
from ..setup.helper import showSetup

from ..oauth20.oauth2core import getOAuth2UserName

from ..oauth20.oauth2tool import showOAuth2

from ..configuration import g_defaultlog

import traceback


class OptionsManager(unohelper.Base):
    def __init__(self, ctx, window, logger):
        self._ctx = ctx
        self._checker = None
        self._disposed = False
        self._model = OptionsModel(ctx)
        self._view = OptionsView(ctx, window)
        self._logmanager = LogManager(ctx, self._view.getFrame(), 'requirements.txt', g_defaultlog)
        self._setup = SetupManager(ctx, self._view.getSetup(), SetupHandler(self), self._model.getConfig())
        self._listener = OptionsListener(self)
        window.addEventListener(self._listener)
        self._slistener = getSetupListener(ctx, self)
        self._logmanager.initView()
        self._logger = logger
        self._logger.logprb(INFO, 'OptionsManager', '__init__()', 151)
        self._loadView(self.init)
        self._view.getLayout().addLayout(self._logmanager.getLayout()).addLayout(self._setup.getLayout())

    def init(self, state):
        self._checker = None
        if self._disposed:
            return
        self._setup.init()
        self._view.initView(*self._model.getInitData(state))
        self._logmanager.loadSetting()
        self._logger.logprb(INFO, 'OptionsManager', 'init()', 161)

    def refresh(self, state):
        self._checker = None
        if self._disposed:
            return
        self._view.refreshView(*self._model.getRefreshData(state))

    def dispose(self, window):
        if self._disposed:
            return
        self._disposed = True
        self._setup.dispose()
        self._logmanager.dispose()
        self._view.dispose()
        window.removeEventListener(self._listener)
        if self._slistener:
            removeSetupListener(self._ctx, self._slistener)
            self._slistener = None

    def loadSetting(self):
        self._loadView(self.init)

    def saveSetting(self):
        if self._checker:
            self._checker.cancel()
        self._setup.saveSetting()
        self._model.setOptionsData(*self._view.getViewData())
        option = self._model.commit()
        if self._logmanager.saveSetting():
            State.restart = True
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

    def closeSetup(self):
        self._slistener = None
        if self._disposed:
            return
        self._loadView(self.refresh)

    def showSetup(self):
        mode = self._setup.getSetupMode()
        showSetup(self._ctx, Dispatch=DispatchListener(self), Mode=mode)

    def dispatchFinished(self, _notification):
        if self._disposed:
            return
        self._loadView(self.refresh)

    def _loadView(self, callback):
        if self._disposed:
            return
        mode = self._setup.getSetupMode()
        self._checker = SetupCheck(self._ctx, callback, python=True, mode=mode)
        self._checker.start()
