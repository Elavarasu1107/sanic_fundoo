from note.models import Note
from sanic import exceptions


def fetch_note(note_id, user):
    note = Note.nodes.get_or_none(id=note_id)
    if not note:
        raise exceptions.NotFound('Note not found')
    if not user.notes.is_connected(note) and user not in note.collaborator.match(access_type='read-write').all():
        raise exceptions.Forbidden('Note not found or permission denied')
    return note
