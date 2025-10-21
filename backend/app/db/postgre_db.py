from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlmodel import SQLModel, select
from typing import Annotated, Generator
import time
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from pydantic import ValidationError

from app.core.env import settings


class PostgreDB:
    """
    PostgreSQL 데이터베이스 매니저 클래스
    - 엔진 및 세션풀 관리
    - FastAPI 의존성 주입용 메서드 제공
    - 재시도 로직 포함
    """

    _engine = None
    _SessionLocal = None
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    @classmethod
    def _init_engine(cls):
        """SQLAlchemy 엔진 초기화 (재시도 로직 포함)"""
        if cls._engine is None:
            database_url = settings.DATABASE_URL

            for attempt in range(1, cls.MAX_RETRIES + 1):
                try:
                    cls._engine = create_engine(
                        database_url,
                        poolclass=QueuePool,
                        pool_size=5,
                        max_overflow=10,
                        pool_pre_ping=True,
                        echo=getattr(settings, "DEBUG", False),
                    )

                    # 연결 테스트
                    with cls._engine.connect() as conn:
                        conn.execute(text("SELECT 1"))

                    cls._SessionLocal = sessionmaker(
                        autocommit=False,
                        autoflush=False,
                        bind=cls._engine,
                    )
                    # TODO: LOG 추가 - print("✓ PostgreSQL 엔진 초기화 완료")
                    return

                except Exception:
                    # TODO: LOG 추가 - print(f"⚠ PostgreSQL connection attempt {attempt}/{cls.MAX_RETRIES} failed: {e}")
                    if attempt < cls.MAX_RETRIES:
                        # TODO: LOG 추가 - print(f"   Retrying in {cls.RETRY_DELAY} seconds...")
                        time.sleep(cls.RETRY_DELAY)
                    else:
                        # TODO: LOG 추가 - print(f"❌ PostgreSQL connection failed after {cls.MAX_RETRIES} attempts")
                        raise

    @classmethod
    def get_db(cls) -> Generator[Session, None, None]:
        """
        FastAPI 의존성 주입용 DB 세션 생성기
        """
        if cls._SessionLocal is None:
            cls._init_engine()
        db = cls._SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @classmethod
    def get_session(cls) -> Session:
        """
        FastAPI 의존성 주입용 DB 세션 생성기
        """
        if cls._SessionLocal is None:
            cls._init_engine()
        return cls._SessionLocal()

    @classmethod
    def init_db(cls, session: Session | None = None):
        """
        데이터베이스 초기화 (테이블 생성 및 초기 superuser 생성)
        여러 워커가 동시에 실행될 때 발생하는 중복 생성 문제 방지
        """
        if cls._engine is None:
            cls._init_engine()

        try:
            # SQLModel 테이블 생성 (User 등)
            SQLModel.metadata.create_all(bind=cls._engine, checkfirst=True)

            # TODO: 동시성 처리가 이래도 안된다면 롤백해야 함
            from app.models.env_model import Base

            # checkfirst=True는 기본값이지만, 명시적으로 지정
            # 이미 존재하는 테이블은 건너뛰고 새로운 테이블만 생성
            Base.metadata.create_all(bind=cls._engine, checkfirst=True)
            # TODO: LOG 추가 - print("✓ Database tables created successfully")

            # 초기 superuser 생성
            cls._create_initial_superuser(session)

        except Exception as e:
            # 동시성 문제로 인한 중복 키 오류는 무시 (테이블이 이미 존재함)
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                # TODO: LOG 추가 - print("ℹ Database tables already exist, skipping creation")
                pass
            else:
                # TODO: LOG 추가 - print(f"❌ Failed to create database tables: {e}")
                raise

    @classmethod
    def _create_initial_superuser(cls, session: Session | None = None):
        """
        초기 superuser 생성
        """
        from app.models.user_model import User
        from app.schemas.user_schema import UserCreate
        from app.services.user_service import UserService

        should_close = False
        if session is None:
            session = cls.get_session()
            should_close = True

        try:
            user = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
            if not user:
                user_in = UserCreate(
                    username=settings.FIRST_SUPERUSER,
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                    is_active=True,
                    nickname="Administrator",
                )
                UserService.create_user(session=session, user_create=user_in)
                # TODO: LOG 추가 - print("✓ Initial superuser created")
        finally:
            if should_close:
                session.close()

    @classmethod
    def close_db(cls):
        """
        데이터베이스 연결 종료
        """
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._SessionLocal = None
            # TODO: LOG 추가 - print("✓ Database connection closed")


# FastAPI 의존성 주입용 헬퍼
def depend_get_db() -> Generator[Session, None, None]:
    yield from PostgreDB.get_db()


# OAuth2 토큰 URL 설정
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# 타입 어노테이션
SessionDep = Annotated[Session, Depends(depend_get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep):
    """현재 인증된 사용자 반환"""
    from app.core import security
    from app.models.user_model import User
    from app.schemas.user_schema import TokenPayload

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_current_active_superuser(current_user: Annotated[object, Depends(get_current_user)]):
    """현재 슈퍼유저 권한 확인"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# 타입 어노테이션 (라우터에서 import해서 사용)
# Note: User 타입은 순환 import 방지를 위해 Any로 선언하고, 런타임에는 User 객체가 반환됨
from typing import Any
CurrentUser = Annotated[Any, Depends(get_current_user)]
