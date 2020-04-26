
import json

from flask import Blueprint, jsonify, abort, make_response

from flask_restful import Api, Resource, fields, marshal, reqparse

from .utils import set_todo_creator
from auth import token_auth as auth

'''todo.py have access to models because resources inherents todos package modules???'''
from models import Todo

todo_api = Blueprint("resources.todos", __name__)
api = Api(todo_api, serve_challenge_on_401=True)

todo_fields = {
    'name': fields.String,
    'created_by': fields.String
}


@auth.error_handler
def errorhandler():
    return jsonify(unauthorized="Cannot add Todo. Login required."), 401


class TodoCollection(Resource):

    request_parser = reqparse.RequestParser()
    request_parser.add_argument(
        'name',
        required=True,
        location=['form', 'json'],
        help="Add the name of Todo"
    )
    request_parser.add_argument(
        'user',
        required=True,
        location=['form', 'json'],
        help="Add the user of the todo"
    )

    def get(self):
        all_todos = Todo.select()
        if not all_todos:
            abort(404, description="No todos currently exist.")
        all_todos = ([marshal(set_todo_creator(todo), todo_fields)
                        for todo in all_todos])
        return {'todos': all_todos}

    @auth.login_required
    def post(self):
        import pdb; pdb.set_trace()
        args = self.request_parser.parse_args()
        if not args['name']:
            return make_response(
                {'invalid_request': "Invalid todo provided"}, 400
            )
        new_todo = Todo.create(**args)
        return (
            marshal(set_todo_creator(new_todo), todo_fields, 'new_todo'),
            201, {'Location': f'{new_todo.location}'}
        )



api.add_resource(
    TodoCollection,
    '/',
    endpoint='todos'
)

class ApiTodo(Resource):

    def get(self, id):
        try:
            api_todo = Todo.get_by_id(id)
        except Todo.DoesNotExist:
            abort(404, description="That todo does not exist")
        return marshal(set_todo_creator(api_todo), todo_fields, envelope="todo")

    @auth.login_required
    def put(self):
        pass

api.add_resource(
    ApiTodo,
    '/<int:id>',
    endpoint="todo"
)
