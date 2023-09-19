from sanic import Blueprint, exceptions
from sanic.views import HTTPMethodView
from sanic_ext import validate, openapi
from sanic.response import json
from . import schemas
from .models import Note
from user.models import User
from user.utils import verify_user
from .utils import fetch_note

bp = Blueprint('note')


class NotesAPI(HTTPMethodView):
    decorators = [verify_user]

    @openapi.definition(body={'application/json': schemas.NoteValidator.model_json_schema()}, secured='authorization')
    async def post(self, request):
        serializer = schemas.NoteValidator(**request.json)
        note = Note(user_id=request.ctx.user.id, **serializer.model_dump())
        note.save()
        request.ctx.user.notes.connect(note)
        note = schemas.NoteResponse.model_validate(note).model_dump()
        return json({'message': 'Note created', 'status': 201, 'data': note}, status=201)

    @openapi.definition(secured='authorization')
    async def get(self, request):
        notes = request.ctx.user.notes.all() + request.ctx.user.collab_notes.all()
        notes = [schemas.NoteResponse.model_validate(x).model_dump() for x in notes]
        return json({'message': 'Notes retrieved', 'status': 200, 'data': notes}, status=200)

    @openapi.definition(body={'application/json': schemas.NoteValidator.model_json_schema()},
                        parameter={'name': 'note_id', 'required': True},
                        secured='authorization')
    async def put(self, request):
        serializer = schemas.NoteValidator(**request.json).model_dump()
        note = fetch_note(note_id=request.args.get('note_id'), user=request.ctx.user)
        if not note:
            raise exceptions.NotFound('Note not found')
        [setattr(note, key, value) for key, value in serializer.items()]
        note.save()
        note = schemas.NoteResponse.model_validate(note).model_dump()
        return json({'message': 'Note updated', 'status': 200, 'data': note}, status=200)

    @openapi.definition(parameter={'name': 'note_id', 'required': True}, secured='authorization')
    async def delete(self, request):
        note = Note.nodes.get_or_none(id=request.args.get('note_id'))
        if not note or not request.ctx.user.notes.is_connected(note):
            raise Exception('Note not found')
        note.delete()
        return json({'message': 'Note deleted', 'status': 200}, status=200)


class CollaboratorAPI(HTTPMethodView):
    decorators = [verify_user]

    @openapi.definition(body={'application/json': schemas.Collaborator.model_json_schema()}, secured='authorization')
    def post(self, request):
        serializer = schemas.Collaborator(**request.json)
        note = Note.nodes.get_or_none(id=serializer.note_id)
        if not note or not request.ctx.user.notes.is_connected(note):
            raise Exception('Note not found')
        collaborators = note.collaborator.all()
        for user in serializer.user_id:
            user_obj = User.nodes.get_or_none(id=user)
            if not user_obj:
                raise Exception(f'User {user} not found')
            if user_obj not in collaborators:
                note.collaborator.connect(user_obj, {'access_type': serializer.access_type})
        return json({'message': 'Collaborator added', 'status': 200}, status=200)

    @openapi.definition(body={'application/json': schemas.CollaboratorDelete.model_json_schema()},
                        secured='authorization')
    def delete(self, request):
        serializer = schemas.CollaboratorDelete(**request.json)
        note = Note.nodes.get_or_none(id=serializer.note_id)
        if not note or not request.ctx.user.notes.is_connected(note):
            raise Exception('Note not found')
        for user in serializer.user_id:
            user_obj = User.nodes.get_or_none(id=user)
            if not user_obj:
                raise Exception(f'User {user} not found')
            note.collaborator.disconnect(user_obj)
        return json({'message': 'Collaborator removed', 'status': 200}, status=200)


bp.add_route(NotesAPI.as_view(), '/note')
bp.add_route(CollaboratorAPI.as_view(), '/note/collaborate')
