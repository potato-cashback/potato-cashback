from flask import current_app as app
from py_modules.mongo import users

from io import BytesIO
import re
import os
import json

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from pyzbar.pyzbar import decode
import urllib.request
from PIL import Image

from py_modules.telegram.config import *
from py_modules.telegram.functions import *
from flask import request

bot = telebot.TeleBot(TOKEN)

def update_user(userId, function_name = "", set_args = {}, push_args = {}, pull_args = {}):
	if function_name != "": 
		users.update_one({'_id': userId}, {'$set': {'function_name': function_name, 'use_function': (function_name != '#')}})
	if set_args != {}: users.update_one({'_id': userId}, {'$set': set_args})
	if push_args != {}: users.update_one({'_id': userId}, {'$push': push_args})
	if pull_args != {}: users.update_one({'_id': userId}, {'$pull': pull_args})
	return

@app.route('/bot/'+TOKEN, methods=['POST'])
def getMessage():
	json_string = request.get_data().decode('utf-8')
	update = telebot.types.Update.de_json(json_string)
	
	# TECHNICAL STOP FOR DEBUGS AND CODE FIXES
	if TECHNICAL_STOP:
		print(update)
		try:
			userId = update.message.chat.id
		except:
			userId = update.callback_query.message.chat.id
		
		# ACCESS KEY ONLY FOR ADMINS
		try:
			if update.message.text == 'Nurmukhambetov':
				users.update_one({'_id': userId}, {'$set': {'admin': True}})
		except: pass
		
		user = users.find_one({'_id': userId})
		if user == None or not 'admin' in user:
			bot.send_message(userId, tree.notification.stop)
			return "Bug fixes", 200

	bot.process_new_updates([update])
	return "!", 200

@app.route('/send_data/<phone>/<sum>')
def process_cashback(phone, sum):
	sum = int(sum)
	money = int(sum * cashback_logic(sum, cashback))
	month = get_today().strftime('%m')

	user = users.find_one({'phone': phone})
	# Check if unregistered
	if user == None:
		users.insert_one({
			'phone': phone,
			'balance': 0,
			
			'all_balance': 0,
			'operations': [],
			'not_joined': True,
			'month': month
		})
		user = users.find_one({'phone': phone})

	if user['month'] != month:
		if user['not_joined']:
			users.update_one({'phone': phone}, {'all_balance': 0, 'month': month})
		else:
			update_user(user['_id'], set_args={'all_balance': 0, 'month': month})

	user = users.find_one({'phone': phone})
	
	# FRAUD DETECTION SYSTEM
	if user['all_balance'] + money > MAX_BALANCE:
		try: bot.send_message(user['_id'], tree.notification.fraud_detect)
		except: pass
		return
		
	new_operation = create_operation(tree.operations.photo, sum, money)
	users.update_one({'phone': phone}, {'$set': {'balance': user['balance'] + money,
												 'all_balance': user['all_balance'] + money},
										'$push': {'operations': new_operation}})	

	try: bot.send_message(user['_id'], tree.notification.balance_increase.format(money))
	except: pass

	return 'nice'

@app.route('/bot/')
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url = URL_bot + TOKEN)
	return '!', 200

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

def create_operation(text, sum, cashback = -1):
	date = get_today().strftime("%d/%m/%Y")
	ctime = get_today().strftime("%H:%M")
	return {'date': date, 'time': ctime, 'details': text, 'sum': sum, 'cashback': cashback}

