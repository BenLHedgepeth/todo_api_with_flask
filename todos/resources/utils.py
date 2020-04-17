from flask import url_for
from models import Todo, User

def set_todo_creator(todo):
    creator = User.select().join(Todo).where(User.id==todo.user.id).get()
    todo.created_by = url_for('resources.users.user', id=creator.id)
    return todo
