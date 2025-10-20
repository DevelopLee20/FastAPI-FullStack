"""
Environment Variable Model for PostgreSQL storage
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EnvVariable(Base):
    """
    환경변수 영속 저장을 위한 PostgreSQL 테이블 모델

    Attributes:
        key: 환경변수 키 (Primary Key)
        value: 환경변수 값
        description: 환경변수 설명 (선택사항)
        created_at: 생성 시각
        updated_at: 마지막 수정 시각
    """
    __tablename__ = "env_variables"

    key = Column(String(255), primary_key=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<EnvVariable(key={self.key}, value={self.value[:20]}...)>"
