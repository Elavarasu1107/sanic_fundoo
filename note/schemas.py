from pydantic import BaseModel, Field, Extra, ConfigDict, field_validator
from typing import Optional, Union, Annotated, List
from datetime import datetime
from pydantic.functional_serializers import field_serializer


class NoteValidator(BaseModel):
    title: str
    description: str
    image: Optional[str] = Field(default=None)
    reminder: Optional[datetime] = Field(default=None)

    class Config:
        from_attributes = True


class CollaboratorDelete(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    note_id: str
    user_id: List[str]


class Collaborator(CollaboratorDelete):
    access_type: str = 'read-only'


class NoteResponse(NoteValidator):
    id: str
    reminder: datetime | None
    created_at: datetime
    updated_at: datetime
    user_id: str

    @field_serializer('reminder', 'created_at', 'updated_at')
    def dt_validate(self, value, _info):
        if value:
            return value.isoformat()
        return value
