from flask import current_app as app
from py_modules.mongo import users

import re
import os
import json
import telebot
from telebot.types import ReplyKeyboardRemove
import urllib.request

from flask import request
from PIL import Image
from py_modules.telegram.classes import *

def get(*args):
	path = './hidden/settings.json'
	jsonFile = open(path, "r", encoding='utf-8')
	data = json.load(jsonFile)
	jsonFile.close()
	return [data[k] for k in list(args)]

bot = telebot.TeleBot(get("TOKEN")[0])
URL_ser = 'https://test-potato-cashback.herokuapp.com'
URL_bot = URL_ser + '/bot/'
URL_image = './py_modules/telegram/images/'

from py_modules.telegram.functions import *

@app.route('/bot/'+get("TOKEN")[0], methods=['POST'])
def getMessage():
	try:
		json_string = request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		
		# TECHNICAL STOP FOR DEBUGS AND CODE FIXES
		if techincal_stop_check(update):
			return "Bug fixes", 200
		
		bot.process_new_updates([update])
	except Exception as e:
		print('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
		return
	return "!", 200

@app.route('/send_data/<phone>/<sum>')
def process_cashback(phone, sum):
	sum = int(sum)
	[tree, cashback] = get("tree", "cashback")
	money = int(sum * cashback_logic(sum, cashback))
	month = get_today().strftime('%m')

	user = users.find_one({'phone': phone})
	# Check if unregistered
	if user is None:
		users.insert_one({
			'phone': phone,
			'balance': 0,
			
			'all_balance': 0,
			'operations': [],
			'not_joined': True,
			'month': month
		})
		user = users.find_one({'phone': phone})

	update_all_balance(user, month)

	user = users.find_one({'phone': phone})
	
	if fraud_check(user, money): return 'bad'
		
	new_operation = create_operation(tree['operations']['photo'], sum, money)
	users.update_one({'phone': phone}, {'$set': {'balance': user['balance'] + money,
												 'all_balance': user['all_balance'] + money},
										'$push': {'operations': new_operation}})	

	try: bot.send_message(user['_id'], tree['notification']['balance_increase'].format(money))
	except: pass

	return 'nice'

@app.route('/bot/')
def webhook():
	bot.remove_webhook()
	[TOKEN] = get("TOKEN")
	bot.set_webhook(url = URL_bot + TOKEN)
	return '!', 200

@bot.message_handler(commands=['nurmukhambetov'])
def check_balances(message):
	userId = message.chat.id
	user = users.find_one({'_id': userId})
	if not 'admin' in user:
		return
	
	[items] = get("items")
	# data = users.find({})
	ans = {sectionName:{itemTag:0 for itemTag in items[sectionName]} for sectionName in items}
	print(ans)
	# users.update_one({}, {'limit_items': ans})

	# for user in data:
	# 	balance = user['balance']
	# 	operations = user['operations']

	# 	sum = 0
	# 	for operation in operations:
	# 		sum += operation['cashback'] if operation['cashback'] != -1 else operation['sum']
		
	# 	if sum == balance:
	# 		ans = ans + user['name'] + ' ' + user['phone'] + ": OK\n"
	# 	else:
	# 		ans = ans + user['name'] + ' ' + user['phone'] + ": " + str(balance) + " != " + str(sum) + "\n"
	# bot.send_message(userId, ans)

@bot.message_handler(commands=['start'])
def menu(message):
	print(message)
	userId = message.chat.id
	month = get_today().strftime("%m")
	[tree, items] = get("tree", "items")

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
			'limit_items': {sectionName:{itemTag:0 for itemTag in items[sectionName]} for sectionName in items},

			'function_name': '#',
			'use_function': False,
			'prev_message': '#',
			'month': month,

			'operations': [],
		})
	else:
		update_all_balance(user, month)
		update_user(userId, function_name='#', set_args={'prev_message': '#'})

	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree['menu']['buttons'], currentInlineState)
	bot.send_message(userId, tree['menu']['text'], reply_markup=keyboard)

