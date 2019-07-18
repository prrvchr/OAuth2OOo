#!
# -*- coding: utf_8 -*-

import uno
import unohelper

from com.sun.star.task import XInteractionRequest
from com.sun.star.task import XInteractionAbort
from com.sun.star.auth import XInteractionUserName


class InteractionAbort(unohelper.Base,
                       XInteractionAbort):
    # XInteractionAbort
    def select(self):
        pass


class InteractionUserName(unohelper.Base,
                          XInteractionUserName):
    def __init__(self, result):
        self.result = result
        self.username = ''
    # XInteractionSupplyParameters
    def setUserName(self, name):
        self.username = name
    def select(self):
        self.result.Value = self.username
        self.result.IsPresent = True


class InteractionRequest(unohelper.Base,
                         XInteractionRequest):
    def __init__(self, request, response):
        self.request = request
        self.continuations = (InteractionAbort(), InteractionUserName(response))
    # XInteractionRequest
    def getRequest(self):
        return self.request
    def getContinuations(self):
        return self.continuations
