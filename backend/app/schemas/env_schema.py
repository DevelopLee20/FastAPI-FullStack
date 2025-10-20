"""
Pydantic schemas for Environment Variable API
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EnvVariableBase(BaseModel):
    """환경변수 기본 스키마"""
    key: str = Field(..., min_length=1, max_length=255, description="환경변수 키")
    value: str = Field(..., description="환경변수 값")
    description: Optional[str] = Field(None, description="환경변수 설명")


class EnvVariableCreate(EnvVariableBase):
    """환경변수 생성 요청 스키마"""
    pass


class EnvVariableUpdate(BaseModel):
    """환경변수 수정 요청 스키마"""
    value: Optional[str] = Field(None, description="환경변수 값")
    description: Optional[str] = Field(None, description="환경변수 설명")


class EnvVariableResponse(EnvVariableBase):
    """환경변수 응답 스키마"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnvVariableListResponse(BaseModel):
    """환경변수 목록 응답 스키마"""
    total: int
    items: list[EnvVariableResponse]
