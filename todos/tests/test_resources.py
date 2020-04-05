import sys
import unittest

from flask import url_for
from peewee import *

from app import app
from models import User, Todo

DATABASE = SqliteDatabase(':memory:')

class ApiTestCaseSetup(unittest.TestCase):

    def setUp(self):

        models = [User, Todo]
        self.todo_resources = [
            {'name': "Task1"},
            {'name': "Task2"},
            {'name': "Task3"}
        ]

        '''Binds models to test database and creates tables'''
        DATABASE.bind(models)
        DATABASE.create_tables(models, safe=True)

        with DATABASE.transaction():
            '''Bulk inserts model instances into the database'''
            Todo.insert_many(self.todo_resources).execute()


    def tearDown(self):
        with DATABASE:
            DATABASE.drop_tables([User, Todo])


class TestTodoCollection(ApiTestCaseSetup):

    def setUp(self):
        super().setUp()

    def test_todo_collection_resource(self):
        with app.test_client() as client:
            http_response = client.get("/api/v1/todos/")
            json_data = http_response.get_json()

        self.assertEqual(http_response.status_code, 200)
        self.assertTrue(http_response.is_json)
        self.assertTrue(all(
            (instance['name'] in self.todo_resources.values()
                for instance in json_data)
        ))

        def tearDown(self):
            super().tearDown()



if __name__ == '__main__':
    unittest.main()