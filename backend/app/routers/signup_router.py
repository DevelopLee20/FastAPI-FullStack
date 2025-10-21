from typing import Any

from fastapi import APIRouter, HTTPException

from app.db.postgre_db import SessionDep
from app.schemas.user_schema import UserCreate, UserPublic, UserRegister
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Public user registration with username, password, email, nickname.
    """
    if UserService.get_user_by_email(session=session, email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    if UserService.get_user_by_username(session=session, username=user_in.username):
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )

    user_create = UserCreate.model_validate(user_in)
    user = UserService.create_user(session=session, user_create=user_create)
    return user
