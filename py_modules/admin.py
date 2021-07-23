from config import username, password

from flask import current_app as app
from flask import send_from_directory, Response

from py_modules.mongo import users

@app.route('/login')
def send_file10():
	return send_from_directory('./hidden/login/', 'index.html')
@app.route('/login/<path:path>')
def send_file11(path):
	return send_from_directory('./hidden/login/', path)

@app.route('/admin/<u>/<p>/<path>')
def loggingin(u, p, path):
	if(u == username and p == password):
		return send_from_directory('./hidden/admin/', path + '/index.html')
	else:
		return '<script>window.location.href = "/"</script>'

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
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title('Распредиление Покупок')
	axis.set_ylabel('Стоимость')
	xs = getData(users)
	axis.boxplot(xs, flierprops={'marker': 'o', 'markersize': 4, 'markerfacecolor': 'fuchsia'})
	if(u == username and p == password):
		return plot(fig)