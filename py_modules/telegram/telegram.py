# TODO:
# 1. function "get" change name also add deep key retrivale
# 2. If possible try removing yellow squiggle lines in imports
# 3. Create credential file where all testing variables will be stored for bot testing
# 4. better method/variable naming  
# 5. Update limit_items for all users when items update
# 6. Clear extract every month

from flask import current_app as app
from py_modules.mongo import users

import re
import os
import json
import telebot
from telebot.types import ReplyKeyboardRemove
import urllib.request
import traceback # Error handiling

from flask import request
from PIL import Image

def recurseToGetValue(jsonTree, pathToKey):
	key = pathToKey.pop(0)
	if len(pathToKey): # if there are more levels to go down
		return recurseToGetValue(jsonTree[key], pathToKey) # recurse
	return jsonTree[key]

def getValueInJson(jsonTree, pathToKeyString): # double entery intentional
    pathToKey = pathToKeyString.split('.')
    return recurseToGetValue(jsonTree, pathToKey)

def get(*args):
	path = './hidden/settings.json'
	jsonFile = open(path, "r", encoding='utf-8')
	data = json.load(jsonFile)
	jsonFile.close()

	return [getValueInJson(data, k) for k in list(args)]

bot = telebot.TeleBot(get("TOKEN")[0])
URL_ser = 'https://test-potato-cashback.herokuapp.com'
URL_bot = URL_ser + '/bot/'
URL_image = './py_modules/telegram/images/'

from py_modules.telegram.classes import *
from py_modules.telegram.functions import *

@app.route('/bot/'+get("TOKEN")[0], methods=['POST'])
def getMessage():
	json_string = request.get_data().decode('utf-8')
	update = telebot.types.Update.de_json(json_string)
	
	# TECHNICAL STOP FOR DEBUGS AND CODE FIXES
	if techincal_stop_check(update):
		return "Bug fixes", 200
	
	bot.process_new_updates([update])

	return "!", 200

@app.route('/send_data/<phone>/<sum>')
def process_cashback(phone, sum):
	sum = int(sum)
	[operations, notifications] = get("tree.operations", "tree.notifications")
	money = int(sum * cashback_logic(sum))
	
	user = find_user({'phone': phone})
	if users.find_one({'phone': phone}) is None:
		user.phone = phone

		users.insert_one(user.__dict__)

	user.clear_data_every_month()
	
	if user.fraud_check(money):
		return 'bad'
	
	new_operation = user.create_operation(operations['photo'], sum, money)
	user.push_operation(new_operation)
	user.update_balance(money)
	
	try: bot.send_message(user._id, notifications['balance_increase'].format(money))
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
	try:
		for user in users.find({}):
			if user['onTelegram'] == False:
				continue
			users.update_one({'_id': user['_id']}, {'$set': {'polls': {}}})
	except:
		print(traceback.format_exc())

	print("COPIED")


@bot.message_handler(commands=['send_poll'])
def sendPolls(message):
	for user in users.find({}):
		user = User(user)
		poll = bot.send_poll(chat_id=user._id,
						question="Are you a robot?",
						options=["Yes", "No"],
						is_anonymous=False)
		user.set_new_poll(poll.poll)
	print("SENT POLL")

@bot.message_handler(commands=['start'])
def menu(message):
	try:
		print(message)
		[menu, show_qr] = get("tree.menu", "show_qr")

		user = find_user({'_id': message.chat.id})

		if not user.onTelegram:
			user._id = message.chat.id
			user.username = message.chat.username
			user.onTelegram = True

			users.insert_one(user.__dict__)

		user.clear_data_every_month()
		user.clear_next_step_handler()

		user.prev_message = '#'
		user.overwrite_data()

		currentInlineState = [Keyformat(), 
							  Keyformat(), 
							  Keyformat(hideButton=(not show_qr)), 
							  Keyformat()]
		keyboard = create_keyboard(menu['buttons'], currentInlineState)
		bot.send_message(user._id, menu['text'], reply_markup=keyboard)
	except:
		print(traceback.format_exc())


@bot.message_handler(commands=['extract'])
def extract(message):
	try:
		[extract, notifications] = get("tree.extract", "tree.notifications")
		user = find_user(message.chat.id)

		if not user.is_registered():
			bot.send_message(user._id, notifications['not_registered'])
			menu(message)
			return

		operations = sorted(user.operations, key=lambda k: k['date']+'#'+k['time'])
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

		currentInlineState = [Keyformat()]
		keyboard = create_keyboard(extract['buttons'], currentInlineState)
		bot.send_message(user._id, msg, reply_markup=keyboard, parse_mode='html')
	except:
		print(traceback.format_exc())


