import redis
import time

from app.core.env import settings


class RedisDB:
    # Redis 싱글톤 객체
    _instance = None
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """
        Redis 클라이언트 인스턴스 반환 (싱글톤, 재시도 로직 포함)
        """
        if cls._instance is None:
            for attempt in range(1, cls.MAX_RETRIES + 1):
                try:
                    cls._instance = redis.Redis(
                        host=settings.REDIS_HOST
                        if hasattr(settings, "REDIS_HOST")
                        else "redis",
                        port=settings.REDIS_PORT,
                        db=0,  # 환경변수 전용 DB
                        decode_responses=True,  # 문자열 자동 디코딩
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        health_check_interval=30,
                    )

                    # 연결 테스트
                    cls._instance.ping()
                    # TODO: LOG 추가(클라이언트 연결 성공)
                    return cls._instance

                except Exception:
                    # TODO: LOG 추가 - print(f"⚠ Redis connection attempt {attempt}/{cls.MAX_RETRIES} failed: {e}")
                    cls._instance = None
                    if attempt < cls.MAX_RETRIES:
                        # TODO: LOG 추가 - print(f"   Retrying in {cls.RETRY_DELAY} seconds...")
                        time.sleep(cls.RETRY_DELAY)
                    else:
                        # TODO: LOG 추가 - print(f"❌ Redis connection failed after {cls.MAX_RETRIES} attempts")
                        raise

        return cls._instance

    @classmethod
    def close(cls):
        """
        Redis 연결 종료
        """
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            # TODO: LOG 추가, ✓ Redis 클라이언트 연결 종료

    @classmethod
    def test_connection(cls) -> bool:
        """
        Redis 연결 테스트
        """
        try:
            client = cls.get_client()
            client.ping()
            # TODO: print("✓ Redis 연결 테스트 성공")
            return True
        except Exception:
            # TODO: print(f"✗ Redis 연결 테스트 실패: {e}")
            return False


# 전역 Redis 의존성 주입용 인스턴스 반환 함수
def depend_get_instance() -> redis.Redis:
    return RedisDB.get_instance()
