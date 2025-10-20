"""
Application Lifecycle Events
앱 시작 및 종료 시 실행되는 이벤트 핸들러
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.postgre_db import PostgreDB
from app.db.redis_db import RedisDB
from app.services.env_services.env_variable import EnvVariableService
from app.services.env_services.env_sync import EnvSyncService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 앱 생명주기 관리

    Startup:
        1. DB 테이블 초기화
        2. .env 파일에서 환경변수 로드 (초기 설정)
        3. DB → Redis 동기화

    Shutdown:
        1. DB → .env 백업
        2. Redis 연결 종료
        3. DB 연결 종료
    """
    # ==================== STARTUP ====================
    # TODO: LOG 추가 - print("=" * 60)
    # TODO: LOG 추가 - print("🚀 Application Startup")
    # TODO: LOG 추가 - print("=" * 60)

    try:
        # 1. DB 테이블 초기화
        # TODO: LOG 추가 - print("\n[1/3] Initializing database tables...")
        PostgreDB.init_db()
        # TODO: LOG 추가 - print("✓ Database tables initialized")

        # 2. .env 파일에서 환경변수 로드 (초기 설정용)
        # TODO: LOG 추가 - print("\n[2/3] Loading initial environment variables from .env...")
        db = PostgreDB.get_session()
        try:
            env_service = EnvVariableService(db)
            count = env_service.load_from_env_file(".env")
            if count > 0:
                # TODO: LOG 추가 - print(f"✓ Loaded {count} environment variables from .env")
                pass
            else:
                # TODO: LOG 추가 - print("ℹ No new environment variables loaded from .env")
                pass
        finally:
            db.close()

        # 3. DB → Redis 동기화
        # TODO: LOG 추가 - print("\n[3/3] Syncing environment variables from DB to Redis...")
        db = PostgreDB.get_session()
        try:
            env_service = EnvVariableService(db)
            if env_service.sync_to_redis():
                env_count = len(env_service.get_all())
                # TODO: LOG 추가 - print(f"✓ Synced {env_count} environment variables to Redis cache")
            else:
                # TODO: LOG 추가 - print("⚠ Failed to sync environment variables to Redis")
                pass
        finally:
            db.close()

        # TODO: LOG 추가 - print("\n" + "=" * 60)
        # TODO: LOG 추가 - print("✓ Application startup completed successfully")
        # TODO: LOG 추가 - print("=" * 60 + "\n")

    except Exception as e:
        # TODO: LOG 추가 - print(f"\n✗ Startup error: {e}")
        raise

    # 앱 실행
    yield

    # ==================== SHUTDOWN ====================
    # TODO: LOG 추가 - print("\n" + "=" * 60)
    # TODO: LOG 추가 - print("🛑 Application Shutdown")
    # TODO: LOG 추가 - print("=" * 60)

    try:
        # 1. DB → .env 백업
        # TODO: LOG 추가 - print("\n[1/3] Backing up environment variables to .env...")
        db = PostgreDB.SessionLocal()
        try:
            env_service = EnvVariableService(db)
            env_dict = env_service.get_all_as_dict()

            if env_dict:
                if EnvSyncService.export_to_env_file(env_dict, ".env", backup=True):
                    # TODO: LOG 추가 - print(f"✓ Exported {len(env_dict)} environment variables to .env")
                    pass
                else:
                    # TODO: LOG 추가 - print("⚠ Failed to export environment variables to .env")
                    pass
            else:
                # TODO: LOG 추가 - print("ℹ No environment variables to export")
                pass
        finally:
            db.close()

        # 2. Redis 연결 종료
        # TODO: LOG 추가 - print("\n[2/3] Closing Redis connection...")
        RedisDB.close()
        # TODO: LOG 추가 - print("✓ Redis connection closed")

        # 3. DB 연결 종료
        # TODO: LOG 추가 - print("\n[3/3] Closing database connection...")
        PostgreDB.close_db()
        # TODO: LOG 추가 - print("✓ Database connection closed")

        # TODO: LOG 추가 - print("\n" + "=" * 60)
        # TODO: LOG 추가 - print("✓ Application shutdown completed successfully")
        # TODO: LOG 추가 - print("=" * 60 + "\n")

    except Exception as e:
        # TODO: LOG 추가 - print(f"\n✗ Shutdown error: {e}")
        # 종료 시에는 에러를 발생시키지 않음
        pass