def sections(message):
	[sections] = get("tree.sections")

	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(sections['buttons'], currentInlineState)
	bot.send_message(message.chat.id, sections['text'], reply_markup=keyboard)

def display_items(message, sectionName, itemId):
	[display_items, items] = get("tree.display_items", "items")

	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	currentInlineState = [
		Keyformat(texts=[item['price']], callbacks=[sectionName, itemId]),
		Keyformat(callbacks=[sectionName, (itemId if itemId > 0 else len(items[sectionName])) - 1]),
		Keyformat(callbacks=[sectionName, itemId]),
		Keyformat(callbacks=[sectionName, itemId+1 if itemId < len(items[sectionName])-1 else 0]),
		Keyformat(texts=[itemId + 1, len(items[sectionName])], callbacks=[sectionName, itemId]),
		Keyformat()]

	keyboard = create_keyboard(display_items['buttons'], currentInlineState)
	bot.send_photo(chat_id=message.chat.id, 
				   photo=Image.open(URL_image + item['image']), 
				   reply_markup=keyboard)

def item_info(message, sectionName, itemId):
	[item_info, items, notifications] = get("tree.item_info", "items", "tree.notifications")

	user = find_user({'_id': message.chat.id})

	if not user.is_registered():
		bot.send_message(user._id, notifications['not_registered'])
		menu(message)
		return

	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	date = get_today().strftime("%d/%m/%Y")

	currentInlineState = [
		Keyformat(callbacks=[sectionName, itemId]), 
		Keyformat(callbacks=[sectionName])]

	keyboard = create_keyboard(item_info['buttons'], currentInlineState)
	bot.send_photo(chat_id=user._id, 
				   photo=Image.open(URL_image + item['image']), 
				   caption=item_info['text'].format(item['name'], item['price'], user.balance, date, user.name, user.phone),
				   reply_markup=keyboard)

def buy_item(message, sectionName, itemId):
	[buy_item, items] = get("tree.buy_item", "items")
	
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	user = find_user({'_id': message.chat.id})
	user_limit_on_item = user.limit_items[sectionName][itemTag]

	# Check if user can buy current item
	if user.balance < item['price']:
		bot.send_message(user._id, buy_item['not_enough'])
		display_items(message, sectionName, itemId)
		return
	# Check if user not reached limit yet for an item
	if user_limit_on_item + 1 > item['limit']:
		bot.send_message(user._id, buy_item['limit_exceeded'])
		display_items(message, sectionName, itemId)
		return

	# Bought an item
	new_operation = user.create_operation(item['name'], -item['price'])
	user.update_balance(-item['price']) 
	user.set_value(f'limit_items.{sectionName}.{itemTag}', user_limit_on_item + 1)
	user.push_operation(new_operation)

	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(buy_item['buttons'], currentInlineState)
	bot.send_message(user._id, buy_item['text'], reply_markup=keyboard)

	confirm_purchase(message, sectionName, itemId)

def confirm_purchase(message, sectionName, itemId):
	[confirmation, items, groupChatId] = get("tree.confirmation", "items", "groupChatId")
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	user = find_user({'_id': message.chat.id})

	currentInlineState = [Keyformat(callbacks=[user._id, sectionName, itemId]), 
						  Keyformat(callbacks=[user._id, sectionName, itemId])]

	keyboard = create_keyboard(confirmation['buttons'], currentInlineState)
	bot.send_photo(chat_id=groupChatId, 
				   photo=Image.open(URL_image + item['image']),
				   caption=confirmation['text'].format(itemTag, user.username, user.balance, user.name, user.phone), 
				   reply_markup=keyboard,
				   parse_mode='html')

def purchase_status(message, status, userId, sectionName, itemId):
	[notifications, operations, items, groupChatId] = get("tree.notifications", "tree.operations", "items", "groupChatId")
	itemTag = list(items[sectionName])[itemId]

	item = items[sectionName][itemTag]

	user = find_user({'_id': userId})
	if status == 'Отвергнут❌':
		bot.send_message(user._id, notifications['product_warning'])

		new_operation = user.create_operation(operations['back'], +item['price'])
		user_limit_on_item = user.limit_items[sectionName][itemTag]
		user.update_balance(+item['price'])
		user.set_value(f'limit_items.{sectionName}.{itemTag}', user_limit_on_item - 1)
		user.push_operation(new_operation)
	elif status == 'Одобрит✅':
		bot.send_message(user._id, notifications['product_success'])

	bot.send_photo(chat_id=groupChatId,
				   photo=Image.open(URL_image + item['image']),
				   caption=notifications['client_info'].format(itemTag, user.username, status, user.balance, user.name, user.phone),
				   parse_mode='html')


