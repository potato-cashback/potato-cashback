from __main__ import app
from config import username, password

from flask import send_from_directory, Response

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

@app.route('/admin/<u>/<p>/analytic/plot.png')
def plot_png(u, p):
	if(u == username and p == password):
		fig = create_figure()
		output = io.BytesIO()
		FigureCanvas(fig).print_png(output)
		return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig
