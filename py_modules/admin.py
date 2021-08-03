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

def recurseToSetValue(jsonTree, operation, pathToKey, newValue):
    key = pathToKey.pop(0)
    
    if key not in jsonTree: jsonTree[key] = {}

    if len(pathToKey): # if there are more levels to go down
        recurseToSetValue(jsonTree[key], operation, pathToKey, newValue)
        # recurse
    else:
        if operation == '$set':
            jsonTree[key] = newValue
        elif operation == '$delete':
            del jsonTree[key]

    return jsonTree

def setValueInJson(jsonTree, operation, pathToKeyString, newValue): # double entery intentional
    pathToKey = pathToKeyString.split('.')
    
    recurseToSetValue(jsonTree, operation, pathToKey, newValue)

def updateJsonFile(path, queries):
	try:
		# Get data from JSON file
		jsonFile = open(path, "r", encoding='utf-8')
		jsonTree = json.load(jsonFile)
		jsonFile.close()

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
		print('Error! Code: {c}, Message, {m}'.format(c = type(e).__name__, m = str(e)))
		return False


@app.route('/admin/<u>/<p>/image/<path:path>')
def imageItem(u, p, path):
	try: assert username == u and password == p
	except: return 'wrong username or password'
	return send_from_directory("./py_modules/telegram/images/", path)

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