@bot.message_handler(commands=['qr'])
def start_qr(message):
	[qr, notifications, show_qr] = get("tree.qr", "tree.notifications", "show_qr")
	if not show_qr:
		receiver(message)
		return 

	user = find_user({'_id': message.chat.id})

	if not user.is_registered():
		bot.send_message(user._id, notifications['not_registered'])
		menu(message)
		return

	update_user(user._id, 'get_qr')
	bot.send_message(user._id, qr['text'])

def get_qr(message):
	[qr] = get("tree.qr")
	
	user = find_user({'_id': message.chat.id})

	if message.content_type != 'photo':
		user.next_step_handler('get_qr')
		bot.send_message(user._id, qr['wrong_format'])
		return

	data = get_data_from_qr(message.photo[-1])
	if data == "not found":
		user.next_step_handler('get_qr')
		bot.send_message(user._id, qr['qr_not_found'])
		return data
	elif data == "not ok":
		bot.send_message(user._id, qr['wrong_qr'])
		menu(message)
		return data

	currentInlineState = [Keyformat(callbacks=[data['date'], data['sum']]), 
						  Keyformat(callbacks=[data['date']]), 
						  Keyformat(callbacks=[data['date']])]
	
	available_cashback = cashback_logic(data['sum'])
	date = get_today().strftime("%d/%m/%Y")

	keyboard = create_keyboard(qr['buttons'], currentInlineState)
	bot.send_message(user._id, qr['result'].format(date, data['sum'], available_cashback*100, int(data['sum'] * available_cashback)), reply_markup=keyboard)

def qr_finish(message, url, sum):
	[notifications, operations] = get("tree.notifications", "tree.operations")
	url = str(url)

	cashback_sum = int(sum * cashback_logic(sum))

	urllib.request.urlopen(URL_ser+'/api/response/'+url)

	user = find_user({'_id': message.chat.id})

	if user.fraud_check(cashback_sum): 
		bot.send_message(user._id, notifications['fraud_detect'])
		urllib.request.urlopen(URL_ser+'/api/cancel/'+url)
		menu(message)
		return

	new_operation = user.create_operation(operations['photo'], sum, cashback_sum)
	user.update_balance(+cashback_sum)
	user.push_operation(new_operation)

	bot.send_message(user._id, notifications['balance_increase'].format(cashback_sum))

def qr_cancel(message, method_name, url):
	url = str(url)
	urllib.request.urlopen(URL_ser+'/api/cancel/'+url)

	run_method_by_name(method_name, message)


def share_with_friends_info(message):
	[share_with_friends, friend_money] = get("tree.share_with_friends", "friend_money")

	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(share_with_friends['buttons'], currentInlineState)
	bot.send_photo(chat_id=message.chat.id,
				   photo=Image.open(URL_image + share_with_friends['image']),
				   caption=share_with_friends['text'].format(friend_money),
				   reply_markup=keyboard)

def get_contacts(message):
	[get_contacts] = get("tree.share_with_friends.get_contacts")

	user = find_user({'_id': message.chat.id})
	user.next_step_handler('get_contacts')
	
	try: bot.delete_message(user._id, message.message_id)
	except: pass

	if message.contact is not None:
		user.add_friend_contact(message.contact)

	friends = user.friend_list_stringify()
	if friends != ": 0": friends = '\n' + friends

	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(get_contacts['buttons'], currentInlineState)
	
	if user.prev_message == '#':
		msg = bot.send_photo(chat_id=user._id,
							 photo=Image.open(URL_image + get_contacts['image']),
							 caption=get_contacts['text'] + friends,
							 reply_markup=keyboard,
							 parse_mode='html')
		user.set_value('prev_message', msg.message_id)
	else:
		bot.edit_message_caption(chat_id=user._id,
								 message_id=user.prev_message,
								 caption=get_contacts['text'] + friends,
								 reply_markup=keyboard,
								 parse_mode='html')


