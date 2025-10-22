import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# --- Alembic 설정 --- #

# 프로젝트 루트 경로를 sys.path에 추가하여 'app' 모듈을 임포트할 수 있도록 설정
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# autogenerate를 위해 모든 SQLModel 모델을 임포트해야 합니다.
# 이 임포트문들은 모델이 SQLModel의 메타데이터에 등록되도록 합니다.
from app.models import env_model  # noqa
from app.models import user_model  # noqa

# Alembic Config 객체. alembic.ini 파일의 값에 접근합니다.
config = context.config

# .ini 파일의 로깅 설정을 불러옵니다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 'autogenerate'를 위해 모델의 메타데이터를 Alembic에 알려줍니다.
target_metadata = SQLModel.metadata

# --- 마이그레이션 실행 함수 --- #


def run_migrations_offline() -> None:
    """'offline' 모드에서 마이그레이션을 실행합니다.

    데이터베이스에 연결하지 않고, 변경사항에 대한 SQL 스크립트를 생성합니다.
    주로 데이터베이스 연결이 불가능한 환경에서 사용됩니다.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'online' 모드에서 마이그레이션을 실행합니다.

    데이터베이스에 직접 연결하여 DDL(데이터 정의어) 문을 실행합니다.
    개발 및 배포 환경에서 일반적으로 사용됩니다.
    """
    # .ini 파일의 설정과 sqlalchemy.url을 바탕으로 데이터베이스 엔진을 생성합니다.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# --- 메인 실행 로직 --- #

# 현재 컨텍스트 모드(online/offline)에 따라 적절한 마이그레이션 함수를 실행합니다.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
