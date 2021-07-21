from __main__ import app
from config import URI

from flask_pymongo import PyMongo
import requests
import ssl

cluster = PyMongo(app, uri=URI, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
users = cluster.db.user


# Find
# users.find({}) # find all users
# Update 
# users.update_one({'phone': 'XXXXX'}, {'$set': {'cashback': value}})
# Insert
# users.insert_one({})


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
	r = requests.get('https://qr-code-telegram-bot.herokuapp.com/send_data/'+phone+'/'+sum)
	if(r.text == 'nice'):
		return 'good'
	elif(r.ok == True):
		return 'bad'
	else:
		return 'server error'