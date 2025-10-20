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
        extra="ignore"  # 추가 필드 무시
    )
    # 애플리케이션 기본 설정
    MODE: str
    PROJECT_NAME: str
    APP_TITLE: str
    APP_DESCRIPTION: str
    APP_VERSION: str

    # CORS 설정
    CORS_ORIGINS: str = "*"
    ALLOWED_HOSTS: str = "*"

    # 서버 포트 설정
    WEB_PORT: int = 8000
    DOCKER_PORT: int = 8000
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000

    # Gunicorn 설정
    TIMEOUT: int = 120
    KEEP_ALIVE: int = 5
    WORKERS: int = 1

    # PostgreSQL Database Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""  # 빈 문자열이면 비밀번호 없음

    # Backend Configuration
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    SECRET_KEY: str

    # Frontend Configuration
    REACT_APP_API_URL: str = "http://localhost:8000"
    NODE_ENV: str = "development"
    
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
    
settings = Settings()