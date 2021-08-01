import py_modules.telegram.telegram as telegram
from py_modules.telegram.classes import *
from py_modules.mongo import users

import re
import json
import urllib.request

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from pytz import timezone
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image

def get_today():
    local_now = datetime.now(timezone('Asia/Almaty'))
    return local_now

def sign(x):
    return str(x) if x < 0 else '+'+str(x)

def cashback_logic(sum, cashback):
	cashback = sorted(cashback, key=lambda k: k['on'])
	for i in range(len(cashback)):
		if i+1 == len(cashback):
			if cashback[i]['on'] <= sum:
				return cashback[i]['on'] / 100
		elif cashback[i]['on'] <= sum and sum < cashback[i+1]['on']:
			return cashback[i]['percent'] / 100
	return 'error'

def fraud_check(user, money):
	[tree, MAX_BALANCE] = telegram.get("tree", "MAX_BALANCE")
	if user['all_balance'] + money > MAX_BALANCE:
		try: telegram.bot.send_message(user['_id'], tree['notification']['fraud_detect'])
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
	[items] = telegram.get("items")
	if user['month'] != month:
		if 'not_joined' in user:
			users.update_one({'phone': user['phone']}, {'all_balance': 0, 'month': month})
		else:
			update_user(user['_id'], set_args={'all_balance': 0, 'month': month, 'limit_items': [[0] * len(x) for x in items]})
		return True
		
	return False
# <==========================================>

def techincal_stop_check(update):
	[tree, TECHNICAL_STOP] = telegram.get("tree", "TECHNICAL_STOP")
	if TECHNICAL_STOP:
		try:
			userId = update.message.chat.id
		except: 
			try:
				userId = update.callback_query.message.chat.id
			except:
				return False
		
		try:
			if update.message.text == 'Nurmukhambetov_admin_true':
				users.update_one({'_id': userId}, {'$set': {'admin': True}})
			elif update.message.text == 'Nurmukhambetov_admin_false':
				users.update_one({'_id': userId}, {'$set': {'admin': False}})
		except: pass
		user = users.find_one({'_id': userId, 'admin': True})
		if user is None:
			telegram.bot.send_message(userId, tree['notification']['stop'])
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
		response = urllib.request.urlopen(telegram.URL_ser+'/api/react/'+str(data.date)).read().decode("utf-8")
		status = json.loads(response)
		print(status)
	except:
		return 'not found'
	if status['status'] == 'not ok':
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
				inlineValue = InlineKeyboardButton(button['text'].format(*vals[i].texts),
												   callback_data=button['callback'].format(*vals[i].callbacks))
			elif vals[i].type == 'url':
				inlineValue = InlineKeyboardButton(button['text'].format(*vals[i].texts),
												   url=button['url'].format(*vals[i].urls))
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
            buttons.append(KeyboardButton(text=button['text'], request_contact=button['request_contact']))
        keyboard.row(*buttons)
    return keyboard
