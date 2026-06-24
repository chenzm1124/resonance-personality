"""事件埋点上报API"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


class TrackEvent(BaseModel):
    event: str
    timestamp: int
    userId: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class BatchEventsRequest(BaseModel):
    events: List[TrackEvent]


@router.post("/batch")
async def report_events(req: BatchEventsRequest, request: Request):
    """批量上报事件（生产环境写入日志/数据库，开发环境打印）"""
    client_ip = request.client.host if request.client else "unknown"
    
    for evt in req.events:
        logger.info(
            f"[Event] {evt.event} | user={evt.userId} | ip={client_ip} | "
            f"ts={evt.timestamp} | props={evt.properties or {}}"
        )

    return {"code": 0, "message": "ok", "data": {"received": len(req.events)}}


@router.post("/error")
async def report_error(request: Request):
    """上报客户端错误"""
    body = await request.json()
    error_type = body.get("errorType", "unknown")
    detail = body.get("detail", "")
    client_ip = request.client.host if request.client else "unknown"

    logger.error(f"[ClientError] type={error_type} | ip={client_ip} | detail={detail}")

    return {"code": 0, "message": "ok"}
