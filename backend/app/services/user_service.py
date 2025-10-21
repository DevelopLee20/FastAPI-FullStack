"""
Service layer for user CRUD and authentication helpers.
"""
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def create_user(*, session: Session, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(*, session: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

    @staticmethod
    def get_user_by_username(*, session: Session, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

    @staticmethod
    def authenticate(*, session: Session, username: str, password: str) -> User | None:
        db_user = UserService.get_user_by_username(session=session, username=username)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
