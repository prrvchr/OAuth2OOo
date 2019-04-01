#!
# -*- coding: utf-8 -*-


class JsonHook():
    def __init__(self, parameters, optional):
        self.parameters = parameters
        self.optional = optional

    def hook(self, pairs):
        parameters = {}
        for key, value in pairs:
            print("JsonHook().hook() %s - %s" % (key, value))
            if value is not None:
                if value in self.optional:
                    parameters[key] = self.optional[value]
                else:
                    parameters[key] = value
            elif key in self.optional:
                parameters[key] = self.optional[key]
            elif key in self.parameters:
                del self.parameters[key]
            print("JsonHook().hook() %s" % (parameters, ))
        return parameters
