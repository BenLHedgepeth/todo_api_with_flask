
import json

from flask import Blueprint, jsonify, abort, make_response, g
from peewee import *
from flask_restful import Api, Resource, fields, marshal, reqparse

from .utils import set_todo_creator
from models import User
from auth import token_auth as auth

'''todo.py have access to models because resources inherents todos package modules???'''
from models import Todo

todo_api = Blueprint("resources.todos", __name__)
api = Api(todo_api, serve_challenge_on_401=True)

todo_fields = {
    'name': fields.String,
    'user': fields.String
}


@auth.error_handler
def error_handler():
    return jsonify(unauthorized="Cannot add Todo. Access token required."), 401


class TodoCollection(Resource):

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument(
            'name',
            required=True,
            location=['form', 'json'],
            help="Add the name of Todo"
        )
        self.request_parser.add_argument(
            'user',
            required=True,
            location=['form', 'json'],
            help="Add the user of the todo"
        )

    def get(self):
        all_todos = Todo.select()
        if not all_todos:
            abort(404, description="No todos currently exist.")
        all_todos = ([marshal(todo, todo_fields)
                        for todo in all_todos])
        return make_response(jsonify({'todos': all_todos}))

    @auth.login_required
    def post(self):
        args = self.request_parser.parse_args()
        argument_name = args['name'].strip()
        if not argument_name:
            return make_response(
                jsonify(invalid_request="Invalid todo provided"), 400
            )
        new_todo = Todo.create(**args)
        return (marshal(new_todo, todo_fields, 'new_todo'),
            201, {'location': f''} #<<<< fix
        )

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
        return marshal(set_todo_creator(api_todo), todo_fields, envelope="todo")

    @auth.login_required
    def put(self, id):
        try:
            user_todo = Todo.select().join(User).where(
                (Todo.id == id) & (User.id == g.user.id)
            ).get()
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

    @auth.login_required
    def delete(self, id):
        try:
            user_todo = Todo.select().where(
                (Todo.id == id) & (Todo.user == g.user)
            ).get()
        except Todo.DoesNotExist:
            pass
        else:
            user_todo.delete_instance()
        return make_response(" ", 204)

api.add_resource(
    ApiTodo,
    '/<int:id>',
    endpoint="todo"
)
