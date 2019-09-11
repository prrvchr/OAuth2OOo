#!
# -*- coding: utf-8 -*-

#from __futur__ import absolute_import

import uno

from .unotools import getInteractionHandler
from .unotools import getOAuth2Request

from .oauth2lib import InteractionRequest


def getUserNameFromHandler(ctx, source, url, message=''):
    username = ''
    message = message if message else "Authentication"
    handler = getInteractionHandler(ctx, message)
    response = uno.createUnoStruct('com.sun.star.beans.Optional<string>')
    request = getOAuth2Request(source, url, message)
    interaction = InteractionRequest(request, response)
    if handler.handleInteractionRequest(interaction):
        if response.IsPresent:
            username = response.Value
    return username
