import base64
import unittest

from flask import url_for
from peewee import *

from app import app
from models import User, Todo



DATABASE = SqliteDatabase(':memory:')

class ApiTestCase(unittest.TestCase):

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
                user = User.create(**self.users[i])
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


class TestTodoCollection(ApiTestCase):
    '''Verify that a HTTP response returns a 404 status status code
    when there are no Todo resources in the TodoCollection resource'''

    def setUp(self):
        super().setUp()
        delete_todos = Todo.delete().where(Todo.id >= 1)
        delete_todos.execute()

    def test_todo_collection_resource_no_todos(self):
        with app.test_client() as client:
            http_response = client.get("api/v1/todos/")
        self.assertEqual(http_response.status_code, 404)

    def tearDown(self):
        super().tearDown()


class TestTodoCollection_002(ApiTestCase):
    '''Verify that a representation of all todo resources
    are sent back to the client with a 200 status code.'''

    def setUp(self):
        super().setUp()

    def test_todo_collection_resource(self):
        with app.test_client() as client:
            http_response = client.get("/api/v1/todos/")
        self.assertEqual(http_response.status_code, 200)

        def tearDown(self):
            super().tearDown()

#
# class TestApiUserCollection(ApiTestCase):
#     '''Verify that a 404 status code is sent back to the
#     client when there is no ApiUser collection resource'''
#
#     def setUp(self):
#         super().setUp()
#
#     def test_get_api_user_collection(self):
#         with app.test_client() as client:
#             http_response = client.get('api/v1/users/')
#
#         self.assertEqual(http_response.status_code, 404)
#
#
#
#     def setUp(self):
#         super().tearDown()

# class TestGetUserResource(ApiTestCase):
#     '''Verify that a representation of a User resource
#     is sent back to the client as a result of a GET request.'''
#
#     def setUp(self):
#         super().setUp()
#
#     def test_get_user_resource_found(self):
#         with app.test_client() as client:
#             http_response = client.get("api/v1/users/1")
#
#             api_user = http_response.get_json()['user']
#
#         self.assertEqual(http_response.status_code, 200)
#         self.assertEqual(api_user['username'], "User_1")
#
#
#     def tearDown(self):
#         super().tearDown()
#
#
# # class TestGetUserResource_002(ApiTestCase):
# #     '''Verify that a client is sent a 404 status code
# #     when the server cannot locate a requested resource'''
# #
# #     def test_get_resource_not_found(self):
# #         with app.test_client() as client:
# #             http_response = client.get("api/v1/users/6")
# #
# #         self.assertEqual(http_response.status_code, 404)
#
# # class TestPostTodo_001(ApiTestCase):
# #     '''Verify that a 401 status code sent back
# #     to the client when it is not authenticated.'''
# #
# #     def setUp(self):
# #         super().setUp()
# #
# #     def test_todo_api_post_success(self):
# #         with app.client() as client:
# #             http_response = client.post("/api/v1/todos",
# #             json={'name': 'This is Task #4', user: 1},
# #
# #         self.assertEqual(http_response.status_code, 401)
# #         self.assertEqual(resource_location, "/api/v1/todos/4")
# #
# #
# #     def tearDown(self):
# #         super().tearDown()
# #
# # class TestPostTodo_002(ApiTestCase):
# #     '''Verify that the data the client submits to the server
# #     creates a new resource and receives a 201 status code'''
# #
# #     def setUp(self):
# #         super().setUp()
# #
# #     def test_todo_api_post_success(self):
# #         with app.client() as client:
# #             http_response = client.post("/api/v1/todos",
# #             json={'name': 'This is Task #4', user: 1},
# #             headers={
# #                 'Authorization': "Basic: " + base64.encode("User_1:secret1")}"
# #             })
# #
# #             resource_location = http_response.headers.get("Location")
# #         self.assertEqual(http_response.status_code, 201)
# #         self.assertEqual(resource_location, "/api/v1/todos/4")
# #
# #
# #     def tearDown(self):
# #         super().tearDown()
#
#
# # class TestAuthorizationFail(ApiTestCaseSetup):
# #
# #     def setUp(self):
# #         super().setUp()
# #
# #     def test_error_handler_response(self):
# #         with app.test_client() as client:
# #             http_response = client.post("/api/v1/todos")
# #             auth_status = http_response.get_json()['auth_status']
# #
# #         self.assertEqual(auth_status, "Bad request. No authorization provided")
# #
# #     def tearDown(self):
# #         super().tearDown()
#
#

if __name__ == '__main__':
    unittest.main()