# EXTRACT LIST SYSTEM
# <+=============================================================================================+>
@bot.message_handler(commands=['extract'])
def extract(message):
	userId = message.chat.id
	user = users.find_one({'_id': userId})

	if not user['registered']:
		register(message)
		return

	operations = sorted(user['operations'], key=lambda k: k['date']+'#'+k['time'])
	queries = [{'date': re.sub(r'2021','21', o['date']), 
				'details': o['details'],
				'value': sign(o['cashback'] if o['cashback'] != -1 else o['sum'])} for o in operations]
	mx_lens = {
		'date': max(len(q['date']) for q in queries),
		'value': max(len(q['value']) for q in queries),
		'details': max(len(q['details']) for q in queries)
	}

	msg = 'ДАТА'.center(mx_lens['date'] + 1)+'|'+'СУММА'.center(mx_lens['value'] + 3)+'|'+'ОПЕРАЦИИ'.center(mx_lens['details'] + 1)+'\n'
	sum_value = 0
	for q in queries:
		spaces = (mx_lens['value'] - len(q['value']))*' '
		new_msg = '{} | {}{}₸ | {}\n'.format(q['date'], spaces, q['value'], q['details'])
		msg = msg + new_msg
		sum_value = sum_value + int(q['value'])
	msg = msg + '\nОстаток: {}₸'.format(sum_value)

	msg = '<code>'+msg+'</code>'

	[tree] = get("tree")
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree['extract']['buttons'], currentInlineState)
	bot.send_message(userId, msg, reply_markup=keyboard, parse_mode='html')
# <+=============================================================================================+>


# GIFT MANANGMENT
# <+=============================================================================================+>
def sections(message):
	userId = message.chat.id
	[tree] = get("tree")

	currentInlineState = [Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree['sections']['buttons'], currentInlineState)
	bot.send_message(userId, tree['sections']['text'], reply_markup=keyboard)
def display_items(message, value):
	userId = message.chat.id
	[tree, items] = get("tree", "items")

	[sectionName, itemId] = value
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	currentInlineState = [
		Keyformat(texts=[item['price']], callbacks=[sectionName, itemId]),
		Keyformat(callbacks=[sectionName, (itemId if itemId > 0 else len(items[sectionName])) - 1]),
		Keyformat(callbacks=[sectionName, itemId]),
		Keyformat(callbacks=[sectionName, itemId+1 if itemId < len(items[sectionName])-1 else 0]),
		Keyformat(texts=[itemId + 1, len(items[sectionName])], callbacks=[sectionName, itemId]),
		Keyformat()]

	keyboard = create_keyboard(tree['display_items']['buttons'], currentInlineState)
	bot.send_photo(chat_id=userId, 
				   photo=Image.open(URL_image + item['image']), 
				   reply_markup=keyboard)
def item_info(message, value):
	userId = message.chat.id
	[tree, items] = get("tree", "items")
	user = users.find_one({'_id': userId})

	if not user['registered']:
		bot.send_message(userId, tree['notification']['not_registered'])
		menu(message)
		return

	[sectionName, itemId] = value
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	date = get_today().strftime("%d/%m/%Y")

	currentInlineState = [
		Keyformat(callbacks=[sectionName, itemId]), 
		Keyformat(callbacks=[sectionName])]

	keyboard = create_keyboard(tree['item_info']['buttons'], currentInlineState)
	bot.send_photo(chat_id=userId, 
				   photo=Image.open(URL_image + item['image']), 
				   caption=tree['item_info']['text'].format(item['name'], item['price'], user['balance'], date, user['name'], user['phone']),
				   reply_markup=keyboard)
