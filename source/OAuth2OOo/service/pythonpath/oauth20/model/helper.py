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

import traceback

from ..configuration import State

try:
    import validators
except TypeError as e:
    print("model.helper TypeError ERROR: %s" % traceback.format_exc())
    State.restart = True
except Exception as e:
    print("model.helper Exception ERROR: %s" % traceback.format_exc())
    State.restart = True


def isEmailValid(email):
    if validators.email(email):
        return True
    return False

# Get the Provider name from an Url
def getProviderName(config, url):
    provider = ''
    if config.getByName('Urls').hasByName(url):
        scope = config.getByName('Urls').getByName(url).getByName('Scope')
        if config.getByName('Scopes').hasByName(scope):
            provider = config.getByName('Scopes').getByName(scope).getByName('Provider')
    return provider

def isAuthorized(urls, scopes, providers, url, user):
    if urls.hasByName(url):
        scope = urls.getByName(url).getByName('Scope')
        if scopes.hasByName(scope):
            provider = scopes.getByName(scope).getByName('Provider')
            return isUserAuthorized(scopes, providers, scope, provider, user)
    return False

def isUserAuthorized(scopes, providers, scope, provider, user):
    if providers.hasByName(provider):
        users = providers.getByName(provider).getByName('Users')
        if users.hasByName(user):
            values = users.getByName(user).getByName('Scopes')
            if scopes.hasByName(scope):
                for s in scopes.getByName(scope).getByName('Values'):
                    if s not in values:
                        return False
                return True
    return False

