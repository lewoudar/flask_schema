from dataclasses import dataclass
from typing import Optional

from flask import Flask, make_response
from flask.views import MethodView
from sqlalchemy import select

from flask_schema.db import Todo, db
from flask_schema.schemas import TodoInputSchema, TodoOutputSchema, TodoUpdateSchema
from flask_schema.validation import (
    RequestSchemaValidationError,
    ResponseSchemaValidationError,
    validate_querystring,
    validate_request,
    validate_response,
)

app = Flask(__name__)

db.drop_all()
db.create_all()


@app.errorhandler(404)
def not_found(error):
    return {'detail': 'Not Found'}, 404


@app.errorhandler(ResponseSchemaValidationError)
def handle_response_error(error: ResponseSchemaValidationError) -> tuple[dict, int]:
    return {'detail': error.validation_error.errors()}, 400


@app.errorhandler(RequestSchemaValidationError)
def handle_request_error(error: RequestSchemaValidationError) -> tuple[dict, int]:
    return {'detail': error.validation_error.errors()}, 400


@dataclass
class TodoFilter:
    done: Optional[bool] = None


class TodoAPI(MethodView):
    def _get_or_not_found(self, session: db.Session, todo_id) -> dict:
        todo = session.get(Todo, todo_id)
        if todo is None:
            return {'detail': f'Todo with id {todo_id} was not found'}
        return todo.to_dict()

    @validate_querystring(TodoFilter)
    def get(self, todo_id: int | None, query_args: TodoFilter):
        with db.Session() as session:
            if todo_id is not None:
                return self._get_or_not_found(session, todo_id)
            query = select(Todo)
            if query_args.done is not None:
                query = query.where(Todo.done.is_(query_args.done))
            todos = session.scalars(query)
            return [todo.to_dict() for todo in todos]

    @validate_request(TodoInputSchema)
    @validate_response(TodoOutputSchema, 201)
    def post(self, data: TodoInputSchema):
        with db.begin() as session:
            todo = Todo(**data.model_dump())
            session.add(todo)
            session.flush()
            return todo.to_dict(), 201

    @validate_request(TodoUpdateSchema)
    @validate_response(TodoOutputSchema)
    def patch(self, todo_id: int, data: TodoUpdateSchema):
        with db.begin() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return {'detail': f'Todo with id {todo_id} was not found'}
            for key, value in data.model_dump(exclude_none=True).items():
                setattr(todo, key, value)
            session.flush()
            return todo.to_dict()

    def delete(self, todo_id: int):
        with db.begin() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return {'detail': f'Todo with id {todo_id} was not found'}
            session.delete(todo)
            return make_response('', 204)


todo_view = TodoAPI.as_view('todo_api')
app.add_url_rule(
    '/todos/', defaults={'todo_id': None}, view_func=todo_view, methods=['GET']
)
app.add_url_rule('/todos/', view_func=todo_view, methods=['POST'])
app.add_url_rule(
    '/todos/<int:todo_id>/', view_func=todo_view, methods=['GET', 'PATCH', 'DELETE']
)
