import json

from flask import Blueprint, jsonify, abort, make_response, g, url_for
from peewee import *
from flask_restful import Api, Resource, fields, marshal, reqparse

from models import Todo

todo_api = Blueprint("resources.todos", __name__)
api = Api(todo_api)

todo_fields = {
    'id': fields.String,
    'name': fields.String
}


class TodoCollection(Resource):

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'name',
            required=True,
            location=['form', 'json'],
            help="Add the name of Todo"
        )

    def get(self):
        all_todos = Todo.select()
        if not all_todos:
            abort(404, description="No todos currently exist.")
        all_todos = ([marshal(todo, todo_fields)
                      for todo in all_todos])
        return {'todos': all_todos}

    def post(self):
        args = self.request_parser.parse_args()
        argument_name = args['name'].strip()
        if not argument_name:
            abort(400, description="Invalid todo name")
        new_todo = Todo.create(**args)
        return (marshal(new_todo, todo_fields, 'new_todo'),
                201, {'location': str(new_todo)})

api.add_resource(
    TodoCollection,
    '/',
    endpoint='todos'
)


class ApiTodo(Resource):

    def __init__(self):
        '''Parse arguments for incoming PUT requests'''
        self.put_request_parser = reqparse.RequestParser()
        self.put_request_parser.add_argument(
            'name',
            required=True,
            location=['form', 'json'],
            help="Cannot accept a blank description"
        )

    def get(self, id):
        try:
            api_todo = Todo.get_by_id(id)
        except Todo.DoesNotExist:
            abort(404, description="That todo does not exist")
        return marshal(api_todo, todo_fields, envelope="todo")

    def put(self, id):
        try:
            user_todo = Todo.select().where(Todo.id == id).get()
        except Todo.DoesNotExist:
            abort(404, description="That todo no longer exists")
        else:
            args = self.put_request_parser.parse_args()
            argument_name = args['name'].strip()
            if not argument_name:
                abort(400, description="Must provide a todo description")
            todo_exists = Todo.get_or_none(Todo.name == args['name'])
            if todo_exists:
                abort(400, description="That todo already exists")
            else:
                user_todo.name = args['name']
                user_todo.save()
            return marshal(user_todo, todo_fields, 'todo'), 204

    def delete(self, id):
        try:
            user_todo = Todo.select().where(Todo.id == id).get()
        except Todo.DoesNotExist:
            abort(404, description="That todo no longer exists")
        else:
            user_todo.delete_instance()
        return make_response(
            " ", 204, {"location": url_for("resources.todos.todos")}
        )

api.add_resource(
    ApiTodo,
    '/<int:id>',
    endpoint="todo"
)