def get_data_from_qr(message):
	userId = message.chat.id

	photo_id = message.photo[-1].file_id
	file_photo = bot.get_file(photo_id)
	downloaded_file_photo = bot.download_file(file_photo.file_path)

	img = Image.open(BytesIO(downloaded_file_photo))
	decoded = decode(img)


	print(decoded)
	# ANTI-FRAUD SYSTEM
	try:
		data = Data(decoded[0].data)
		response = urllib.request.urlopen(URL_ser+'/api/react/'+str(data.date)).read().decode("utf-8")
		status = Map(json.loads(response))
		print(status)
	except Exception as e:
		print('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
		update_user(userId, 'cashback_photo_QR')
		bot.send_message(userId, tree.cashback_photo.qr_not_found)
		return
	if status.status == 'not ok':
		bot.send_message(userId, tree.cashback_photo.wrong_qr)
		menu(message)
		return

	data.sum = int(data.sum)
	return data

@bot.message_handler(commands=['start'])
def menu(message):
	userId = message.chat.id
	month = get_today().strftime("%m")
	print(month)
	user = users.find_one({'_id': userId})
	if user == None:
		date = get_today().strftime("%d/%m/%Y")
		ctime = get_today().strftime("%H:%M")
		nickname = message.chat.username

		users.insert_one({
			'_id': userId,
			'username': nickname,
			'register_date': date,
			'register_time': ctime,
			'balance': 0,
			'all_balance': 0,
			'registered': False,

			'name': '',
			'phone': '', 
			'friends': {},
			'limit_items': empty_limit_arr,

			'function_name': '#',
			'use_function': False,
			'prev_message': '#',
			'month': month,

			'operations': [],
		})
	else:
		if user['month'] != month:
			update_user(userId, set_args={'all_balance': 0, 'limit_items': empty_limit_arr})
		update_user(userId, function_name='#', set_args={'prev_message': '#', 'month': month})

	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.menu.buttons, currentInlineState)
	bot.send_message(userId, tree.menu.text, reply_markup=keyboard)

# EXTRACT LIST SYSTEM
# <+=============================================================================================+>
@bot.message_handler(commands=['extract'])
def extract(message):
	userId = message.chat.id
	user = users.find_one({'_id': userId})

	if not user['registered']:
		register(message)
		return

	clen = [0, 0]
	for x in user['operations']:
		clen[0] = max(clen[0], len(x['date']) - 2)
		value = x['cashback']
		if value == -1: value = x['sum']
		clen[1] = max(clen[1], len(str(abs(value))))

	msg = '<code>'+'ДАТА'.center(clen[0]+ 1)+'|'+'СУММА'.center(clen[1] + 4)+'|'+' ОПЕРАЦИИ'+'\n'

	for x in user['operations']:
		value = x['cashback']
		if value == -1: value = x['sum']
		sub = clen[1] - len(str(abs(value)))
		new_date = re.sub(r'2021','21', x['date'])
		msg = msg + '{} | {}{}{}₸ | {}\n'.format(new_date, sub*' ', sign(value), abs(value), x['details'])
	msg = msg + '\nОстаток: {}₸</code>'.format(user['balance'])

	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree.extract.buttons, currentInlineState)
	bot.send_message(userId, msg, reply_markup=keyboard, parse_mode='html')
# <+=============================================================================================+>


# GIFT MANANGMENT
# <+=============================================================================================+>
def list_sections(message):
	userId = message.chat.id

	currentInlineState = [Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.list_sections.buttons, currentInlineState)
	bot.send_message(userId, tree.list_sections.text, reply_markup=keyboard)
def list_gifts(message, value):
	userId = message.chat.id
	[toyId, sectionId] = [int(x) for x in value]
	item = items[sectionId][toyId]

	currentInlineState = [
		Keyformat(texts=[item.price], callbacks=[toyId, sectionId]),
		Keyformat(callbacks=[(toyId if toyId > 0 else len(items[sectionId])) - 1, sectionId]),
		Keyformat(callbacks=[toyId, sectionId]),
		Keyformat(callbacks=[toyId+1 if toyId < len(items[sectionId])-1 else 0, sectionId]),
		Keyformat(texts=[toyId + 1, len(items[sectionId])], callbacks=[toyId, sectionId]),
		Keyformat()]

	keyboard = create_keyboard(tree.list_gifts.buttons, currentInlineState)
	bot.send_photo(chat_id=userId, 
				   photo=item.image, 
				   reply_markup=keyboard)
def buy_gift(message, value):
	userId = message.chat.id
	user = users.find_one({'_id': userId})
	if not user['registered']:
		bot.send_message(userId, tree.notification.not_registered)
		menu(message)
		return

	[toyId, sectionId] = [int(x) for x in value]
	item = items[sectionId][toyId]

	date = get_today().strftime("%d/%m/%Y")

	currentInlineState = [Keyformat(callbacks=[toyId, sectionId]), Keyformat(callbacks=[sectionId])]
	keyboard = create_keyboard(tree.buy_gift.buttons, currentInlineState)
	bot.send_photo(chat_id=userId, 
				   photo=item.image, 
				   caption=tree.buy_gift.text.format(item.name, item.price, user['balance'], date, user['name'], user['phone']),
				   reply_markup=keyboard)
