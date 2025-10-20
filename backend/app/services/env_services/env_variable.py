"""
Environment Variable Database Service
PostgreSQL을 이용한 환경변수 CRUD 작업 및 Redis 캐시 연동
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.env_model import EnvVariable
from app.schemas.env_schema import EnvVariableCreate, EnvVariableUpdate
from app.services.env_services.env_cache import EnvCacheService


class EnvVariableService:
    """
    환경변수 DB 서비스

    PostgreSQL을 영속 저장소로 사용하며,
    Redis 캐시와 자동 동기화
    """

    def __init__(self, db: Session):
        self.db = db
        self.cache = EnvCacheService()

    def get(self, key: str) -> Optional[EnvVariable]:
        """
        환경변수 조회 (캐시 우선)

        Args:
            key: 환경변수 키

        Returns:
            EnvVariable 객체 또는 None
        """
        # 1차: Redis 캐시에서 조회
        cached_value = self.cache.get(key)
        if cached_value is not None:
            # 캐시 히트 - DB 객체 조회 (메타데이터 포함)
            return self.db.query(EnvVariable).filter(EnvVariable.key == key).first()

        # 2차: DB에서 조회
        env_var = self.db.query(EnvVariable).filter(EnvVariable.key == key).first()

        # DB에 있으면 캐시에 저장
        if env_var:
            self.cache.set(env_var.key, env_var.value)

        return env_var

    def get_all(self) -> list[EnvVariable]:
        """
        모든 환경변수 조회

        Returns:
            EnvVariable 리스트
        """
        return self.db.query(EnvVariable).all()

    def create(self, env_create: EnvVariableCreate) -> EnvVariable:
        """
        환경변수 생성

        Args:
            env_create: 생성할 환경변수 데이터

        Returns:
            생성된 EnvVariable 객체

        Raises:
            ValueError: 이미 존재하는 키인 경우
        """
        # 중복 확인
        existing = self.db.query(EnvVariable).filter(
            EnvVariable.key == env_create.key
        ).first()

        if existing:
            raise ValueError(f"Environment variable '{env_create.key}' already exists")

        # DB에 저장
        env_var = EnvVariable(
            key=env_create.key,
            value=env_create.value,
            description=env_create.description
        )

        try:
            self.db.add(env_var)
            self.db.commit()
            self.db.refresh(env_var)

            # Redis 캐시에 저장
            self.cache.set(env_var.key, env_var.value)

            return env_var

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create environment variable: {str(e)}")

    def update(self, key: str, env_update: EnvVariableUpdate) -> Optional[EnvVariable]:
        """
        환경변수 수정

        Args:
            key: 수정할 환경변수 키
            env_update: 수정 데이터

        Returns:
            수정된 EnvVariable 객체 또는 None
        """
        env_var = self.db.query(EnvVariable).filter(EnvVariable.key == key).first()

        if not env_var:
            return None

        # 수정 적용
        if env_update.value is not None:
            env_var.value = env_update.value
        if env_update.description is not None:
            env_var.description = env_update.description

        try:
            self.db.commit()
            self.db.refresh(env_var)

            # Redis 캐시 갱신
            self.cache.set(env_var.key, env_var.value)

            return env_var

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update environment variable: {str(e)}")

    def delete(self, key: str) -> bool:
        """
        환경변수 삭제

        Args:
            key: 삭제할 환경변수 키

        Returns:
            삭제 성공 여부
        """
        env_var = self.db.query(EnvVariable).filter(EnvVariable.key == key).first()

        if not env_var:
            return False

        try:
            self.db.delete(env_var)
            self.db.commit()

            # Redis 캐시에서 삭제
            self.cache.delete(key)

            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete environment variable: {str(e)}")

    def get_all_as_dict(self) -> dict[str, str]:
        """
        모든 환경변수를 딕셔너리로 조회

        Returns:
            환경변수 딕셔너리 {key: value}
        """
        env_vars = self.get_all()
        return {env.key: env.value for env in env_vars}

    def load_from_env_file(self, env_file_path: str = ".env") -> int:
        """
        .env 파일에서 환경변수 로드하여 DB에 저장

        Args:
            env_file_path: .env 파일 경로

        Returns:
            로드된 환경변수 개수
        """
        import os
        from dotenv import dotenv_values

        if not os.path.exists(env_file_path):
            # TODO: LOG 추가 - print(f"Warning: {env_file_path} not found")
            return 0

        env_dict = dotenv_values(env_file_path)
        count = 0

        for key, value in env_dict.items():
            if not value:  # 빈 값 무시
                continue

            # 이미 존재하는지 확인
            existing = self.db.query(EnvVariable).filter(
                EnvVariable.key == key
            ).first()

            if not existing:
                env_var = EnvVariable(key=key, value=value)
                self.db.add(env_var)
                count += 1

        try:
            self.db.commit()
            # TODO: LOG 추가 - print(f"Loaded {count} environment variables from {env_file_path}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            # TODO: LOG 추가 - print(f"Failed to load environment variables: {e}")
            return 0

    def sync_to_redis(self) -> bool:
        """
        DB의 모든 환경변수를 Redis로 동기화

        Returns:
            성공 여부
        """
        env_dict = self.get_all_as_dict()
        return self.cache.sync_from_db(env_dict)
