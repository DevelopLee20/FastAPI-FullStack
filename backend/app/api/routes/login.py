from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Message, NewPassword, Token, UserPublic
# 이메일 기능 제거로 인해 주석 처리
# from app.utils import (
#     generate_password_reset_token,
#     generate_reset_password_email,
#     send_email,
#     verify_password_reset_token,
# )

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery - 이메일 기능이 비활성화되었습니다

    비밀번호를 재설정하려면 관리자에게 문의하세요.
    """
    raise HTTPException(
        status_code=501,
        detail="Password recovery via email is disabled. Please contact an administrator to reset your password.",
    )


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password - 이메일 기능이 비활성화되었습니다

    비밀번호를 재설정하려면 관리자에게 문의하세요.
    """
    raise HTTPException(
        status_code=501,
        detail="Password reset via email is disabled. Please contact an administrator to reset your password.",
    )


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery - 이메일 기능이 비활성화되었습니다
    """
    raise HTTPException(
        status_code=501,
        detail="Password recovery via email is disabled.",
    )
