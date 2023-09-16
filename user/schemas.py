from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserRequest(BaseModel):
    username: str = Field(max_length=100, pattern='^[A-Za-z0-9]{4,}$')
    password: str = Field(max_length=255)
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone: int
    location: str
    admin_key: str = None


class UserLogin(BaseModel):
    username: str = Field(max_length=100, pattern='^[A-Za-z0-9]{4,}$')
    password: str = Field(max_length=255)


class ResetPassword(BaseModel):
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
