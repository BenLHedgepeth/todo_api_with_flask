import datetime

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *


DATABASE = SqliteDatabase(None)

class AbstractModel(Model):
    class Meta:
        database = DATABASE

class Todo(AbstractModel):
    name = CharField(unique=True)

    def __str__(self):
        return self.name
        

class User(AbstractModel):
    username = CharField(unique=True)
    password = CharField()
    todos = ForeignKeyField(Todo, related_name="todos")

    def __str__(self):
        return self.username


def initialize(*args, **kwargs):
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([*args], safe=True)
    DATABASE.close()
