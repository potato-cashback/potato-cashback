import json

class Data(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

class Keyformat(object):
    def __init__(self, type='callback', texts=[], callbacks=[], urls=[]):
        self.type = type
        self.texts = texts
        self.callbacks = callbacks
        self.urls = urls