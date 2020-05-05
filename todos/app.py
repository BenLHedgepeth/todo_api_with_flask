from flask import Flask, jsonify, render_template

from config import HOST, PORT, DEBUG

from peewee import *


import models
from resources.todos import todo_api


app = Flask(__name__)
app.register_blueprint(todo_api, url_prefix="/api/v1/todos")

models.DATABASE.init('todo_api.db')
models.initialize(models.Todo)


@app.errorhandler(404)
def not_found(e):
    message = str(e).split(':')[1]
    return jsonify(error=message), 404


@app.errorhandler(400)
def bad_request(e):
    message = str(e).split(':')[1]
    return jsonify(error=message), 400


@app.route('/')
def my_todos():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
