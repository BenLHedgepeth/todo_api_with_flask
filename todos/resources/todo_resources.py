from flask import Blueprint

from flask_restful import Api, Resource

todo_api = Blueprint('resources.todos', __name__)
api = Api(todo_api)

