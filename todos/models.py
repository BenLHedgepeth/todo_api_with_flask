import datetime

from flask import url_for

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *
from argon2 import PasswordHasher

from config import SECRET_KEY

DATABASE = SqliteDatabase(None)


class _Model(Model):
    class Meta:
        database = DATABASE


class Todo(_Model):
    name = CharField(unique=True)

    def __str__(self):
        return url_for('resources.todos.todo', id=self.id)


def initialize(*args, **kwargs):
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([*args], safe=True)
    DATABASE.close()