def conditions(message):
	[conditions] = get("tree.conditions")
	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(conditions['buttons'], currentInlineState)
	bot.send_photo(chat_id=message.chat.id, 
				   photo=Image.open(URL_image + conditions['image']), 
				   caption=conditions['text'], 
				   reply_markup=keyboard)

def display_partners(message):
	[display_partners] = get("tree.display_partners")
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(display_partners['buttons'], currentInlineState)
	bot.send_message(message.chat.id, display_partners['text'], reply_markup=keyboard)


def services_rules(message):
	[services_rules] = get("tree.services_rules")
	currentInlineState = [Keyformat(), Keyformat()]
	keyboard = create_keyboard(services_rules['buttons'], currentInlineState)
	bot.send_message(message.chat.id, services_rules['text'], reply_markup=keyboard, parse_mode='html')

def ask_question(message):
	[ask_question] = get("tree.ask_question")
	currentInlineState = [Keyformat()]
	keyboard = create_keyboard(ask_question['buttons'], currentInlineState)
	bot.send_message(message.chat.id, ask_question['text'], reply_markup=keyboard)


def profile(message): 
	[profile] = get("tree.profile")
	user = find_user({'_id': message.chat.id})

	# Start registration process
	if not user.is_registered():
		register(message)
		return

	date = get_today().strftime("%d/%m/%Y")
	currentInlineState = [Keyformat(), Keyformat(), Keyformat(), Keyformat()]
	keyboard = create_keyboard(profile['buttons'], currentInlineState)
	bot.send_message(user._id, profile['text'].format(user.balance, date, user.name, user.phone), reply_markup=keyboard)

def register(message):
	[register] = get("tree.register")
	user = find_user({'_id': message.chat.id})

	user.next_step_handler('enter_name')
	bot.send_message(user._id, register['enter_name'])

def enter_name(message):
	[register] = get("tree.register")
	user = find_user({'_id': message.chat.id})

	user.set_name(message.text)
	user.next_step_handler('enter_contact')

	keyboard = create_reply_keyboard(register['reply_buttons'])
	bot.send_message(user._id, register['enter_contact'], reply_markup=keyboard, parse_mode='html')

def enter_contact(message):
	[register, profile] = get("tree.register", "tree.profile")
	user = find_user({'_id': message.chat.id})
	if message.contact is not None:
		phone = set_phone_template(message.contact.phone_number)

		user.set_phone(phone)

		date = get_today().strftime("%d/%m/%Y")

		bot.send_message(user._id, register['check_info'], reply_markup=ReplyKeyboardRemove())
		keyboard = create_keyboard(register['buttons'], [Keyformat(), Keyformat()])
		bot.send_message(user._id, profile['text'].format(user.balance, date, user.name, user.phone), reply_markup=keyboard)
	else:
		user.next_step_handler('enter_contact')
		keyboard = create_reply_keyboard(register['reply_buttons'])
		bot.send_message(user._id, register['enter_contact'], reply_markup=keyboard, parse_mode='html')

def register_completed(message):
	user = find_user({'_id': message.chat.id})

	if not user.is_registered():
		user.on_first_registery()

	user.add_previous_cashback_from_phone()
	user.add_cashback_to_their_friends()

	profile(message)

def run_method_by_name(name, *args):
	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(name)
	try:
		method(*args)
	except:
		print(traceback.format_exc())
	return

@bot.poll_answer_handler()
def receivePollAnswer(poll):
	try:
		user = find_user({'_id': poll.user.id})
		user.update_poll_answer(poll.poll_id, poll.options_ids[0]) #One option per poll
	except:
		print(traceback.format_exc())

@bot.message_handler(content_types = ['text', 'photo', 'contact'])
def receiver(message):
	[TEMPLATE_MESSAGE, show_qr] = get("TEMPLATE_MESSAGE", "show_qr")
	user = find_user({'_id': message.chat.id})

	if user.use_function:
		[method_name, args] = calc(user.function_name)
		args.insert(0, message)
		user.clear_next_step_handler()
		run_method_by_name(method_name, *args)
	elif message.content_type == "photo" and show_qr == True:
		data = get_qr(message)
		if data == "not found" and data == "not ok":
			bot.send_message(user._id, TEMPLATE_MESSAGE)
	else:
		bot.send_message(user._id, TEMPLATE_MESSAGE)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	message = call.message
	bot.delete_message(message.chat.id, message.message_id)

	[method_name, args] = calc(call.data)
	args.insert(0, message)
	run_method_by_name(method_name, *args)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
