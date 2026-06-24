"""共鸣人格IP打造系统 — FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import engine, Base
from app.api.router import api_router

# 确保所有模型被导入，以便 Base.metadata 包含它们
import app.models  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时自动建表"""
    # 开发环境自动建表（生产环境应使用 Alembic 迁移）
    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="共鸣人格IP打造系统后端API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": -1, "message": f"服务器内部错误: {str(exc)}", "data": None},
    )


# 注册路由
app.include_router(api_router)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
