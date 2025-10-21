"""
FastAPI Main Application
환경변수 및 인증 기능 통합
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.env import settings
from app.core.lifecycle import lifespan
from app.routers import env_router
from app.routers import login_router
from app.routers import signup_router
from app.routers import user_router


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(env_router.router)
app.include_router(login_router.router, prefix=settings.API_V1_STR)
app.include_router(signup_router.router, prefix=settings.API_V1_STR)
app.include_router(user_router.router, prefix=settings.API_V1_STR)


# Health Check 엔드포인트
@app.get("/health", tags=["Health"])
async def health_check():
    """서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "mode": settings.MODE,
    }


@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": f"{settings.APP_TITLE} - Environment Variable Management",
        "docs": "/docs",
        "health": "/health",
        "env_api": "/api/env",
        "auth_api": f"{settings.API_V1_STR}/login/access-token",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
