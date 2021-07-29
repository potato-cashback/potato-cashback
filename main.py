from flask import Flask

app = Flask(__name__)

with app.app_context():
    from py_modules import admin, api, files, mongo

with app.app_context():
	from py_modules.telegram import telegram

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)