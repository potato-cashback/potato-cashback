import py_modules.telegram.telegram as telegram
import py_modules.telegram.config as config
from py_modules.mongo import users

import re
import json
import urllib.request

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from datetime import datetime
from pytz import timezone
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image


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

def get_today():
    local_now = datetime.now(timezone('Asia/Almaty'))
    return local_now

def sign(x):
    return str(x) if x < 0 else '+'+str(x)

def cashback_logic(sum, cashback):
    res = 0
    if sum >= 5000: res = cashback[1]
    elif sum >= 3000: res = cashback[0]
    return res

def fraud_check(user, money):
	if user['all_balance'] + money > config.MAX_BALANCE:
		try: telegram.bot.send_message(user['_id'], config.tree.notification.fraud_detect)
		except: pass
		return True
	return False

def create_operation(text, sum, cashback = -1):
	date = get_today().strftime("%d/%m/%Y")
	ctime = get_today().strftime("%H:%M")
	return {'date': date, 'time': ctime, 'details': text, 'sum': sum, 'cashback': cashback}

def calc(query):
	value = -1
	if '?' in query:
		value = re.search(r'\?.+', query)[0][1:].split(',')
		query = re.search(r'^[^\?]+', query)[0]
	return [query, value]

# MONGODB UPDATES
# <==========================================>
def update_user(userId, function_name = "", set_args = {}, push_args = {}, pull_args = {}):
	if function_name != "": 
		users.update_one({'_id': userId}, {'$set': {'function_name': function_name, 'use_function': (function_name != '#')}})

	if set_args != {}: users.update_one({'_id': userId}, {'$set': set_args})
	if push_args != {}: users.update_one({'_id': userId}, {'$push': push_args})
	if pull_args != {}: users.update_one({'_id': userId}, {'$pull': pull_args})
	return

def update_all_balance(user, month = get_today().strftime('%m')):
	if user['month'] != month:
		if user['not_joined']:
			users.update_one({'phone': user['phone']}, {'all_balance': 0, 'month': month})
		else:
			update_user(user['_id'], set_args={'all_balance': 0, 'month': month, 'limit_items': config.empty_limit_arr})
		return True
	return False
# <==========================================>

def techincal_stop_check(update):
	if config.TECHNICAL_STOP:
		try:
			userId = update.message.chat.id
		except:
			userId = update.callback_query.message.chat.id
		
		try:
			if update.message.text == 'Nurmukhambetov_admin_true':
				users.update_one({'_id': userId}, {'$set': {'admin': True}})
			elif update.message.text == 'Nurmukhambetov_admin_false':
				users.update_one({'_id': userId}, {'$set': {'admin': False}})
		except: pass
		user = users.find_one({'_id': userId, 'admin': True})
		if user is None:
			telegram.bot.send_message(userId, config.tree.notification.stop)
			return True
	return False


def get_data_from_qr(message):
	userId = message.chat.id

	photo_id = message.photo[-1].file_id
	file_photo = telegram.bot.get_file(photo_id)
	downloaded_file_photo = telegram.bot.download_file(file_photo.file_path)

	img = Image.open(BytesIO(downloaded_file_photo))
	decoded = decode(img)

	print(decoded)
	# ANTI-FRAUD SYSTEM
	try:
		data = Data(decoded[0].data)
		response = urllib.request.urlopen(config.URL_ser+'/api/react/'+str(data.date)).read().decode("utf-8")
		status = Map(json.loads(response))
		print(status)
	except:
		return 'not found'
	if status.status == 'not ok':
		return 'not ok'

	data.sum = int(data.sum)
	return data

def create_keyboard(arr, vals):
	keyboard = InlineKeyboardMarkup()
	i = 0
	for lst in arr:
		buttons = []
		for button in lst:
			if vals[i].type == 'callback':
				inlineValue = InlineKeyboardButton(button.text.format(*vals[i].texts),
												   callback_data=button.callback.format(*vals[i].callbacks))
			elif vals[i].type == 'url':
				inlineValue = InlineKeyboardButton(button.text.format(*vals[i].texts),
												   url=button.url.format(*vals[i].urls))
			buttons.append(inlineValue)
			i = i + 1
		keyboard.row(*buttons)
	return keyboard

def create_reply_keyboard(arr):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.one_time_keyboard = True

    for lst in arr:
        buttons = []
        for button in lst:
            buttons.append(KeyboardButton(text=button.text, request_contact=button.request_contact))
        keyboard.row(*buttons)
    return keyboard
