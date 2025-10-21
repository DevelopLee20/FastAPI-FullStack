"""
Pydantic/SQLModel schemas for user operations.
"""
import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(max_length=50)
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    nickname: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    username: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=40)
    email: EmailStr = Field(max_length=255)
    nickname: str = Field(min_length=1, max_length=255)


class UserUpdate(SQLModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    is_active: bool | None = None
    is_superuser: bool | None = None
    nickname: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    nickname: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserPublic(SQLModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    nickname: str | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
