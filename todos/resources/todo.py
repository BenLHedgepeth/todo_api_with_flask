
from flask import Blueprint, jsonify, abort

from flask_restful import Api, Resource, fields, marshal

from .utils import set_todo_creator

'''todo.py have access to models because resources inherents todos package modules???'''
from models import Todo

todo_api = Blueprint("resources.todos", __name__)
api = Api(todo_api)

todo_fields = {
    'name': fields.String,
    'created_by': fields.String
}

class TodoCollection(Resource):

    def get(self):
        all_todos = Todo.select()
        if not all_todos:
            abort(404, description="No todos currently exist.")
        all_todos = ([marshal(set_todo_creator(todo), todo_fields)
                        for todo in all_todos])
        return {'todos': all_todos}



api.add_resource(
    TodoCollection,
    '/',
    endpoint='todos'
)
