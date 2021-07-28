from flask import current_app as app
from flask import send_from_directory

@app.route('/')
@app.route('/<path:path>')
def send_file(path = ""):
	if("login" in path and "." in path):	
		return send_from_directory('./hidden/', path)
	elif("login" in path):
		return send_from_directory('./hidden/', path + "/index.html")
		

	if("." in path):
		return send_from_directory('./public/', path)
	elif(path == ""):
		return send_from_directory('./public/', "index.html")
	else:
		return send_from_directory('./public/', path + "/index.html")