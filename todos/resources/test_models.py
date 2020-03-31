import unittest

from peewee import *

from models import Todo, User

DATABASE = SqliteDatabase(":memory:")

class SetupApiModels(unittest.TestCase):

    def setUp(self):

        models = [User, Todo]

        with test_database:
            test_database.bind(models)
            test_database.create_tables(models)

