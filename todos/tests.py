from base64 import b64encode
import unittest
import sys
import json



from flask import url_for, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from peewee import *

from app import app
from models import User, Todo
from auth import verify_password, verify_token
from config import SECRET_KEY


DATABASE = SqliteDatabase(':memory:')


class ApiTestCase(unittest.TestCase):
    '''Create tables and instantiate database'''

    def setUp(self):

        models = [User, Todo]

        '''Binds models to test database and creates tables'''
        DATABASE.bind(models)
        DATABASE.create_tables(models, safe=True)

        self.todo_resources = [
            {'name': "Task1"}, {'name': "Task2"}, {'name': "Task3"}
        ]

        self.users = [
            {'username': "User_1", 'password': 'secret1'},
            {'username': "User_2", 'password': 'secret2'}
        ]

        for i, todo in enumerate(self.todo_resources):
            try:
                user = User(username=self.users[i]['username'])
                user.password = user.set_password(self.users[i]['password'])
                user.save()
            except IndexError:
                user = User.get_by_id(i)
                todo.update({'user': user})
            else:
                todo.update({'user': user})

        with DATABASE.transaction():
            '''Bulk inserts model instances into the database'''
            Todo.insert_many(self.todo_resources).execute()

    def tearDown(self):
        with DATABASE:
            DATABASE.drop_tables([User, Todo])


class TestApiTokenRequest(ApiTestCase):
    '''Verify that a token is issued to an API user'''
    def test_issue_api_token_success(self):
        user_credentials = b64encode(b"User_1:secret1").decode()
        with app.test_client() as client:
            http_response = client.get(
                "/api/v1/token",
                headers={
                    'Authorization': f"Basic {user_credentials}"
                }
            )
            json_data = http_response.get_json()
        self.assertIn('token', json_data)


class TestVerifyPasswordCallback(ApiTestCase):
    '''Verify that a user's credentials validates
    and the user is enabled to access login required
    protected resources.'''

    def test_verify_password_callback(self):
        '''NOTE: The global object "g" is being set within
        this function and an application context is required'''

        with app.test_request_context():
            user_verified = verify_password("User_1", 'secret1')
        self.assertTrue(user_verified)


class TestApiUserCollection(ApiTestCase):
    '''Verify that a 404 status code is sent back to the
    client when there is no ApiUser collection resource [GET]'''

    def setUp(self):
        super().setUp()
        delete_users = User.delete().where(Todo.id >= 1)
        delete_users.execute()

    def test_get_api_user_collection(self):
        with app.test_client() as client:
            http_response = client.get('api/v1/users/')

        self.assertEqual(http_response.status_code, 404)


class TestCreateNewApiUserResource(ApiTestCase):
    '''Verify that a client creates a new ApiUser resource [POST].'''
    def setUp(self):
        super().setUp()
        self.previous_user_count = User.select().count()


    def test_post_create_user_success(self):
        with app.test_client() as client:
            http_response = client.post(
                'api/v1/users/',
                content_type="application/json",
                data=json.dumps({
                    'username': 'User_101',
                    'password': 'mypassword',
                    'verify_password': 'mypassword'
                })
            )
            new_user = http_response.get_json()['user']['username']

        current_user_count = User.select().count()

        self.assertEqual(http_response.status_code, 201)
        self.assertGreater(current_user_count, self.previous_user_count)
        self.assertEqual(new_user, "User_101")


class TestInvalidUserCredentials(ApiTestCase):
    '''Verify that a client gets a 400 status code
    when the passwords don't match [POST].'''

    def test_post_create_user_invalid_password(self):
        with app.test_client() as client:
            http_response = client.post(
                'api/v1/users/',
                content_type="application/json",
                data=json.dumps({
                    'username': 'User_101',
                    'password': 'mypassword',
                    'verify_password': 'notmypassword'
                })
            )

        self.assertEqual(http_response.status_code, 400)

class TestUserTodoPostNoToken(ApiTestCase):
    '''Verify that an API user cannot create a Todo
    without an API token.'''

    def setUp(self):
        super().setUp()
        self.login_creds = b64encode(b"User_2:secret2").decode()

    def test_post_todo_fail_no_token(self):
        with app.test_client() as client:
            http_response = client.post(
                'api/v1/todos/',
                headers={
                    'authorization': f"Basic {self.login_creds}"
                },
                json={
                    "name": "A simple todo",
                    "user": 2
                }
            )
            unauthorized = http_response.get_json()['unauthorized']

        self.assertEqual(http_response.status_code, 401)
        self.assertEqual(
            unauthorized, "Cannot add Todo. Access token required."
        )


