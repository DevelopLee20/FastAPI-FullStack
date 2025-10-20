"""
Redis Cache Manager for Environment Variables
"""
import json
from typing import Optional, Dict, List
import redis
from app.db.redis_db import RedisDB


class EnvCacheService:
    """
    환경변수 Redis 캐시 관리 서비스

    Redis를 1차 캐시로 사용하여 환경변수 조회 성능 최적화
    """

    # Redis 키 prefix
    ENV_PREFIX = "env:"
    ENV_ALL_KEY = "env:all"

    def __init__(self):
        self.redis_client: redis.Redis = RedisDB.get_instance()

    def _make_key(self, key: str) -> str:
        """Redis 키 생성"""
        return f"{self.ENV_PREFIX}{key}"

    def get(self, key: str) -> Optional[str]:
        """
        환경변수 조회 (Redis 캐시에서)

        Args:
            key: 환경변수 키

        Returns:
            환경변수 값 또는 None
        """
        try:
            redis_key = self._make_key(key)
            value = self.redis_client.get(redis_key)
            return value
        except redis.RedisError as e:
            # Redis 오류 시 None 반환 (DB에서 조회하도록)
            # TODO: LOG 추가 - print(f"Redis get error for key {key}: {e}")
            return None

    def get_all(self) -> Dict[str, str]:
        """
        모든 환경변수 조회 (Redis 캐시에서)

        Returns:
            환경변수 딕셔너리
        """
        try:
            # Pattern matching으로 모든 env: 키 조회
            pattern = f"{self.ENV_PREFIX}*"
            keys = self.redis_client.keys(pattern)

            result = {}
            for redis_key in keys:
                # env: prefix 제거
                key = redis_key.replace(self.ENV_PREFIX, "")
                value = self.redis_client.get(redis_key)
                if value:
                    result[key] = value

            return result
        except redis.RedisError as e:
            # TODO: LOG 추가 - print(f"Redis get_all error: {e}")
            return {}

    def set(self, key: str, value: str) -> bool:
        """
        환경변수 캐시 저장/갱신

        Args:
            key: 환경변수 키
            value: 환경변수 값

        Returns:
            성공 여부
        """
        try:
            redis_key = self._make_key(key)
            self.redis_client.set(redis_key, value)
            return True
        except redis.RedisError as e:
            # TODO: LOG 추가 - print(f"Redis set error for key {key}: {e}")
            return False

    def set_many(self, env_dict: Dict[str, str]) -> bool:
        """
        여러 환경변수 일괄 캐시 저장

        Args:
            env_dict: 환경변수 딕셔너리

        Returns:
            성공 여부
        """
        try:
            pipeline = self.redis_client.pipeline()
            for key, value in env_dict.items():
                redis_key = self._make_key(key)
                pipeline.set(redis_key, value)
            pipeline.execute()
            return True
        except redis.RedisError as e:
            # TODO: LOG 추가 - print(f"Redis set_many error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        환경변수 캐시 삭제

        Args:
            key: 환경변수 키

        Returns:
            성공 여부
        """
        try:
            redis_key = self._make_key(key)
            self.redis_client.delete(redis_key)
            return True
        except redis.RedisError as e:
            # TODO: LOG 추가 - print(f"Redis delete error for key {key}: {e}")
            return False

    def clear_all(self) -> bool:
        """
        모든 환경변수 캐시 삭제

        Returns:
            성공 여부
        """
        try:
            pattern = f"{self.ENV_PREFIX}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except redis.RedisError as e:
            # TODO: LOG 추가 - print(f"Redis clear_all error: {e}")
            return False

    def sync_from_db(self, env_dict: Dict[str, str]) -> bool:
        """
        DB의 환경변수를 Redis로 동기화 (앱 시작 시)

        Args:
            env_dict: DB에서 조회한 환경변수 딕셔너리

        Returns:
            성공 여부
        """
        try:
            # 기존 캐시 삭제
            self.clear_all()
            # 새로운 데이터 일괄 저장
            return self.set_many(env_dict)
        except Exception as e:
            # TODO: LOG 추가 - print(f"Redis sync_from_db error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        환경변수 존재 여부 확인

        Args:
            key: 환경변수 키

        Returns:
            존재 여부
        """
        try:
            redis_key = self._make_key(key)
            return self.redis_client.exists(redis_key) > 0
        except redis.RedisError as e:
            # TODO: LOG 추가 - print(f"Redis exists error for key {key}: {e}")
            return False