def user_buy(message, value):
	userId = message.chat.id
	[toyId, sectionId] = [int(x) for x in value]
	item = items[sectionId][toyId]

	user = users.find_one({'_id': userId})

	# Check if user can buy current item
	if user['balance'] < item.price:
		bot.send_message(userId, tree.user_buy.not_enough)
		list_gifts(message, value)
		return
	# Check if user not reached limit yet for an item
	if user['limit_items'][sectionId][toyId] + 1 > item.limit:
		bot.send_message(userId, tree.user_buy.limit_exceeded)
		list_gifts(message, value)
		return

	new_operation = create_operation(item.name, -item.price)
	update_user(userId, set_args={'balance': user['balance'] - item.price,
								  f'limit_items.{sectionId}.{toyId}': user['limit_items'][sectionId][toyId] + 1},
						push_args={'operations': new_operation})

	confirm_user(message, value)

	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree.user_buy.buttons, currentInlineState)
	bot.send_message(userId, tree.user_buy.text, reply_markup=keyboard)
def confirm_user(message, value):
	userId = message.chat.id
	[toyId, sectionId] = [int(x) for x in value]
	item = items[sectionId][toyId]

	user = users.find_one({'_id': userId})

	currentInlineState = [Keyformat(callbacks=[userId, toyId, sectionId]), 
						  Keyformat(callbacks=[userId, toyId, sectionId])]

	keyboard = create_keyboard(tree.confirmation.buttons, currentInlineState)
	bot.send_photo(chat_id=groupChatId, 
				   photo=item.image,
				   caption=tree.confirmation.text.format(item.tag, user['username'], user['balance'], user['name'], user['phone']), 
				   reply_markup=keyboard,
				   parse_mode='html')
def confirmed(message, value):
	option = value[0]
	[userId, toyId, sectionId] = [int(x) for x in value[1:]]

	item = items[sectionId][toyId]

	user = users.find_one({'_id': userId})
	if option == 'no':
		text = 'Отвергнут ❌'
		bot.send_message(userId, tree.notification.product_warning)

		new_operation = create_operation(tree.operations.back, +item.price)
		update_user(userId, set_args={'balance': user['balance'] + item.price,
									  f'limit_items.{sectionId}.{toyId}': user['limit_items'][sectionId][toyId] - 1},
							push_args={'operations': new_operation})

		user['balance'] = user['balance'] + item.price
	elif option == 'yes':
		text = 'Одобрит ✅'
		bot.send_message(userId, tree.notification.product_success)

	bot.send_photo(chat_id=groupChatId,
				   photo=item.image,
				   caption=tree.notification.client_info.format(item.tag, user['username'], text, user['balance'], user['name'], user['phone']),
				   parse_mode='html')
# <+=============================================================================================+>

# QR MANAGEMENT
# <+=============================================================================================+>
@bot.message_handler(commands=['qr'])
def cashback_photo(message):
	userId = message.chat.id
	user = users.find_one({'_id': userId})

	if not user['registered']:
		bot.send_message(userId, tree.notification.not_registered)
		menu(message)
		return

	update_user(userId, 'cashback_photo_QR')
	bot.send_message(userId, tree.cashback_photo.text)
def cashback_photo_QR(message):
	userId = message.chat.id
	if message.content_type != 'photo':
		update_user(userId, 'cashback_photo_QR')
		bot.send_message(userId, tree.cashback_photo.wrong_format)
		return

	data = get_data_from_qr(message)
	if data == None: return

	currentInlineState = [Keyformat(callbacks=[data.date, data.sum]), 
						  Keyformat(callbacks=[data.date]), 
						  Keyformat(callbacks=[data.date])]
	
	available_cashback = cashback_logic(data.sum, cashback)
	date = get_today().strftime("%d/%m/%Y")

	keyboard = create_keyboard(tree.cashback_photo.buttons, currentInlineState)
	bot.send_message(userId, tree.cashback_photo.result.format(date, data.sum, available_cashback*100, int(data.sum * available_cashback)), reply_markup=keyboard)
