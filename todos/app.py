from flask import Flask, g, jsonify, render_template
from config import HOST, PORT, DEBUG

from peewee import *

import models

app = Flask(__name__)

models.DATABASE.init('todo_api.db')
models.initialize(models.User, models.Todo)


@app.route('/')
def my_todos():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)