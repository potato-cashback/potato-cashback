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

class Account(dict):
    def __init__(self, user):
        today = get_today()
        self._id = user['_id']

        self.register_date  = user.get('register_date', today.strftime("%d/%m/%Y"))
        self.register_time = user.get('register_time', today.strftime("%H:%M"))
        self.registered = user.get('registered', False)

        self.name = user.get('name', '')
        self.username = user.get('username', '')

        self.phone =  user.get('phone', '')
        self.balance = user.get('balance', 0)
        self.all_balance = user.get('all_balance', 0)

        self.friends = user.get('friends', {})
        self.limit_items = user.get('limit_items', {sectionName:{itemTag:0 for itemTag in items[sectionName]} for sectionName in items})

        self.function_name = user.get('function_name', '#')
        self.use_function = user.get('use_function', False)
        self.prev_message = user.get('prev_message', '#')
        self.month = user.get('prev_message', today.strftime("%m"))

        self.operations = user.get('operations', [])