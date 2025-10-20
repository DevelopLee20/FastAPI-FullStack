"""
FastAPI Main Application
환경변수 관리 시스템 통합
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.env import settings
from app.core.lifecycle import lifespan
from app.routers import env_router


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록
app.include_router(env_router.router)


# Health Check 엔드포인트
@app.get("/health", tags=["Health"])
async def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "mode": settings.MODE
    }


@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": f"{settings.APP_TITLE} - Environment Variable Management",
        "docs": "/docs",
        "health": "/health",
        "env_api": "/api/env"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
