from flask import Flask

app = Flask(__name__)

from py import files
from py import mongo
from py import api
from py import admin

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)