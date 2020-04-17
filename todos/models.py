import datetime

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *


DATABASE = SqliteDatabase(None)

class _Model(Model):
    class Meta:
        database = DATABASE


class User(_Model):
    username = CharField(unique=True)
    password = CharField()

    def __str__(self):
        return self.username


class Todo(_Model):
    name = CharField(unique=True)
    user = ForeignKeyField(User, related_name="todos")

    def __str__(self):
        return self.name



def initialize(*args, **kwargs):
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([*args], safe=True)
    DATABASE.close()
