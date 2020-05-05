import unittest
import json

from flask import url_for, g
from peewee import *

from app import app
from models import Todo
from config import SECRET_KEY


DATABASE = SqliteDatabase(':memory:')


class ApiTestCase(unittest.TestCase):
    '''Create tables and instantiate database'''

    def setUp(self):

        models = [Todo]

        '''Binds models to test database and creates tables'''
        DATABASE.bind(models)
        DATABASE.create_tables(models, safe=True)

        self.todo_resources = [
            {'name': "Task1"}, {'name': "Task2"}, {'name': "Task3"}
        ]

        with DATABASE.transaction():
            '''Bulk inserts model instances into the database'''
            Todo.insert_many(self.todo_resources).execute()

    def tearDown(self):
        with DATABASE:
            DATABASE.drop_tables([Todo])


class TestPostTodo(ApiTestCase):

    def setUp(self):
        super().setUp()
        self.previous_todo_count = Todo.select().count()

    def test_todo_collection_post_todo_success(self):
        '''Verify that a client receives a 201 status code after
        successfully creating a new Todo.'''

        with app.test_client() as client:
            http_response = client.post(
                "/api/v1/todos/",
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
                json={
                    "name": " ",
                    "user": 1
                }
            )
            invalid_todo = http_response.get_json()['message']
        self.assertEqual(http_response.status_code, 400)
        self.assertEqual(invalid_todo, "Invalid todo name")


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

    def test_put_update_user_todo_success(self):
        with app.test_client() as client:
            http_response = client.put(
                "api/v1/todos/3",
                data={
                    "name": "Quit it!",
                }
            )
        self.assertEqual(http_response.status_code, 204)

    def test_put_update_todo_name_exists_fail(self):
        with app.test_client() as client:
            http_response = client.put(
                "api/v1/todos/3",
                json={
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

    def test_delete_todo_success(self):
        with app.test_client() as client:
            http_response = client.delete("/api/v1/todos/1")
            current_todo_count = Todo.select().count()

        self.assertLess(current_todo_count, self.previous_todo_count)
        self.assertEqual(http_response.status_code, 204)

if __name__ == '__main__':
    unittest.main()
