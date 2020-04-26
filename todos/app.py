from flask import Flask, g, jsonify, render_template, current_app

from config import HOST, PORT, DEBUG

from peewee import *


import models
from resources.todo import todo_api
from resources.users import user_api
from auth import basic_auth as auth

app = Flask(__name__)
app.register_blueprint(todo_api, url_prefix="/api/v1/todos")
app.register_blueprint(user_api, url_prefix="/api/v1/users")

models.DATABASE.init('todo_api.db')
models.initialize(models.User, models.Todo)

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="str(e)"), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400

@app.route("/api/v1/token")
@auth.login_required
def issue_api_token():
    '''NOTE: @login_required must be declared below the Flask route
    or else "g" doesn\'t retain state for this view'''
    token = g.user.request_token()
    return jsonify(token=token)

@app.route('/')
def my_todos():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
