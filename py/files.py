from __main__ import app
from flask import send_from_directory

@app.route('/')
def send_file1():
	return send_from_directory('./public/', 'index.html')

@app.route('/<path:path>')
def send_file2(path):
	return send_from_directory('./public/', path)

@app.route('/qr')
def send_file3():
	return send_from_directory('./public/qr/', 'index.html')

@app.route('/qr/<path:path>')
def send_file4(path):
	return send_from_directory('./public/qr/', path)
	
@app.route('/table')
def send_file5():
	return send_from_directory('./public/table/', 'index.html')
@app.route('/table/<path:path>')
def send_file6(path):
	return send_from_directory('./public/table/', path)
	
@app.route('/phone')
def send_file7():
	return send_from_directory('./public/phone/', 'index.html')
@app.route('/phone/<path:path>')
def send_file8(path):
	return send_from_directory('./public/phone/', path)

@app.route('/app/<path:path>')
def send_file9(path):
	return send_from_directory('./public/app/', path)
