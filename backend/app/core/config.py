"""应用配置管理"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置，从环境变量和 .env 文件读取"""

    APP_NAME: str = "共鸣人格IP打造系统"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # 数据库
    DATABASE_URL: str = "sqlite:///./resonance_personality.db"

    # 微信小程序
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 大模型 API（OpenAI 兼容接口）
    LLM_PROVIDER: str = "openai"          # openai 兼容接口
    LLM_API_KEY: str = ""                 # API Key
    LLM_BASE_URL: str = "https://ai.chinaz.net/v1"  # API 地址（OpenAI 兼容）
    LLM_MODEL: str = "gpt-4o-mini"        # 模型名称
    LLM_MAX_TOKENS: int = 2000            # 最大输出 token

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