def buy_item(message, value):
	userId = message.chat.id
	[tree, items] = get("tree", "items")
	
	[sectionName, itemId] = value
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	user = users.find_one({'_id': userId})
	user_limit_on_item = user['limit_items'][sectionName][itemTag]

	# Check if user can buy current item
	if user['balance'] < item['price']:
		bot.send_message(userId, tree['buy_item']['not_enough'])
		display_items(message, value)
		return
	# Check if user not reached limit yet for an item
	if user_limit_on_item + 1 > item['limit']:
		bot.send_message(userId, tree['buy_item']['limit_exceeded'])
		display_items(message, value)
		return

	new_operation = create_operation(item['name'], -item['price'])
	update_user(userId, set_args={'balance': user['balance'] - item['price'],
								  f'limit_items.{sectionName}.{itemTag}': user_limit_on_item + 1},
						push_args={'operations': new_operation})

	confirm_purchase(message, value)

	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree['buy_item']['buttons'], currentInlineState)
	bot.send_message(userId, tree['buy_item']['text'], reply_markup=keyboard)
def confirm_purchase(message, value):
	userId = message.chat.id
	[tree, items, groupChatId] = get("tree", "items", "groupChatId")
	[sectionName, itemId] = value
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	user = users.find_one({'_id': userId})

	currentInlineState = [Keyformat(callbacks=[userId, sectionName, itemId]), 
						  Keyformat(callbacks=[userId, sectionName, itemId])]

	keyboard = create_keyboard(tree['confirmation']['buttons'], currentInlineState)
	bot.send_photo(chat_id=groupChatId, 
				   photo=Image.open(URL_image + item['image']),
				   caption=tree['confirmation']['text'].format(itemTag, user['username'], user['balance'], user['name'], user['phone']), 
				   reply_markup=keyboard,
				   parse_mode='html')
def purchase_status(message, value):
	[tree, items, groupChatId] = get("tree", "items", "groupChatId")
	[status, userId, sectionName, itemId] = value
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	user = users.find_one({'_id': userId})
	if status == 'Отвергнут❌':
		bot.send_message(userId, tree['notification']['product_warning'])

		new_operation = create_operation(tree['operations']['back'], +item['price'])
		update_user(userId, set_args={'balance': user['balance'] + item['price'],
									  f'limit_items.{sectionName}.{itemTag}': user['limit_items'][sectionName][itemTag] - 1},
							push_args={'operations': new_operation})

		user['balance'] = user['balance'] + item['price']
	elif status == 'Одобрит✅':
		bot.send_message(userId, tree['notification']['product_success'])

	bot.send_photo(chat_id=groupChatId,
				   photo=Image.open(URL_image + item['image']),
				   caption=tree['notification']['client_info'].format(itemTag, user['username'], status, user['balance'], user['name'], user['phone']),
				   parse_mode='html')
# <+=============================================================================================+>

# QR MANAGEMENT
# <+=============================================================================================+>
@bot.message_handler(commands=['qr'])
def cashback_photo(message):
	userId = message.chat.id
	[tree] = get("tree")
	user = users.find_one({'_id': userId})

	if not user['registered']:
		bot.send_message(userId, tree['notification']['not_registered'])
		menu(message)
		return

	update_user(userId, 'cashback_photo_QR')
	bot.send_message(userId, tree['cashback_photo']['text'])
def cashback_photo_QR(message):
	userId = message.chat.id
	[tree, cashback] = get("tree", "cashback")
	if message.content_type != 'photo':
		update_user(userId, 'cashback_photo_QR')
		bot.send_message(userId, tree['cashback_photo']['wrong_format'])
		return

	data = get_data_from_qr(message)
	if data == "not found":
		update_user(userId, 'cashback_photo_QR')
		bot.send_message(userId, tree['cashback_photo']['qr_not_found'])
		return
	elif data == "not ok":
		bot.send_message(userId, tree['cashback_photo']['wrong_qr'])
		menu(message)
		return

	currentInlineState = [Keyformat(callbacks=[data.date, data.sum]), 
						  Keyformat(callbacks=[data.date]), 
						  Keyformat(callbacks=[data.date])]
	
	available_cashback = cashback_logic(data.sum, cashback)
	date = get_today().strftime("%d/%m/%Y")

	keyboard = create_keyboard(tree['cashback_photo']['buttons'], currentInlineState)
	bot.send_message(userId, tree['cashback_photo']['result'].format(date, data.sum, available_cashback*100, int(data.sum * available_cashback)), reply_markup=keyboard)
