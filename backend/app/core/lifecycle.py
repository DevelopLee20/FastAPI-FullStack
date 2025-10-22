"""
Application Lifecycle Events
앱 시작 및 종료 시 실행되는 이벤트 핸들러
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.logging import setup_logging

from app.db.postgre_db import PostgreDB
from app.db.redis_db import RedisDB
from app.services.env_services.env_variable import EnvVariableService
from app.services.env_services.env_sync import EnvSyncService
from app.core.runtime_env import ensure_core_env_synced

# 로깅 설정
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 앱 생명주기 관리

    Startup:
        1. DB 테이블 초기화
        2. .env 파일 -> PostgreSQL 동기화 (초기 설정)
        3. env.py 핵심 설정 -> PostgreSQL/Redis 동기화
        4. PostgreSQL -> Redis 전체 동기화

    Shutdown:
        1. PostgreSQL -> .env 백업
        2. Redis 연결 종료
        3. DB 연결 종료
    """
    # ==================== STARTUP ====================
    logging.info("=" * 60)
    logging.info("🚀 Application Startup")
    logging.info("=" * 60)

    try:
        # 1. DB 테이블 초기화
        logging.info("\n[1/4] Initializing database tables...")
        PostgreDB.init_db()
        logging.info("✓ Database tables initialized")

        # 2. .env 파일 -> PostgreSQL 동기화
        logging.info("\n[2/4] Syncing .env to PostgreSQL...")
        db = PostgreDB.get_session()
        try:
            env_service = EnvVariableService(db)
            count = env_service.load_from_env_file(".env")
            if count > 0:
                logging.info(f"✓ Synced {count} variables from .env to PostgreSQL")
            else:
                logging.info("ℹ No new variables to sync from .env")
        finally:
            db.close()

        # 3. env.py 설정 -> PostgreSQL/Redis 동기화
        logging.info("\n[3/4] Syncing runtime settings to PostgreSQL & Redis...")
        ensure_core_env_synced(force=True)
        logging.info("✓ Runtime settings synced")

        # 4. PostgreSQL -> Redis 동기화
        logging.info("\n[4/4] Syncing PostgreSQL to Redis...")
        db = PostgreDB.get_session()
        try:
            env_service = EnvVariableService(db)
            synced = env_service.sync_to_redis()
            if synced:
                logging.info("✓ Redis cache refreshed from PostgreSQL")
            else:
                logging.warning("⚠ Redis cache sync skipped or failed")
        finally:
            db.close()

        logging.info("\n" + "=" * 60)
        logging.info("✓ Application startup completed successfully")
        logging.info("=" * 60 + "\n")

    except Exception as e:
        logging.error(f"\n✗ Startup error: {e}", exc_info=True)
        raise

    # 앱 실행
    yield

    # ==================== SHUTDOWN ====================
    logging.info("\n" + "=" * 60)
    logging.info("🛑 Application Shutdown")
    logging.info("=" * 60)

    try:
        # 1. PostgreSQL -> .env 백업
        logging.info("\n[1/3] Backing up PostgreSQL to .env...")
        db = PostgreDB.get_session()
        try:
            env_service = EnvVariableService(db)
            env_dict = env_service.get_all_as_dict()

            if env_dict:
                if EnvSyncService.export_to_env_file(env_dict, ".env", backup=True):
                    logging.info(f"✓ Backed up {len(env_dict)} variables to .env")
                else:
                    logging.error("⚠ Failed to back up variables to .env")
            else:
                logging.info("ℹ No variables to back up")
        finally:
            db.close()

        # 2. Redis 연결 종료
        logging.info("\n[2/3] Closing Redis connection...")
        RedisDB.close()
        logging.info("✓ Redis connection closed")

        # 3. DB 연결 종료
        logging.info("\n[3/3] Closing database connection...")
        PostgreDB.close_db()
        logging.info("✓ Database connection closed")

        logging.info("\n" + "=" * 60)
        logging.info("✓ Application shutdown completed successfully")
        logging.info("=" * 60 + "\n")

    except Exception as e:
        logging.error(f"\n✗ Shutdown error: {e}", exc_info=True)
        # 종료 시에는 에러를 발생시키지 않음
        pass