class TestAuthenicatedUserPostTodo(ApiTestCase):
    '''Verifying the responses the API transmits'''

    def setUp(self):
        super().setUp()
        self.previous_todo_count = Todo.select().count()

        user = User.get(User.id == 1)
        token_serializer = Serializer(SECRET_KEY)
        self.token = token_serializer.dumps({'id': user.id}).decode()

    def test_todo_collection_post_todo_success(self):
        '''Verify that a client receives a 201 status code after
        successfully creating a new Todo.'''

        with app.test_client() as client:
            http_response = client.post(
                "/api/v1/todos/",
                headers={
                    'authorization': f"Bearer {self.token}",
                    'content_type': "application/json"
                },
                data={
                    "name": "Must do a todo",
                    "user": 1
                }
            )
        current_todo_count = Todo.select().count()
        self.assertEqual(http_response.status_code, 201)
        self.assertGreater(current_todo_count, self.previous_todo_count)

    def test_todo_collection_post_todo_fail(self):
        '''Verify that a client receives a 400 status code after
        failing to provide a name for a new Todo.'''

        with app.test_client() as client:
            http_response = client.post(
                "/api/v1/todos/",
                headers={
                    'authorization': f"Bearer {self.token}",
                },
                json={
                    "name": "",
                    "user": 1
                }
            )
            invalid_todo = http_response.get_json()['invalid_request']
        self.assertEqual(http_response.status_code, 400)
        self.assertEqual(invalid_todo, "Invalid todo provided")


class TestNoTodoCollectionExists(ApiTestCase):
    '''Verify that a HTTP response returns a 404 status status code
    when there are no Todo resources in the TodoCollection resource [GET]'''

    def setUp(self):
        super().setUp()
        delete_todos = Todo.delete().where(Todo.id >= 1)
        delete_todos.execute()

    def test_todo_collection_resource_no_todos(self):
        with app.test_client() as client:
            http_response = client.get("api/v1/todos/")
        self.assertEqual(http_response.status_code, 404)


class TestGetTodoCollection(ApiTestCase):
    '''Verify that a representation of all todo resources
    are sent back to the client with a 200 status code [GET].'''

    def test_todo_collection_resource(self):
        with app.test_client() as client:
            http_response = client.get("/api/v1/todos/")
        self.assertEqual(http_response.status_code, 200)


class TestTodoResource(ApiTestCase):
    '''Verify that a 200 status code is sent back to the
    client to indicate a resource was successfully found [GET].'''

    def test_get_todo_resource_success(self):
        with app.test_client() as client:
            http_response = client.get("api/v1/todos/2")
            todo_resource_name = http_response.get_json()['todo']

        self.assertEqual(http_response.status_code, 200)
        self.assertEqual(todo_resource_name['name'], 'Task2')


class TestNoTodoResource(ApiTestCase):
    '''Verify that a 404 status code is sent back to the client
    when a resource with a given id does not exist [GET].'''
    def test_get_todo_resource_not_found(self):
        with app.test_client() as client:
            http_response = client.get("api/v1/todos/8")

        self.assertEqual(http_response.status_code, 404)


class TestUpdateTodoResource(ApiTestCase):
    '''Verify that a client succesfully updates an existing todo.'''
    def setUp(self):
        super().setUp()
        user = User.get_by_id(2)
        token_serializer = Serializer(SECRET_KEY)
        self.token = token_serializer.dumps({'id': user.id}).decode()

    def test_put_update_user_todo_success(self):
        with app.test_client() as client:
            http_response = client.put(
                "api/v1/todos/3",
                headers={
                    'authorization': f"Bearer {self.token}"
                },
                data = {
                    "name": "Quit it!",
                }
            )
        self.assertEqual(http_response.status_code, 204)

    def test_put_update_todo_name_exists_fail(self):
        with app.test_client() as client:
            http_response = client.put(
                "api/v1/todos/3",
                headers={
                    'authorization': f"Bearer {self.token}"
                },
                json = {
                    "name": "Task1",
                }
            )
            json_data = http_response.get_json()
        self.assertEqual(http_response.status_code, 400)


class TestDeleteTodoResource(ApiTestCase):
    '''Verify that a client successfully deletes a todo.'''

    def setUp(self):
        super().setUp()
        self.previous_todo_count = Todo.select().count()
        user = User.get_by_id(1)
        token_serializer = Serializer(SECRET_KEY)
        self.token = token_serializer.dumps({'id': user.id}).decode()

    def test_delete_todo_success(self):
        with app.test_client() as client:
            http_response = client.delete(
                "/api/v1/todos/1",
                headers={
                    'authorization': f"Bearer {self.token}"
                }
            )
            current_todo_count = Todo.select().count()

        self.assertLess(current_todo_count, self.previous_todo_count)
        self.assertEqual(http_response.status_code, 204)

if __name__ == '__main__':
    unittest.main()
