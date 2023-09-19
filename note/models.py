import neomodel as db
from datetime import datetime


class Collaborator(db.StructuredRel):
    access_type = db.StringProperty(default='read-only')


class Note(db.StructuredNode):
    id = db.UniqueIdProperty()
    title = db.StringProperty(max_length=100)
    description = db.StringProperty()
    image = db.StringProperty(default=None)
    reminder = db.DateTimeFormatProperty(default=None, format='%Y-%m-%d %H-%M-%S')
    created_at = db.DateTimeFormatProperty(default_now=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = db.DateTimeFormatProperty(format='%Y-%m-%d %H:%M:%S', default=datetime.now())
    user_id = db.StringProperty()
    created_by = db.RelationshipFrom('user.models.User', 'CREATED_BY')
    collaborator = db.RelationshipTo('user.models.User', 'COLLABORATED_TO', model=Collaborator)

    def __str__(self):
        return self.title

    @property
    def to_json(self):
        return {x: y.isoformat() if isinstance(y, datetime) else y for x, y in self.__dict__.items()}
