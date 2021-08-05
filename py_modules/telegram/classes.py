import json
import py_modules.telegram.telegram as telegram
from py_modules.telegram.functions import *

class Data(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

class Keyformat(object):
    def __init__(self, type='callback', texts=[], callbacks=[], urls=[]):
        self.type = type
        self.texts = texts
        self.callbacks = callbacks
        self.urls = urls

def empty_items_shelfs():
    [items] = telegram.get("items")
    return {sectionName: {
                itemTag: 0 for itemTag in items[sectionName]
            } for sectionName in items}

class User(dict):
    def __init__(self, user):
        today = get_today()
        self._id = user.get('_id', 'no id')

        self.register_date  = user.get('register_date', today.strftime("%d/%m/%Y"))
        self.register_time = user.get('register_time', today.strftime("%H:%M"))
        self.registered = user.get('registered', False)
        self.onTelegram = user.get('onTelegram', False)

        self.name = user.get('name', 'no name')
        self.username = user.get('username', 'no username')

        self.phone =  user.get('phone', 'no phone')
        self.balance = user.get('balance', 0)
        self.all_balance = user.get('all_balance', 0)

        self.friends = user.get('friends', {})
        self.limit_items = user.get('limit_items', empty_items_shelfs())

        self.function_name = user.get('function_name', '#')
        self.use_function = user.get('use_function', False)
        self.prev_message = user.get('prev_message', '#')
        self.month = user.get('month', today.strftime("%m"))

        self.operations = user.get('operations', [])

    def is_registered(self):
        return self.registered

    def clear_data_every_month(self):
        if self.is_new_month():
            self.all_balance = 0
            self.limit_items = empty_items_shelfs()
        self.overwrite_data()

    def create_operation(self, name, value, cashback = -1):
        today = get_today()
        date = today.strftime("%d/%m/%Y")
        ctime = today.strftime("%H:%M")
        return {
            'date': date, 
            'time': ctime, 
            'details': name, 
            'sum': value, 
            'cashback': cashback
        }

    def push_operation(self, operation):
        self.operations.append(operation)
        self.push_to_arr('operations', operation)

    def pull_from_arr(self, arr, value):
        users.update_one({'_id': self._id}, {'$pull': {arr: value}})
    def push_to_arr(self, arr, value):
        users.update_one({'_id': self._id}, {'$push': {arr: value}})
    def set_value(self, key, value):
        users.update_one({'_id': self._id}, {'$set': {key: value}})
    def overwrite_data(self):
        data = self.__dict__
        old_data = users.find_one({'_id': self._id})
        for key in data:
            if old_data[key] == data[key]: continue
            self.set_value(key, data[key])

    def is_new_month(self):
        todays_month = get_today().strftime("%m")
        if todays_month == self.month:
            self.month = todays_month
            return True
        return False

    def update_balance(self, value):
        self.balance += value
        self.set_value('balance', self.balance)
        
    def user_exists(self, _id=None, phone=None):
        if _id is None and phone is None:
            return False
        user = users.find_one({'_id': _id}) or users.find_one({'phone': phone, 'registered': True})
        return user is not None
    
    def phone_in_friends_list(self, phone):
        return phone in self.friends

    def add_friend_contact(self, contact):
        [tree] = telegram.get("tree")
        friends_phone = set_phone_template(contact.phone_number)
        if not self.phone_in_friends_list(friends_phone):
            if self.user_exists(phone=friends_phone):
                self.friends[friends_phone] = False
                self.set_value(f'friends.{friends_phone}', False)
                return self.friends
            else:
                return tree['notification']['user_already_joined'].format(friends_phone)
        else:
            return tree['notification']['user_is_in_contacts'].format(friends_phone)
    
    def change_phone(self, new_phone):
        self.phone = new_phone
        self.set_value('phone', self.phone)
    
    def change_name(self, new_name):
        self.name = new_name
        self.set_value('name', self.name)
