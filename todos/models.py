import datetime

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *
from argon2 import PasswordHasher

from config import SECRET_KEY

from exceptions import PasswordMatchError

DATABASE = SqliteDatabase(None)
ph = PasswordHasher()

class _Model(Model):
    class Meta:
        database = DATABASE


class User(_Model):
    username = CharField(unique=True)
    password = CharField()

    def __str__(self):
        return self.username

    @staticmethod
    def set_password(password):
        return ph.hash(password)

    def check_password(self, password):
        return ph.verify(self.password, password)

    def request_token(self):
        token_serializer = Serializer(SECRET_KEY)
        return token_serializer.dumps({'id': self.id}).decode()


    @classmethod
    def create_user(cls, *args, **kwargs):
        if kwargs['password'] != kwargs['verify_password']:
            raise PasswordMatchError("Verification failed. Try again.")
        else:
            if not kwargs['username']:
                raise ValueError("No username provided")
            try:
                username_taken = cls.get(cls.username == kwargs['username'])
            except cls.DoesNotExist:
                user = cls.create(
                    username= kwargs['username'],
                    password = cls.set_password(kwargs['password'])
                )
                return user
            else:
                return False


class Todo(_Model):
    name = CharField(unique=True)
    user = ForeignKeyField(User, related_name="todos")

    def __str__(self):
        return self.name

    @property
    def location(self):
        return f'http://localhost/api/v1/todos/{self.id}'

def initialize(*args, **kwargs):
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([*args], safe=True)
    DATABASE.close()
