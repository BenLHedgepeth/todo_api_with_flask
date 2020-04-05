
from flask import Blueprint, jsonify

from flask_restful import Api, Resource, fields, marshal

from models import Todo

todo_api = Blueprint("resources.todos", __name__)
api = Api(todo_api)

todos_fields = {
    'name': fields.String
}

class TodoList(Resource):
    pass
    

api.add_resource(
    TodoList,
    ''
    'todos'
)