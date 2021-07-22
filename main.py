from flask import Flask

app = Flask(__name__)

from py_modules import files
from py_modules import mongo
from py_modules import api
from py_modules import admin
from py_modules.telegram import telegram

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)