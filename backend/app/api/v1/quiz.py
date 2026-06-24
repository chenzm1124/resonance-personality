"""答题与结果相关API"""

import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.quiz_record import QuizRecord
from app.models.test_result import TestResult
from app.core.calculator import calculate_personality, PERSONALITY_NAMES
from app.schemas.common import success_response, error_response

router = APIRouter(prefix="/quiz", tags=["答题"])


class QuizSubmitRequest(BaseModel):
    """答题提交请求"""
    user_id: int
    answers: list[int]  # 63题答案，每题0-10
    duration_seconds: int = 0


class QuizProgressRequest(BaseModel):
    """答题进度同步请求（可选，用于跨设备恢复）"""
    user_id: int
    answers: list[int]  # 当前已答题目答案
    record_id: int | None = None  # 已有记录ID，为空则新建


@router.post("/submit")
async def submit_quiz(req: QuizSubmitRequest, db: Session = Depends(get_db)):
    """
    提交63题答案，服务端计算九色人格得分并存储结果。
    """
    # 校验答案
    if len(req.answers) != 63:
        return error_response(code=400, message=f"答案数量应为63题，实际收到{len(req.answers)}题")

    for i, score in enumerate(req.answers):
        if not (0 <= score <= 10):
            return error_response(code=400, message=f"第{i+1}题得分{score}超出0-10范围")

    # 创建答题记录
    record = QuizRecord(
        user_id=req.user_id,
        answers_json=json.dumps(req.answers),
        duration_seconds=req.duration_seconds,
        status="completed",
    )
    db.add(record)
    db.flush()  # 获取 record.id

    # 服务端计算九色人格
    result = calculate_personality(req.answers)

    # 存储测试结果
    test_result = TestResult(
        user_id=req.user_id,
        quiz_record_id=record.id,
        nine_scores_json=json.dumps(result["nine_scores"]),
        master_personality=result["master_personality"],
        sub_personalities_json=json.dumps(result["sub_personalities"]),
    )
    db.add(test_result)
    db.commit()
    db.refresh(test_result)

    return success_response(data={
        "record_id": record.id,
        "result_id": test_result.id,
        "nine_scores": result["nine_scores"],
        "master_personality": {
            "index": result["master_personality"],
            "name": PERSONALITY_NAMES[result["master_personality"]],
        },
        "sub_personalities": [
            {"index": idx, "name": PERSONALITY_NAMES[idx]}
            for idx in result["sub_personalities"]
        ],
    })


@router.post("/progress")
async def sync_progress(req: QuizProgressRequest, db: Session = Depends(get_db)):
    """
    同步答题进度（可选功能，用于跨设备恢复）。
    """
    if req.record_id:
        record = db.query(QuizRecord).filter(QuizRecord.id == req.record_id).first()
        if not record:
            return error_response(code=404, message="答题记录不存在")
        record.answers_json = json.dumps(req.answers)
    else:
        record = QuizRecord(
            user_id=req.user_id,
            answers_json=json.dumps(req.answers),
            status="in_progress",
        )
        db.add(record)

    db.commit()
    db.refresh(record)

    return success_response(data={
        "record_id": record.id,
        "answered_count": len(req.answers),
    })


@router.get("/result/{result_id}")
async def get_result(result_id: int, db: Session = Depends(get_db)):
    """查询测试结果详情"""
    result = db.query(TestResult).filter(TestResult.id == result_id).first()
    if not result:
        return error_response(code=404, message="测试结果不存在")

    nine_scores = json.loads(result.nine_scores_json)
    sub_personalities = json.loads(result.sub_personalities_json)

    return success_response(data={
        "result_id": result.id,
        "user_id": result.user_id,
        "nine_scores": nine_scores,
        "master_personality": {
            "index": result.master_personality,
            "name": PERSONALITY_NAMES[result.master_personality],
        },
        "sub_personalities": [
            {"index": idx, "name": PERSONALITY_NAMES[idx]}
            for idx in sub_personalities
        ],
        "created_at": result.created_at.isoformat(),
    })


@router.get("/results")
async def get_user_results(
    user_id: int,
    db: Session = Depends(get_db),
):
    """获取用户所有测试结果列表"""
    results = (
        db.query(TestResult)
        .filter(TestResult.user_id == user_id)
        .order_by(TestResult.created_at.desc())
        .all()
    )

    items = []
    for r in results:
        nine_scores = json.loads(r.nine_scores_json)
        items.append({
            "result_id": r.id,
            "master_personality": {
                "index": r.master_personality,
                "name": PERSONALITY_NAMES[r.master_personality],
            },
            "nine_scores": nine_scores,
            "created_at": r.created_at.isoformat(),
        })

    return success_response(data={"results": items})
