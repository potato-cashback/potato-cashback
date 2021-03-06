import traceback
import py_modules.telegram.telegram as telegram
import py_modules.telegram.classes as classes
from py_modules.mongo import users

import re
import json
import urllib.request
import traceback
import base64

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

def cashback_logic(sum):
	sum = int(sum)
	[cashback] = telegram.get("cashback")
	print(cashback)
	arr_cashback = [cashback[x] for x in cashback]
	print(arr_cashback)
	arr_cashback = sorted(arr_cashback, key=lambda k: k['on'])
	for i in range(len(arr_cashback)):
		if i+1 == len(arr_cashback):
			if arr_cashback[i]['on'] <= sum:
				return arr_cashback[i]['percent'] / 100
		elif arr_cashback[i]['on'] <= sum and sum < arr_cashback[i+1]['on']:
			return arr_cashback[i]['percent'] / 100
	return 0

def find_user(search):
	user = users.find_one(search) or {}
	return classes.User(user)

def calc(query):
	value = []
	if '?' in query:
		value = re.search(r'\?.+', query)[0][1:].split(',')
		for i in range(len(value)):
			try: value[i] = int(value[i])
			except: pass
		query = re.search(r'^[^\?]+', query)[0]
	return [query, value]

def check_if_registered(message, user):
	if not user['registered']:
		telegram.register(message)
		return False
	return True

def set_phone_template(phone_number):
	hasPlus = (phone_number[0] == '+')
	if not hasPlus:
		return '+' + phone_number
	return phone_number


def convertBase64ToImage(uri):
	decoded = base64.b64decode(uri)
	img = Image.open(BytesIO(decoded))
	return img

# MONGODB UPDATES
# <==========================================>
def update_user(userId, function_name = "", set_args = {}, push_args = {}, pull_args = {}):
	if function_name != "": 
		users.update_one({'_id': userId}, {'$set': {'function_name': function_name, 'use_function': (function_name != '#')}})

	if set_args != {}: users.update_one({'_id': userId}, {'$set': set_args})
	if push_args != {}: users.update_one({'_id': userId}, {'$push': push_args})
	if pull_args != {}: users.update_one({'_id': userId}, {'$pull': pull_args})
	return
# <==========================================>

def techincal_stop_check(update):
	[notifications, TECHNICAL_STOP] = telegram.get("tree.notifications", "TECHNICAL_STOP")
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
			telegram.bot.send_message(userId, notifications['stop'])
			return True
	return False


def get_data_from_qr(photo):

	photo_id = photo.file_id
	file_photo = telegram.bot.get_file(photo_id)
	downloaded_file_photo = telegram.bot.download_file(file_photo.file_path)

	img = Image.open(BytesIO(downloaded_file_photo))
	decoded = decode(img)

	print(decoded)
	try:
		qr_data = json.loads(decoded[0].data)
		url = telegram.URL_ser+'/api/react/'+str(qr_data['date'])
		response = urllib.request.urlopen(url).read()
		status = json.loads(response)

		if status['status'] == 'not ok':
			return 'not ok'
		return qr_data
	except:
		print(traceback.format_exc())
		return 'not found'

def create_keyboard(arr, vals):
	keyboard = InlineKeyboardMarkup()
	i = 0
	for lst in arr:
		buttons = []
		for button in lst:
			if not vals[i].hideButton:
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