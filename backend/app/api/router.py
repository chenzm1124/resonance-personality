"""API路由汇总"""

from fastapi import APIRouter
from app.api.v1 import auth, quiz, config, events, recommend

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(quiz.router)
api_router.include_router(config.router)
api_router.include_router(events.router)
api_router.include_router(recommend.router)
