import sys
import unittest

from flask import url_for
from peewee import *

# from todos import app
from .todos.models import User, Todo


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
        todo_list = Todo.select()
        print(todo_list)


if __name__ == '__main__':
    print(sys.path)
    # unittest.main()