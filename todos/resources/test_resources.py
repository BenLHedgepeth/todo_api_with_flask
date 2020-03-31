import sys
import unittest

from os.path import abspath, dirname

from flask import url_for
from peewee import *

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from todos import models






test_db = SqliteDatabase(":memory:")

class ApiTestCaseSetup(unittest.TestCase):

    def setUp(self):

        models = [User, Todo]
        todo_resources = [
            {'name': "Task1"},
            {'name': "Task2"},
            {'name': "Task3"}
        ]
        with test_db:
            '''Binds models to test database and creates tables'''
            test_db.bind(models)
            test_db.create_tables(models)

            with tb.transaction():
                '''Bulk inserts model instances into the database'''
                Todo.insert_many(todo_resources).execute()


    def tearDown(self):
        with test_db:
            test_db.drop_tables()


class TestTodoCollection(ApiTestCaseSetup):

    def setUp(self):
        super().setUp()

    def test_todo_collection_resource(self):
        pass


if __name__ == '__main__':
    print(todos.app.app)
    # print(Todo.select())
    # unittest.main()