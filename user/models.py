import datetime
from settings import settings
import neomodel as db
from neomodel.scripts.neomodel_install_labels import load_python_module_or_file
from passlib.handlers.pbkdf2 import pbkdf2_sha256


class User(db.StructuredNode):
    id = db.UniqueIdProperty()
    username = db.StringProperty(max_length=100, unique_index=True, required=True)
    password = db.StringProperty(max_length=255, required=True)
    email = db.EmailProperty(unique_index=True)
    first_name = db.StringProperty(max_length=100, required=False)
    last_name = db.StringProperty(max_length=100, required=False)
    phone = db.IntegerProperty()
    location = db.StringProperty(max_length=100, required=False)
    is_superuser = db.BooleanProperty(default=False)
    is_verified = db.BooleanProperty(default=False)
    created_at = db.DateTimeFormatProperty(default_now=True, format='%Y-%m-%dT%H:%M:%SZ')
    notes = db.RelationshipTo('note.models.Note', 'CREATED_BY')
    collab_notes = db.RelationshipFrom('note.models.Note', 'COLLABORATED_TO')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get('admin_key') == settings.admin_key:
            self.is_superuser = True

    def save_user(self):
        self.password = self.hash_password(self.password)
        return super().save()

    def make_password(self, password):
        self.password = self.hash_password(password)

    def hash_password(self, password):
        return pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    @property
    def to_json(self):
        return {x: y.isoformat() if isinstance(y, datetime.datetime) else y for x, y in self.__dict__.items()}

    def __str__(self):
        return self.username


load_python_module_or_file(__name__)
