from flask import Flask, send_from_directory
from flask_pymongo import PyMongo
from config import *
import urllib.request
import os

app = Flask(__name__)
cluster = PyMongo(app, uri=URI)
users = cluster.db.user

# Find
# users.find({}) # find all users
# Update 
# users.update_one({'phone': 'XXXXX'}, {'$set': {'cashback': value}})
# Insert
# users.insert_one({})

def create_file(id, message):
	file = open(f'./public/_ids/{id}', "w")
	file.write(message)
	file.close

def delete_file(id):
	os.remove(f'./public/_ids/{id}')
# ----------------------- MongoDB ------------------------------------

@app.route('/mongodb')
def get_data():
	d = str(list(users.find()))
	return d

@app.route('/mongodb/phone/<phone>')
def phone_name(phone):
	user = users.find_one({'phone': phone})
	if user != None:
		return user['name']
	else:
		return ""

@app.route('/mongodb/phone/<phone>/<sum>')
def send_data(phone, sum):
	urllib.request.urlopen('https://qr-code-telegram-bot.herokuapp.com/send_data/'+phone+'/'+sum)
	return "bruh"


# ----------------------- FILES ------------------------------------
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


#---------------------- API ----------------------------------------    
@app.route('/api/create/<qrId>', methods=['GET'])
def create(qrId):
	create_file(qrId, '')
	return '{"status":"ok", "id":'+qrId+'}'

@app.route('/api/react/<qrId>', methods=['GET'])
def react(qrId):
	if(not os.path.exists('./public/_ids/' + qrId)):
		return '{"status": "not ok", "error": "no such data"}'

	create_file(qrId, '0')
	return '{"status":"ok", "id":'+qrId+'}'

@app.route('/api/response/<qrId>', methods=['GET'])
def response(qrId):
	create_file(qrId, '1')
	return '{"status":"ok", "id":'+qrId+'}'

@app.route('/api/cancel/<qrId>', methods=['GET'])
def cancel(qrId):
	create_file(qrId, '2')
	return '{"status":"ok", "id":'+qrId+'}'

@app.route('/ids/<qrId>', methods=['GET'])
def ids(qrId):
	try:
		file = open(f'./public/_ids/{qrId}')
		data = file.read()

		if str(data) == "1" or str(data) == "2":
			delete_file(qrId)
		return '{"status":"ok", "data":"'+ str(data) +'"}'
	except:
		return '{"status":"ok", "data":"no data"}'

# ---------------------------- LOGIN ------------------------------
@app.route('/login')
def send_file10():
	return send_from_directory('./hidden/login/', 'index.html')
@app.route('/login/<path:path>')
def send_file11(path):
	return send_from_directory('./hidden/login/', path)

@app.route('/admin/<u>/<p>/<path>')
def loggingin(u, p, path):
	if(u == 'admin' and p == 'analitic'):
		return send_from_directory('./hidden/admin/', path + '/index.html')
	else:
		return '<script>window.location.href = "/"</script>'

# ----------------------------- SERVER ------------------------------
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)

# ---------------------------- AUTO DELETE --------------------------

# import os, shutil
# folder = './public/_ids/'
# for filename in os.listdir(folder):
#     file_path = os.path.join(folder, filename)
#     try:
#         if os.path.isfile(file_path) or os.path.islink(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path):
#             shutil.rmtree(file_path)
#     except Exception as e:
#         print('Failed to delete %s. Reason: %s' % (file_path, e))

