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

from .options import OptionsManager

from .configuration import g_extension
from .configuration import g_identifier
from .configuration import g_oauth2

from .unolib import KeyMap

from .unotool import createService
from .unotool import getDialog
from .unotool import getParentWindow
from .unotool import getStringResource

from .dialog import UserHandler
from .dialog import UserView

from .logger import logMessage
from .logger import disposeLogger
from .logger import getMessage

from .oauth2model import OAuth2Model

from .request import Response
from .request import Request
from .request import Enumeration
from .request import Enumerator
from .request import Iterator
from .request import InputStream
from .request import Uploader
from .request import getSessionMode
from .request import execute

from .oauth2lib import OAuth2OOo
from .oauth2lib import NoOAuth2
from .oauth2lib import InteractionRequest
from .oauth2lib import getOAuth2UserName

from .oauth2helper import showOAuth2Wizard

