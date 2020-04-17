from flask import Flask, g, jsonify, render_template
from config import HOST, PORT, DEBUG

from peewee import *


import models
from resources.todo import todo_api
from resources.users import user_api

app = Flask(__name__)
app.register_blueprint(todo_api, url_prefix="/api/v1/todos")
app.register_blueprint(user_api, url_prefix="/api/v1/users")

models.DATABASE.init('todo_api.db')
models.initialize(models.User, models.Todo)

@app.errorhandler(404)
def not_found(e):
    return {'error': str(e)}, 404

@app.route('/')
def my_todos():
    return render_template('index.html')

if __name__ == '__main__':
    print(app.url_map)
    app.run(host=HOST, port=PORT, debug=DEBUG)
