from flask import url_for
from models import Todo, User

def set_todo_creator(todo):
    creator = todo.user
    todo.created_by = url_for('resources.users.user', id=creator.id)
    return todo


def set_todos(user):
    todos = Todo.select().join(User).where(User.id == user.id)
    user.todos_created = [url_for('resources.todos.todo', id=todo.id) for todo in todos]
    return user
