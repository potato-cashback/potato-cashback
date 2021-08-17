import py_modules.telegram.telegram as telegram
from py_modules.telegram.functions import *

class Keyformat(object):
    def __init__(self, type='callback', texts=[], callbacks=[], urls=[], hideButton=False):
        self.type = type
        self.hideButton = hideButton
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
        self.admin = user.get('admin', False)

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

        self.polls = user.get('polls', {})

        self.operations = user.get('operations', [])

    def set_new_poll(self, poll):
        self.polls[poll.id] = {
            'question': poll.question,
            'options': [option.__dict__ for option in poll.options],
            'answer': "",
        } 
        self.overwrite_data()

    def update_poll_answer(self, poll_id, choosen_option):
        answer = self.polls[poll_id]['options'][choosen_option].text
        self.polls[poll_id]['answer'] = answer
        self.overwrite_data()

    def is_admin(self):
        return self.admin

    def send_notification(self, message_text):
        telegram.bot.send_message(self._id, message_text, parse_mode="html")

    def add_cashback_to_their_friends(self):
        [notifications, friend_money] = telegram.get("tree.notifications", "friend_money")

        users_to_add_balance = users.find({f'friends.{self.phone}': False})
        for user in users_to_add_balance:
            user = User(user)
            user.send_notification(notifications['friend_join'].format(self.phone, friend_money))

            new_operation = self.create_operation(self.phone[1:], friend_money)
            # [1:] is important, max length for operation text is 12.
            # Exceeding it will casuse offset in a telegram message.
            user.push_operation(new_operation)
            user.update_balance(friend_money)
            user.friends[self.phone] = True
            user.overwrite_data()

    def add_previous_cashback_from_phone(self):
        [register] = telegram.get("tree.register")
        search_key = {'phone': self.phone, 'onTelegram': False}
        if users.find_one(search_key) is not None:
            prev_user_data = find_user(search_key)

            self.update_balance(prev_user_data.balance)

            for operation in prev_user_data.operations:
                self.push_operation(operation)

            users.delete_one({'phone': self.phone, 'onTelegram': False})

            self.send_notification(register['previous_cashbacks'].format(prev_user_data.balance))
            return

    def on_first_registery(self):
        [register, operations, welcome_cashback_sum] = telegram.get("tree.register", "tree.operations", "welcome_cashback_sum")
        
        self.set_value('registered', True)
        self.update_balance(welcome_cashback_sum)

        new_operation = self.create_operation(operations['register'], welcome_cashback_sum)
        self.push_operation(new_operation)

        self.send_notification(register['welcome_casback'].format(welcome_cashback_sum))
        return 

    def fraud_check(self, value):
        [MAX_BALANCE] = telegram.get("MAX_BALANCE")
        return self.all_balance + value > MAX_BALANCE

    def next_step_handler(self, function_name):
        self.function_name = function_name
        self.use_function = True
        self.overwrite_data()

    def clear_next_step_handler(self):
        self.function_name = '#'
        self.use_function = False
        self.overwrite_data()

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
        self.__dict__[key] = value
        users.update_one({'_id': self._id}, {'$set': {key: value}})
    def overwrite_data(self):
        data = self.__dict__
        old_data = users.find_one({'_id': self._id})
        for key in data:
            if old_data[key] == data[key]: continue
            self.set_value(key, data[key])

    def is_new_month(self):
        todays_month = get_today().strftime("%m")
        if todays_month != self.month:
            self.month = todays_month
            return True
        return False

    def update_balance(self, value):
        self.balance += value
        if value > 0: 
            self.all_balance += value
        self.overwrite_data()
        
    def user_exists(self, _id=None, phone=None):
        if _id is None and phone is None:
            return False
        
        user = users.find_one({'_id': _id}) or users.find_one({'phone': phone, 'registered': True})
        return user is not None
    
    def phone_in_friends_list(self, phone):
        return phone in self.friends

    def friend_list_stringify(self):
        friends = ""
        buffer_counter = 1
        for friends_phone in self.friends:
            friendOnTelegram = self.friends[friends_phone]
            if not friendOnTelegram:
                friends += f"{buffer_counter}. {friends_phone}\n"
                buffer_counter += 1

        return friends if friends != "" else ": 0"

    def add_friend_contact(self, contact):
        if contact is None: return 'no contact'

        [notifications] = telegram.get("tree.notifications")
        friends_phone = set_phone_template(contact.phone_number)
        if not self.user_exists(phone=friends_phone):
            if not self.phone_in_friends_list(friends_phone):
                self.friends[friends_phone] = False
                self.overwrite_data()
                return 'ok'
            else:
                self.send_notification(notifications['user_is_in_contacts'].format(friends_phone))
                return
        else:
            self.send_notification(notifications['user_already_joined'].format(friends_phone))
            return
    
    def set_phone(self, new_phone):
        self.phone = new_phone
        self.overwrite_data()
    
    def set_name(self, new_name):
        self.name = new_name
        self.overwrite_data()