def cashback_photo_finish(message, values):
	userId = message.chat.id
	[tree, cashback] = get("tree", "cashback")
	[url, true_money] = values
	true_money = int(true_money)
	money = int(true_money * cashback_logic(true_money, cashback))

	urllib.request.urlopen(URL_ser+'/api/response/'+url)

	user = users.find_one({'_id': userId})

	if fraud_check(user, money): 
		urllib.request.urlopen(URL_ser+'/api/cancel/'+url)
		menu(message)
		return

	new_operation = create_operation(tree['operations']['photo'], true_money, money)

	update_user(userId, set_args={'balance': user['balance'] + money, 
								  'all_balance': user['all_balance'] + money},
						push_args={'operations': new_operation})
	bot.send_message(userId, tree['notification']['balance_increase'].format(money))
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
	[tree, friend_money] = get("tree", "friend_money")

	userId = message.chat.id
	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree['share']['buttons'], currentInlineState)
	bot.send_photo(chat_id=userId,
				   photo=Image.open(URL_image + tree['share']['image']),
				   caption=tree['share']['text'].format(friend_money),
				   reply_markup=keyboard)

def get_nicknames(message):
	userId = message.chat.id
	[tree] = get("tree")

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
				bot.send_message(userId, tree['get_nicknames']['user_already_joined'].format(phone), parse_mode='html')
		else:
			bot.send_message(userId, tree['get_nicknames']['user_is_written'].format(phone), parse_mode='html')
	
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
	keyboard = create_keyboard(tree['get_nicknames']['buttons'], currentInlineState)
	
	if user['prev_message'] == '#':
		msg = bot.send_photo(chat_id=userId,
							 photo=Image.open(URL_image + tree['get_nicknames']['image']),
							 caption=tree['get_nicknames']['text'] + list_friends,
							 reply_markup=keyboard,
							 parse_mode='html')
		update_user(userId, set_args={'prev_message': msg.message_id})
	else:
		bot.edit_message_caption(chat_id=userId,
								 message_id=user['prev_message'],
								 caption=tree['get_nicknames']['text'] + list_friends,
								 reply_markup=keyboard,
								 parse_mode='html')
# <+=============================================================================================+>


# CONDITIONS
# <+=============================================================================================+>
def conditions(message):
	userId = message.chat.id
	[tree] = get("tree")
	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree['conditions']['buttons'], currentInlineState)
	bot.send_photo(chat_id=userId, 
				   photo=Image.open(URL_image + tree['conditions']['image']), 
				   caption=tree['conditions']['text'], 
				   reply_markup=keyboard)

# <+=============================================================================================+>


# LIST PARTNERS
# <+=============================================================================================+>
def list_partners(message):
	userId = message.chat.id
	[tree] = get("tree")
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree['list_partners']['buttons'], currentInlineState)
	bot.send_message(userId, tree['list_partners']['text'], reply_markup=keyboard)
# <+=============================================================================================+>

# QUESTIONS
# <+=============================================================================================+>
def faq(message):
	userId = message.chat.id
	[tree] = get("tree")
	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree['faq']['buttons'], currentInlineState)
	bot.send_message(userId, tree['faq']['text'], reply_markup=keyboard, parse_mode='html')

def ask_question(message):
	userId = message.chat.id
	[tree] = get("tree")
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(tree['ask_question']['buttons'], currentInlineState)
	bot.send_message(userId, tree['ask_question']['text'], reply_markup=keyboard)
# <+=============================================================================================+>

