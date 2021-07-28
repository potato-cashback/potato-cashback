from config import username, password

from flask import current_app as app
from flask import send_from_directory, Response, request

from py_modules.mongo import users
import json

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

@app.route('/admin/<u>/<p>/saveJSON', methods=['GET'])
def saveJson(u, p):
	try: assert username == u and password == p
	except: return 'wrong username or password'

	data = json.loads(request.args.get('data'))
	path = './hidden/settings.json'

	updateJsonFile(path, data)

	return 'saved'

def updateJsonFile(path, new_data):
	try:
		# Get data from JSON file
		jsonFile = open(path, "r", encoding='utf-8')
		data = json.load(jsonFile)
		jsonFile.close()

		for key in new_data:
			data[key] = new_data[key]

		## Save our changes to JSON file
		jsonFile = open(path, "w+", encoding='utf-8')
		jsonFile.write(json.dumps(data, ensure_ascii=False))
		jsonFile.close()
		return 'good'
	except Exception as e:
		print('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
		return False

import io
import random
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