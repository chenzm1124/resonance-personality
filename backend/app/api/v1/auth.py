"""认证相关API"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx

from app.db.session import get_db
from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.common import success_response, error_response

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """微信登录请求"""
    code: str  # wx.login 返回的 code


class UserInfoUpdate(BaseModel):
    """用户信息更新"""
    nickname: str | None = None
    avatar_url: str | None = None


@router.post("/login")
async def wechat_login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录。
    通过 wx.login 的 code 换取 openid，返回 JWT token。
    开发环境下可传入 mock_code 直接生成测试用户。
    """
    settings = get_settings()
    openid = None

    # 开发环境：支持 mock 登录
    if settings.APP_ENV == "development" and req.code.startswith("mock_"):
        openid = f"dev_{req.code}"
    else:
        # 调用微信 code2session 接口
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.WECHAT_APPID,
            "secret": settings.WECHAT_SECRET,
            "js_code": req.code,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            return error_response(code=401, message=f"微信登录失败: {data.get('errmsg', '未知错误')}")
        openid = data.get("openid")

    if not openid:
        return error_response(code=401, message="无法获取用户标识")

    # 查找或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(openid=openid)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 生成 token
    token = create_access_token({"sub": str(user.id), "openid": openid})

    return success_response(data={
        "token": token,
        "user": {
            "id": user.id,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
        },
    })


@router.put("/profile")
async def update_profile(
    req: UserInfoUpdate,
    db: Session = Depends(get_db),
    user_id: int = 0,  # 实际应从 JWT 中解析，MVP先简化
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(code=404, message="用户不存在")

    if req.nickname is not None:
        user.nickname = req.nickname
    if req.avatar_url is not None:
        user.avatar_url = req.avatar_url

    db.commit()
    db.refresh(user)

    return success_response(data={
        "id": user.id,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
    })


@router.get("/status")
async def get_user_status(
    db: Session = Depends(get_db),
    user_id: int = 0,  # 实际应从 JWT 中解析
):
    """
    获取用户测试状态: new(新用户) / in_progress(答题中) / completed(已完成)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return error_response(code=404, message="用户不存在")

    from app.models.quiz_record import QuizRecord

    # 查找最新答题记录
    latest_record = (
        db.query(QuizRecord)
        .filter(QuizRecord.user_id == user.id)
        .order_by(QuizRecord.created_at.desc())
        .first()
    )

    if not latest_record:
        status = "new"
    elif latest_record.status == "completed":
        status = "completed"
    else:
        status = "in_progress"

    return success_response(data={
        "status": status,
        "latest_record_id": latest_record.id if latest_record else None,
        "current_question": len(eval(latest_record.answers_json)) if latest_record and latest_record.answers_json != "[]" else 0,
    })