# PROFILE/REGISTERATION SYSTEM
# <+=============================================================================================+>
def profile(message): 
	userId = message.chat.id
	[tree] = get("tree")
	user = users.find_one({'_id': userId})
	if not user['registered']:
		register(message)
		return
	date = get_today()
	string_date = date.strftime("%d/%m/%Y")

	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(tree['profile']['buttons'], currentInlineState)
	bot.send_message(userId, tree['profile']['text'].format(user['balance'], string_date, user['name'], user['phone']), reply_markup=keyboard)
def register(message):
	userId = message.chat.id
	[tree] = get("tree")
	update_user(userId, 'process_register_step_get_name')
	bot.send_message(userId, tree['register']['choose_name'])
# NAME
def process_register_step_get_name(message):
	userId = message.chat.id
	[tree] = get("tree")
	update_user(userId, 'register_last_step_phone', set_args={'name': message.text})

	keyboard = create_reply_keyboard(tree['register']['reply_buttons'])
	bot.send_message(userId, tree['register']['get_telephone'], reply_markup=keyboard, parse_mode='html')
# PHONE
def register_last_step_phone(message):
	userId = message.chat.id
	[tree] = get("tree")
	if message.contact is not None:
		phone = message.contact.phone_number
		phone = f'+{phone}' if phone[0] != '+' else phone

		users.update_one({'_id': userId}, {'$set': {'phone': phone}})

		user = users.find_one({'_id': userId})

		date = get_today().strftime("%d/%m/%Y")

		bot.send_message(userId, tree['register']['check_info'], reply_markup=ReplyKeyboardRemove())

		keyboard = create_keyboard(tree['register']['buttons'], [Keyformat(), Keyformat()])
		bot.send_message(userId, tree['profile']['text'].format(user['balance'], date, user['name'], user['phone']), reply_markup=keyboard)
	else:
		keyboard = create_reply_keyboard(tree['register']['reply_buttons'])
		bot.send_message(userId, tree['register']['get_telephone'], reply_markup=keyboard, parse_mode='html')

# COMPLETE
def register_complete(message):
	userId = message.chat.id
	[tree, welcome_cashback_sum, friend_money] = get("tree", "welcome_cashback_sum", "friend_money")
	user = users.find_one({'_id': userId})

	if not user['registered']:
		bot.send_message(userId, tree['register']['welcome_casback'].format(welcome_cashback_sum))
		new_operation = create_operation(tree['operations']['register'], welcome_cashback_sum)

		update_user(userId, set_args={'balance': user['balance'] + welcome_cashback_sum, 'registered': True},
							push_args={'operations': new_operation})
	
	user = users.find_one({'_id': userId})

	# Adding previous cashback to a registered account
	prev_user_data = users.find_one({'phone': user['phone'], 'not_joined': True})
	if prev_user_data != None:
		bot.send_message(userId, tree['register']['previous_cashbacks'].format(prev_user_data['balance']))

		# Update balance and add operations
		update_user(userId, set_args={'balance': user['balance'] + prev_user_data['balance']})
		for operation in prev_user_data['operations']:
			update_user(userId, push_args={'operations': operation})

		users.delete_one({'phone': user['phone'], 'not_joined': True})

	# Sending cashback to those who written their phone number
	users_to_add_money = users.find({'friends.{}'.format(user['phone']): False})
	for u in users_to_add_money:
		bot.send_message(u['_id'], tree['notification']['friend_join'].format(user['phone'], friend_money))

		new_operation = create_operation(user['phone'][1:], friend_money)
		update_user(u['_id'], set_args={'balance': u['balance'] + friend_money,
										'friends.{}'.format(user['phone']): True},
								push_args={'operations': new_operation})

	profile(message)
# <+=============================================================================================+>

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
		[TEMPLATE_MESSAGE] = get("TEMPLATE_MESSAGE")
		data = cashback_photo_QR(message)
		if data == "not found" or data == "not ok":
			bot.send_message(userId, TEMPLATE_MESSAGE)
	else:
		[TEMPLATE_MESSAGE] = get("TEMPLATE_MESSAGE")
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