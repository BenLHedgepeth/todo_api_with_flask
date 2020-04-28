
import sys

from os.path import abspath, dirname

from flask import Blueprint, abort

from flask_restful import Api, Resource, fields, marshal, reqparse

from models import User

from .utils import set_todos
from exceptions import PasswordMatchError

user_api = Blueprint('resources.users', __name__)
api = Api(user_api, serve_challenge_on_401=True)

user_fields = {
    'id': fields.String,
    'username': fields.String,
    'todos_created': fields.List(fields.String)
}

class ApiUserCollection(Resource):

    request_parser = reqparse.RequestParser(trim=True, bundle_errors=True)
    request_parser.add_argument('username', required=True, location=['form', 'json'])
    request_parser.add_argument('password', required=True)
    request_parser.add_argument('verify_password', required=True)

    def get(self):
        api_users = User.select()
        if not api_users.count():
            abort(404, description="No users currently exist")
        return [marshal(set_todos(api_user), user_fields) for api_user in api_users]

    def post(self):
        args = self.request_parser.parse_args()
        try:
            new_user = User.create_user(**args)
        except (PasswordMatchError, ValueError) as e:
            abort(400, description=e)
        else:
            if new_user:
                return (
                    marshal(new_user, user_fields, 'user'),
                    201, {'Location': f'api/v1/users/{new_user.id}/'}
                )
            return


api.add_resource(
    ApiUserCollection,
    '/',
    endpoint="users"
)


class ApiUser(Resource):

    def get(self, id):
        try:
            api_user = User.get(User.id==id)
        except User.DoesNotExist:
            abort(404, description="Cannot locate User with that ID")
        else:
            return marshal(set_todos(api_user), user_fields, envelope='user'), 200

api.add_resource(
    ApiUser,
    '/<int:id>',
    endpoint="user"
)
