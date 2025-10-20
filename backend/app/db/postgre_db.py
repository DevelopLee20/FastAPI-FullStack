from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import time

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
    def init_db(cls):
        """
        데이터베이스 초기화 (테이블 생성)
        여러 워커가 동시에 실행될 때 발생하는 중복 생성 문제 방지
        """
        if cls._engine is None:
            cls._init_engine()

        try:
            # TODO: 동시성 처리가 이래도 안된다면 롤백해야 함
            from app.models.env_model import Base

            # checkfirst=True는 기본값이지만, 명시적으로 지정
            # 이미 존재하는 테이블은 건너뛰고 새로운 테이블만 생성
            Base.metadata.create_all(bind=cls._engine, checkfirst=True)
            # TODO: LOG 추가 - print("✓ Database tables created successfully")
        except Exception as e:
            # 동시성 문제로 인한 중복 키 오류는 무시 (테이블이 이미 존재함)
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                # TODO: LOG 추가 - print("ℹ Database tables already exist, skipping creation")
                pass
            else:
                # TODO: LOG 추가 - print(f"❌ Failed to create database tables: {e}")
                raise

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
