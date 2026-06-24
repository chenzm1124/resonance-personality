"""博主推荐 API 接口"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.common import success_response, error_response
from app.services.llm_recommend import get_creator_recommendations

router = APIRouter(prefix="/recommend", tags=["推荐"])


class RecommendRequest(BaseModel):
    """博主推荐请求"""
    nineScores: list[float]          # 9个人格得分
    masterPersonality: int           # 主人格索引 (0-8)
    subPersonalities: list[int]      # 2个辅人格索引


@router.post("/creators")
async def recommend_creators(req: RecommendRequest):
    """
    根据人格测评结果推荐匹配的短视频博主。

    - nineScores: 9个人格维度的得分 (0-10)
    - masterPersonality: 主人格索引 (0-8)
    - subPersonalities: 辅人格索引列表 [2个]
    """
    try:
        # 参数校验
        if len(req.nineScores) != 9:
            return error_response(code=400, message="nineScores 应包含9个分值")
        if not (0 <= req.masterPersonality <= 8):
            return error_response(code=400, message="masterPersonality 应在 0-8 之间")
        if len(req.subPersonalities) < 1 or len(req.subPersonalities) > 3:
            return error_response(code=400, message="subPersonalities 应包含1-3个索引")

        result = await get_creator_recommendations(
            nine_scores=req.nineScores,
            master_personality=req.masterPersonality,
            sub_personalities=req.subPersonalities,
        )

        return success_response(data=result)

    except Exception as e:
        return error_response(code=500, message=f"推荐服务异常: {str(e)}")
