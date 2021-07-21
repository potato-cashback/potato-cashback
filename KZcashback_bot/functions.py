import re
import json

from datetime import datetime
from pytz import timezone

class Data(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

class Keyformat(object):
    def __init__(self, type='callback', texts=[], callbacks=[], urls=[]):
        self.type = type
        self.texts = texts
        self.callbacks = callbacks
        self.urls = urls


class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    if isinstance(v, list):
                        self.__convert(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                elif isinstance(v, list):
                    self.__convert(v)
                self[k] = v

    def __convert(self, v):
        for elem in range(0, len(v)):
            if isinstance(v[elem], dict):
                v[elem] = Map(v[elem])
            elif isinstance(v[elem], list):
                self.__convert(v[elem])

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

def getFromArrDict(arr, name, val):
    for x in arr:
        if x[name] == val:
            return x
    return None

def previous(path):
    return re.search(r'(.+\/)+', path)[0][:-1]


def get_today():
    local_now = datetime.now(timezone('Asia/Almaty'))
    return local_now


def sign(x):
    if x - abs(x) == 0:
        return '+'
    return '-'

def in_array(arr, x):
    for y in arr:
        key = list(y.keys())[0]
        if key == x:
            return True
    return False

def cashback_logic(sum, cashback):
    res = 0
    if sum >= 5000: res = cashback[1]
    elif sum >= 3000: res = cashback[0]
    return res