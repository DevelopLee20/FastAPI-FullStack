"""
Environment Variables API Router
환경변수 CRUD API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgre_db import depend_get_db
from app.schemas.env_schema import (
    EnvVariableCreate,
    EnvVariableUpdate,
    EnvVariableResponse,
    EnvVariableListResponse
)
from app.services.env_services.env_variable import EnvVariableService


router = APIRouter(
    prefix="/api/env",
    tags=["Environment Variables"],
)


def get_env_service(db: Session = Depends(depend_get_db)) -> EnvVariableService:
    """환경변수 서비스 의존성 주입"""
    return EnvVariableService(db)


@router.get(
    "",
    response_model=EnvVariableListResponse,
    summary="모든 환경변수 조회",
    description="모든 환경변수를 조회합니다."
)
async def get_all_env_variables(
    service: EnvVariableService = Depends(get_env_service)
):
    """모든 환경변수 조회"""
    env_vars = service.get_all()
    return EnvVariableListResponse(
        total=len(env_vars),
        items=env_vars
    )


@router.get(
    "/{key}",
    response_model=EnvVariableResponse,
    summary="환경변수 단건 조회",
    description="특정 키의 환경변수를 조회합니다. (Redis 캐시 우선)"
)
async def get_env_variable(
    key: str,
    service: EnvVariableService = Depends(get_env_service)
):
    """환경변수 조회"""
    env_var = service.get(key)

    if not env_var:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment variable '{key}' not found"
        )

    return env_var


@router.post(
    "",
    response_model=EnvVariableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환경변수 생성",
    description="새로운 환경변수를 생성합니다. (DB 저장 + Redis 캐시)"
)
async def create_env_variable(
    env_create: EnvVariableCreate,
    service: EnvVariableService = Depends(get_env_service)
):
    """환경변수 생성"""
    try:
        env_var = service.create(env_create)
        return env_var
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{key}",
    response_model=EnvVariableResponse,
    summary="환경변수 수정",
    description="기존 환경변수를 수정합니다. (DB 업데이트 + Redis 캐시 갱신)"
)
async def update_env_variable(
    key: str,
    env_update: EnvVariableUpdate,
    service: EnvVariableService = Depends(get_env_service)
):
    """환경변수 수정"""
    try:
        env_var = service.update(key, env_update)

        if not env_var:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Environment variable '{key}' not found"
            )

        return env_var
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="환경변수 삭제",
    description="환경변수를 삭제합니다. (DB 삭제 + Redis 캐시 제거)"
)
async def delete_env_variable(
    key: str,
    service: EnvVariableService = Depends(get_env_service)
):
    """환경변수 삭제"""
    try:
        success = service.delete(key)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Environment variable '{key}' not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/sync/db-to-redis",
    status_code=status.HTTP_200_OK,
    summary="DB → Redis 동기화",
    description="DB의 모든 환경변수를 Redis로 동기화합니다."
)
async def sync_db_to_redis(
    service: EnvVariableService = Depends(get_env_service)
):
    """DB → Redis 동기화"""
    success = service.sync_to_redis()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync environment variables to Redis"
        )

    return {"message": "Environment variables synced to Redis successfully"}


@router.post(
    "/load/from-env-file",
    status_code=status.HTTP_200_OK,
    summary=".env 파일 로드",
    description=".env 파일에서 환경변수를 로드하여 DB에 저장합니다."
)
async def load_from_env_file(
    service: EnvVariableService = Depends(get_env_service)
):
    """env 파일에서 로드"""
    count = service.load_from_env_file(".env")

    return {
        "message": f"Loaded {count} environment variables from .env file",
        "count": count
    }
