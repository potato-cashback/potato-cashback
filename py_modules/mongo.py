from config import URI, URL

from flask import current_app as app
from flask_pymongo import PyMongo
import requests
import ssl

try:
	cluster = PyMongo(app, uri=URI, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
	users = cluster.db.user

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
except:
	@app.route('/mongodb')
	def get_data():
		return '[]'

	@app.route('/mongodb/phone/<phone>')
	def phone_name(phone):
		return ""
		
	print('MongoDB not connected')

# Find
# users.find({}) # find all users
# Update 
# users.update_one({'phone': 'XXXXX'}, {'$set': {'cashback': value}})
# Insert
# users.insert_one({})


@app.route('/mongodb/phone/<phone>/<sum>')
def send_data(phone, sum):
	try:
		r = requests.get(URL + '/send_data/'+phone+'/'+sum)
		if(r.text == 'nice'):
			return 'good'
		elif(r.text == 'bad'):
			return 'bad'
	except:	
		return 'server error'