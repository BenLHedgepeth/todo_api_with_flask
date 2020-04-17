
from flask import Blueprint, abort

from flask_restful import Api, Resource, fields, marshal

from models import User

user_api = Blueprint('resources.users', __name__)
api = Api(user_api)

user_fields = {
    'username': fields.String
}

class ApiUserCollection(Resource):

    def get(self):
        api_users = User.select()
        if not api_users.count():
            abort(404, description="No users currently exist")
        return [marshal(api_user, user_fields) for api_user in api_users]

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
            return marshal(api_user, user_fields, envelope='user'), 200

api.add_resource(
    ApiUser,
    '/<int:id>',
    endpoint="user"
)
