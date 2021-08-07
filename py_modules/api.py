from flask import current_app as app
import os, shutil
import json

folder = "./public/_ids/"

if not os.path.exists(folder):
	print("folder created")
	os.makedirs(folder)
else:
	for filename in os.listdir(folder):
		file_path = os.path.join(folder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			print('Failed to delete %s. Reason: %s' % (file_path, e))

def create_file(id, message):
	file = open(f'./public/_ids/{id}', "w")
	file.write(message)
	file.close

def delete_file(id):
	os.remove(f'./public/_ids/{id}')


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

def get(*args):
	path = './hidden/settings.json'
	jsonFile = open(path, "r", encoding='utf-8')
	data = json.load(jsonFile)
	jsonFile.close()
	return [data[k] for k in list(args)]

@app.route('/getCashbackLogic/<sum>')
def get_cashback_logic(sum):
	sum = int(sum)
	[cashback] = get("cashback")

	arr_cashback = [cashback[x] for x in cashback]

	arr_cashback = sorted(arr_cashback, key=lambda k: k['on'])
	for i in range(len(arr_cashback)):
		if i+1 == len(arr_cashback):
			if arr_cashback[i]['on'] <= sum:
				return str(arr_cashback[i]['percent'] / 100)
		elif arr_cashback[i]['on'] <= sum and sum < arr_cashback[i+1]['on']:
			return str(arr_cashback[i]['percent'] / 100)
	return 'error'