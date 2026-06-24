"""题目配置与人格配置管理API"""

import json
import os
from fastapi import APIRouter
from app.schemas.common import success_response, error_response

router = APIRouter(prefix="/config", tags=["答题配置"])

# 数据文件路径（后端也持有一份配置数据）
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')


def _load_json(filename: str) -> list | dict | None:
    """加载JSON数据文件"""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


@router.get("/questions")
async def get_questions():
    """获取63道题目配置"""
    questions = _load_json('questions.json')
    if questions is None:
        return error_response(code=404, message="题目配置未找到")
    return success_response(data=questions)


@router.get("/personalities")
async def get_personalities():
    """获取9种人格配置"""
    personalities = _load_json('personalities.json')
    if personalities is None:
        return error_response(code=404, message="人格配置未找到")
    return success_response(data=personalities)


@router.get("/dimensions")
async def get_dimensions():
    """获取7维度配置"""
    dimensions = _load_json('dimensions.json')
    if dimensions is None:
        return error_response(code=404, message="维度配置未找到")
    return success_response(data=dimensions)
