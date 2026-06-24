"""通用响应模型"""

from pydantic import BaseModel
from typing import Any, Optional


class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class ErrorDetail(BaseModel):
    """错误详情"""
    detail: str


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def error_response(code: int = -1, message: str = "error", data: Any = None) -> dict:
    """错误响应"""
    return {"code": code, "message": message, "data": data}
