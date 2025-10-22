from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    애플리케이션 환경 변수 설정

    우선순위:
    1. 시스템 환경 변수 (Docker 컨테이너에서 설정)
    2. .env 파일
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 추가 필드 무시
    )

    # 애플리케이션 기본 설정
    MODE: str
    PROJECT_NAME: str
    APP_TITLE: str
    APP_DESCRIPTION: str
    APP_VERSION: str

    # CORS 설정
    CORS_ORIGINS: str

    # 서버 포트 설정 (uvicorn 실행 시 사용)
    BACKEND_PORT: int
    DEBUG: bool

    # PostgreSQL Database Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int

    # Security Configuration
    SECRET_KEY: str

    # API & Auth Configuration
    API_V1_STR: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # Runtime-managed environment variables (comma separated keys)
    RUNTIME_ENV_KEYS: str = "CORS_ORIGINS,ACCESS_TOKEN_EXPIRE_MINUTES"

    @property
    def DATABASE_URL(self) -> str:
        """
        PostgreSQL 데이터베이스 URL 생성
        """
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """
        CORS origins를 리스트로 변환
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def RUNTIME_ENV_KEYS_LIST(self) -> List[str]:
        """
        런타임에서 DB/Redis로 관리할 환경변수 키 목록 반환
        """
        if not self.RUNTIME_ENV_KEYS:
            return []
        return [
            key.strip()
            for key in self.RUNTIME_ENV_KEYS.split(",")
            if key and key.strip()
        ]


settings = Settings()
