from config import username, password

from flask import current_app as app
from flask import send_from_directory, Response, request

from py_modules.telegram.telegram import bot
from py_modules.telegram.functions import find_user, convertBase64ToImage
from py_modules.mongo import users
import json
import traceback
import base64

import requests 
import os

from io import BytesIO

@app.route('/admin/<u>/<p>/<path:path>')
def loggingin(u, p, path):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	if(not "." in path):
		return send_from_directory('./hidden/admin/', path + '/index.html')
	else:
		return send_from_directory('./hidden/admin/', path)


@app.route('/admin/<u>/<p>/clean')
def clean(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	try:
		user_0 = users.delete_one({'phone': '+0'})
		user_1 = users.delete_one({'phone': '+1'})
		return 'cleaned'
	except:	
		return 'server error'

@app.route('/admin/<u>/<p>/saveJSON', methods=['POST'])
def saveJson(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	data = json.loads(request.data)
	path = './hidden/settings.json'

	updateJsonFile(path, data)

	return 'saved'

@app.route('/admin/<u>/<p>/getJSON')
def getJson(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	try:
		path = './hidden/settings.json'
		jsonFile = open(path, "r", encoding='utf-8')
		data = json.load(jsonFile)
		jsonFile.close()

		return json.dumps(data, ensure_ascii=False)
	except:
		return 'server error', 404


def createOrUpdateImage(base64Img, tag):
	base64Img = base64Img + "=" * (4 - len(base64Img) % 4)
	imgdata = base64.b64decode(str(base64Img))

	pathToImage = "items/balance/" + tag + ".png"
	with open("py_modules/telegram/images/" + pathToImage, 'wb+') as file:
		file.write(imgdata)

	return pathToImage

def recurseToSetValue(jsonTree, operation, pathToKey, prevKey, newValue):
	key = pathToKey.pop(0)
	if key not in jsonTree: jsonTree[key] = {}
	if len(pathToKey): # if there are more levels to go down
		recurseToSetValue(jsonTree[key], operation, pathToKey, key, newValue) # recurse
	else:
		if operation == '$set':
			if key == 'image':
				jsonTree[key] = createOrUpdateImage(newValue, prevKey)
			else:
				jsonTree[key] = newValue
		elif operation == '$delete':
			del jsonTree[key]
	return jsonTree

def setValueInJson(jsonTree, operation, pathToKeyString, newValue): # double entery intentional
    pathToKey = pathToKeyString.split('.')
    recurseToSetValue(jsonTree, operation, pathToKey, None, newValue)

def updateJsonFile(path, queries):
	try:
		# Get data from JSON file
		jsonFile = open(path, "r", encoding='utf-8')
		jsonTree = json.load(jsonFile)
		jsonFile.close()

		print(queries)
		for operation in queries:
			for keyPath in queries[operation]:
				value = queries[operation][keyPath]
				setValueInJson(jsonTree, operation, keyPath, value)

		## Save our changes to JSON file
		jsonFile = open(path, "w+", encoding='utf-8')
		jsonFile.write(json.dumps(jsonTree, ensure_ascii=False))
		jsonFile.close()
		return 'good'
	except Exception as e:
		print(traceback.format_exc())
		return False

@app.route('/admin/<u>/<p>/image/<path:path>')
def imageItem(u, p, path):
	try: assert username == u and password == p
	except: return 'wrong username or password'
	return send_from_directory("./py_modules/telegram/images/", path)

@app.route('/admin/<u>/<p>/message/send_whatsapp_message/', methods=['POST'])
def sendWhatsappMessages(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	data = json.loads(request.data)

	f = open("temp_w.txt", "w+")
	f.write(str(data))
	f.close()

	f = open("temp_w.txt", "r")
	strData = f.read().replace("'", '"')
	f.close()
	os.remove("temp_w.txt")

	data = json.loads(strData)

	if data["base64Image"] != "#":
		img = convertBase64ToImage(data["base64Image"])
		img = img.resize((512, 512 * img.height // img.width))
		
		buffered = BytesIO()
		img.save(buffered, format="PNG")
		img_str = base64.b64encode(buffered.getvalue())

		data["base64Image"] = img_str

	r = requests.post('https://whatsapp-web-potato.herokuapp.com/mail/', data = data)
	
	return 'Responce: ' + r.text

@app.route('/admin/<u>/<p>/message/send_telegram_message/', methods=['POST'])
def sendTelegramMessages(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	data = json.loads(request.data)

	f = open("temp_t.txt", "w+")
	f.write(str(data))
	f.close()

	f = open("temp_t.txt", "r")
	strData = f.read().replace("'", '"')
	f.close()
	os.remove("temp_t.txt")

	data = json.loads(strData)

	if data["base64Image"] != "#":
		img = convertBase64ToImage(data["base64Image"])
		img = img.resize((512, 512 * img.height // img.width))
		
		buffered = BytesIO()
		img.save(buffered, format="PNG")
		img_str = base64.b64encode(buffered.getvalue())

		data["base64Image"] = img_str

	for phone in data['phones']:
		print(phone)
		user = find_user({'phone': phone})
  
		if data['base64Image'] != '#':
			bot.send_photo(chat_id=user._id,
						   photo=convertBase64ToImage(data['base64Image']),
						   caption=data['message'],
						   parse_mode='html')
		else:
			bot.send_message(chat_id=user._id, 
							 text=data['message'], 
							 parse_mode='html')
	return 'Message sent to all users'

@app.route('/admin/<u>/<p>/message/send_poll/', methods=['POST'])
def sendTelegramPolls(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	data = json.loads(request.data)
	print(data, type(data['phones']))
	for phone in data['phones']:
		user = find_user({'phone': phone})
		poll = bot.send_poll(chat_id = user._id,
						question = data['question'],
						options = data['options'],
						is_anonymous=False)
		user.set_new_poll(poll.poll)
	return 'Poll sent to all users'

# --------------------------------------------------------------------


import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

def getData(u):
	d = list(u.find())
	output = []
	for person in d:
		for operation in person["operations"]:
			if operation["details"] == 'кешбэк':
				output.append(operation["sum"])
	return output

def plot(f):
	output = io.BytesIO()
	FigureCanvas(f).print_png(output)
	return Response(output.getvalue(), mimetype='image/png')

@app.route('/admin/<u>/<p>/analytic/plot_1.png')
def plot_1(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title('Распредиление Покупок')
	axis.set_xlabel('Стоимость')
	axis.set_ylabel('Кол-во Покупок')
	xs = getData(users)
	axis.hist(xs, bins = int(180/5), color = 'blue', edgecolor = 'black')
	if(u == username and p == password):
		return plot(fig)

@app.route('/admin/<u>/<p>/analytic/plot_2.png')
def plot_2(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title('Распредиление Покупок')
	axis.set_ylabel('Стоимость')
	xs = getData(users)
	axis.boxplot(xs, flierprops={'marker': 'o', 'markersize': 4, 'markerfacecolor': 'fuchsia'})
	if(u == username and p == password):
		return plot(fig)

@app.route('/admin/<u>/<p>/analytic/plot_3.png')
def plot_3(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title('Распредиление Покупок')
	axis.set_ylabel('Стоимость')
	xs = getData(users)
	axis.boxplot(xs, flierprops={'marker': 'o', 'markersize': 4, 'markerfacecolor': 'fuchsia'})
	if(u == username and p == password):
		return plot(fig)