def cashback_photo_finish(message, values):
	userId = message.chat.id

	[url, true_money] = values
	true_money = int(true_money)
	money = int(true_money * cashback_logic(true_money, cashback))

	urllib.request.urlopen(URL_ser+'/api/response/'+url)

	user = users.find_one({'_id': userId})

	# FRAUD CHECK SYSTEM: LIMIT ON CASHBACK
	if user['all_balance'] + money > MAX_BALANCE:
		bot.send_message(userId, tree.notification.fraud_detect)
		return

	new_operation = create_operation(tree.operations.photo, true_money, money)

	update_user(userId, set_args={'balance': user['balance'] + money, 
								  'all_balance': user['all_balance'] + money},
						push_args={'operations': new_operation})
	bot.send_message(userId, tree.notification.balance_increase.format(money))
def cashback_photo_cancel(message, values):
	[function_name, url] = values

	urllib.request.urlopen(URL_ser+'/api/cancel/'+url)

	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(function_name)
	method(message)

# <+=============================================================================================+>


# SHARE
# <+=============================================================================================+>
def share(message):
	userId = message.chat.id
	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.share.buttons, currentInlineState)
	bot.send_photo(chat_id=userId,
				   photo=tree.share.image,
				   caption=tree.share.text,
				   reply_markup=keyboard)

def get_nicknames(message):
	userId = message.chat.id
	update_user(userId, 'get_nicknames')

	user = users.find_one({'_id': userId})
	
	try: bot.delete_message(userId, message.message_id)
	except: pass

	if message.contact is not None:
		print(message.contact)
		phone = message.contact.phone_number
		phone = f'+{phone}' if phone[0] != '+' else phone
		
		if not phone in user['friends']:
			if users.find_one({'phone': phone}) == None:
				update_user(userId, set_args={'friends.{}'.format(phone): False})
			else:
				bot.send_message(userId, tree.get_nicknames.user_already_joined.format(phone), parse_mode='html')
		else:
			bot.send_message(userId, tree.get_nicknames.user_is_written.format(phone), parse_mode='html')
	
	user = users.find_one({'_id': userId})

	list_friends = "\n"
	cnt = 0
	print(user['friends'])
	for friend in user['friends']:
		print(friend)
		if not user['friends'][friend]:
			cnt = cnt + 1
			list_friends = list_friends + "{}. {}\n".format(cnt, friend)
	if list_friends == "\n":
		list_friends = ": 0"

	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.get_nicknames.buttons, currentInlineState)
	
	if user['prev_message'] == '#':
		msg = bot.send_photo(chat_id=userId,
							 photo=tree.get_nicknames.image,
							 caption=tree.get_nicknames.text + list_friends,
							 reply_markup=keyboard,
							 parse_mode='html')
		update_user(userId, set_args={'prev_message': msg.message_id})
	else:
		bot.edit_message_caption(chat_id=userId,
								 message_id=user['prev_message'],
								 caption=tree.get_nicknames.text + list_friends,
								 reply_markup=keyboard,
								 parse_mode='html')



# <+=============================================================================================+>


# CONDITIONS
# <+=============================================================================================+>
def conditions(message):
	userId = message.chat.id
	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.conditions.buttons, currentInlineState)
	bot.send_photo(chat_id=userId, 
				   photo=tree.conditions.image, 
				   caption=tree.conditions.text, 
				   reply_markup=keyboard)

# <+=============================================================================================+>


# LIST PARTNERS
# <+=============================================================================================+>
def list_partners(message):
	userId = message.chat.id
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree.list_partners.buttons, currentInlineState)
	bot.send_message(userId, tree.list_partners.text, reply_markup=keyboard)
# <+=============================================================================================+>

# QUESTIONS
# <+=============================================================================================+>
def faq(message):
	userId = message.chat.id
	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.faq.buttons, currentInlineState)
	bot.send_message(userId, tree.faq.text, reply_markup=keyboard, parse_mode='html')

def ask_question(message):
	userId = message.chat.id
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree.ask_question.buttons, currentInlineState)
	bot.send_message(userId, tree.ask_question.text, reply_markup=keyboard)
# <+=============================================================================================+>

# PROFILE/REGISTERATION SYSTEM
# <+=============================================================================================+>
def profile(message): 
	userId = message.chat.id
	user = users.find_one({'_id': userId})
	if not user['registered']:
		register(message)
		return
	date = get_today()
	string_date = date.strftime("%d/%m/%Y")

	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree.profile.buttons, currentInlineState)
	bot.send_message(userId, tree.profile.text.format(user['balance'], string_date, user['name'], user['phone']), reply_markup=keyboard)
def register(message):
	userId = message.chat.id
	update_user(userId, 'process_register_step_get_name')
	bot.send_message(userId, tree.register.choose_name)
# NAME
def process_register_step_get_name(message):
	userId = message.chat.id
	update_user(userId, 'register_last_step_phone', set_args={'name': message.text})

	keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	keyboard.one_time_keyboard = True

	button_phone = KeyboardButton(text="Продолжить", request_contact=True)
	keyboard.add(button_phone)
	bot.send_message(userId, tree.register.get_telephone, reply_markup=keyboard, parse_mode='html')
# PHONE
def register_last_step_phone(message):
	userId = message.chat.id
	if message.contact is not None:
		print(message.contact)
		users.update_one({'_id': userId}, {'$set': {'phone': '+'+message.contact.phone_number}})

		user = users.find_one({'_id': userId})

		date = get_today().strftime("%d/%m/%Y")

		bot.send_message(userId, tree.register.check_info, reply_markup=ReplyKeyboardRemove())
		keyboard = create_keyboard(tree.register.buttons, [Keyformat(), Keyformat()])
		bot.send_message(userId, tree.profile.text.format(user['balance'], date, user['name'], user['phone']), reply_markup=keyboard)
	else:
		keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
		button_phone = KeyboardButton(text="Продолжить", request_contact=True)
		keyboard.add(button_phone)
		bot.send_message(userId, tree.register.get_telephone, reply_markup=keyboard, parse_mode='html')

def register_complete(message):
	userId = message.chat.id
	user = users.find_one({'_id': userId})

	if not user['registered']:
		bot.send_message(userId, tree.register.welcome_casback)
		new_operation = create_operation(tree.operations.register, welcome_cashback_sum)

		update_user(userId, set_args={'balance': user['balance'] + welcome_cashback_sum, 'registered': True},
							push_args={'operations': new_operation})
	
	user = users.find_one({'_id': userId})

	# Adding previous cashback to a registered account
	prev_user_data = users.find_one({'phone': user['phone'], 'not_joined': True})
	if prev_user_data != None:
		bot.send_message(userId, tree.register.previous_cashbacks.format(prev_user_data['balance']))

		# Update balance and add operations
		update_user(userId, set_args={'balance': user['balance'] + prev_user_data['balance']})
		for operation in prev_user_data['operations']:
			update_user(userId, push_args={'operations': operation})

		# Remove not_joined document
		users.delete_one({'phone': user['phone'], 'not_joined': True})

	# Sending cashback to those who written their phone number
	users_to_add_money = users.find({'friends.{}'.format(user['phone']): False})
	for u in users_to_add_money:
		print(u)
		bot.send_message(u['_id'], tree.notification.friend_join.format(user['phone'], friend_money))

		new_operation = create_operation(user['phone'][1:], friend_money)
		update_user(u['_id'], set_args={'balance': u['balance'] + friend_money,
										'friends.{}'.format(user['phone']): True},
								push_args={'operations': new_operation})

	profile(message)
# <+=============================================================================================+>
def calc(query):
	value = -1
	if '?' in query:
		value = re.search(r'\?.+', query)[0][1:].split(',')
		query = re.search(r'^[^\?]+', query)[0]
	return [query, value]

@bot.message_handler(content_types = ['text', 'photo', 'contact'])
def receiver(message):
	userId = message.chat.id
	user = users.find_one({'_id': userId})
	if user['use_function']:
		[query, values] = calc(user['function_name'])

		update_user(userId, '#')

		print(query, values)
		possibles = globals().copy()
		possibles.update(locals())
		method = possibles.get(query)
		
		try:
			if values != -1:
				method(message, values)
			else:
				method(message)
		except Exception as e:
			print('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
			return
	elif message.content_type == "photo":
		cashback_photo_QR(message)
	else:
		bot.send_message(userId, TEMPLATE_MESSAGE)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	bot.delete_message(call.message.chat.id, call.message.message_id)

	userId = call.message.chat.id
	[query, value] = calc(call.data)

	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(query)
	
	try:
		if value == -1:
			method(call.message)
		else:
			method(call.message, value)
	except Exception as e:
		print('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
		return

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))