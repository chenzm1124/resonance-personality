"""LLM 博主推荐服务 — 根据人格测评结果推荐匹配的短视频博主"""

import json
import hashlib
import time
from typing import Any

from app.core.config import get_settings
from app.core.calculator import PERSONALITY_NAMES

settings = get_settings()

# 9种人格的描述关键词（用于构建 Prompt）
PERSONALITY_DESCRIPTIONS = {
    0: {"name": "英雄", "desc": "热血逆袭、领导力、突破担当", "keywords": "热血,逆袭,领导力,突破,担当"},
    1: {"name": "军师", "desc": "洞察规律、分析谋略、框架思维", "keywords": "洞察,框架,规律,分析,谋略"},
    2: {"name": "德鲁伊", "desc": "温和疗愈、倾听陪伴、自然低调", "keywords": "温和,疗愈,倾听,陪伴,自然"},
    3: {"name": "梦想家", "desc": "自由创意、浪漫探索、跨界创新", "keywords": "自由,创意,浪漫,探索,跨界"},
    4: {"name": "圣人", "desc": "深度洞察、原创理论、认知升级", "keywords": "洞察,原创理论,底层逻辑,人性,认知升级"},
    5: {"name": "天真者", "desc": "温暖付出、真诚纯粹、家庭关怀", "keywords": "温暖,付出,真诚,纯粹,家庭"},
    6: {"name": "普通人", "desc": "务实稳重、接地气、平凡幸福", "keywords": "务实,稳重,接地气,平凡,幸福"},
    7: {"name": "王者", "desc": "审美品质、精神追求、不将就", "keywords": "审美,品质,精神,追求,不将就"},
    8: {"name": "将军", "desc": "成功导向、执行力、目标价值", "keywords": "成功,执行力,目标,价值,体面"},
}

# 简单内存缓存 (相同人格组合 24h 内复用)
_cache: dict[str, tuple[float, list[dict]]] = {}
CACHE_TTL = 86400  # 24小时


def _cache_key(master: int, subs: list[int]) -> str:
    """生成缓存键"""
    raw = f"{master}_{sorted(subs)}"
    return hashlib.md5(raw.encode()).hexdigest()


def _build_prompt(master_idx: int, sub_indices: list[int], nine_scores: list[float]) -> str:
    """构建 LLM Prompt"""
    master_info = PERSONALITY_DESCRIPTIONS.get(master_idx, {})
    sub_names = [PERSONALITY_DESCRIPTIONS.get(i, {}).get("name", "未知") for i in sub_indices]

    prompt = f"""你是一位短视频IP打造专家。根据以下用户的人格测评结果，推荐3位适合该用户模仿学习的抖音/短视频平台大V博主。

## 用户人格特征
- 主人格: {master_info.get('name', '未知')}（{master_info.get('desc', '')}）
- 辅人格: {"、".join(sub_names)}
- 人格特征关键词: {master_info.get('keywords', '')}
- 主人格得分: {nine_scores[master_idx] if master_idx < len(nine_scores) else '?'} / 10

## 推荐要求
1. 推荐的博主应是在抖音、快手或小红书平台有一定影响力的内容创作者
2. 博主的内容风格应与用户的人格特征相匹配（如：英雄型适合励志/创业类博主，军师型适合商业分析/知识类博主）
3. 优先推荐粉丝量在10万以上的博主
4. 每位博主需提供2-3条代表作参考

## 输出格式
请严格按以下JSON格式输出（不要添加其他文字）:
{{
  "creators": [
    {{
      "name": "博主昵称",
      "platform": "抖音/快手/小红书",
      "style_tags": ["风格标签1", "风格标签2"],
      "followers": "粉丝量级(如: 100万+)",
      "reason": "推荐理由(50字以内，说明为什么适合该人格类型模仿)",
      "shooting_direction": "推荐拍摄方向(如: 逆袭故事、创业复盘)",
      "videos": [
        {{
          "title": "视频标题",
          "description": "视频简介(20字以内)",
          "url": "https://www.douyin.com/video/xxx 或分享链接"
        }}
      ]
    }}
  ]
}}
"""
    return prompt


async def get_creator_recommendations(
    nine_scores: list[float],
    master_personality: int,
    sub_personalities: list[int],
) -> dict[str, Any]:
    """
    获取博主推荐（带缓存）。

    返回:
        {
            "creators": [...],
            "cached": bool,
            "master_name": str,
            "sub_names": [str, str]
        }
    """
    cache_key = _cache_key(master_personality, sub_personalities)

    # 检查缓存
    if cache_key in _cache:
        cached_time, cached_data = _cache[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            master_name = PERSONALITY_NAMES[master_personality] if master_personality < len(PERSONALITY_NAMES) else "未知"
            sub_names = [PERSONALITY_NAMES[i] if i < len(PERSONALITY_NAMES) else "未知" for i in sub_personalities]
            return {
                "creators": cached_data,
                "cached": True,
                "master_name": master_name,
                "sub_names": sub_names,
            }

    # 调用 LLM
    prompt = _build_prompt(master_personality, sub_personalities, nine_scores)
    creators = await _call_llm(prompt)

    # 写入缓存
    _cache[cache_key] = (time.time(), creators)

    master_name = PERSONALITY_NAMES[master_personality] if master_personality < len(PERSONALITY_NAMES) else "未知"
    sub_names = [PERSONALITY_NAMES[i] if i < len(PERSONALITY_NAMES) else "未知" for i in sub_personalities]

    return {
        "creators": creators,
        "cached": False,
        "master_name": master_name,
        "sub_names": sub_names,
    }


async def _call_llm(prompt: str) -> list[dict]:
    """调用大模型 API 获取推荐结果"""
    if not settings.LLM_API_KEY:
        # 无 API Key 时返回示例数据
        return _get_mock_recommendations()

    try:
        return await _call_openai(prompt)
    except Exception as e:
        print(f"[LLM推荐] 调用失败: {e}")
        return _get_mock_recommendations()


async def _call_openai(prompt: str) -> list[dict]:
    """调用 OpenAI 兼容接口（使用 httpx 直接请求，避免 SDK 兼容性问题）"""
    import httpx

    # 拼接完整 URL
    base = settings.LLM_BASE_URL.rstrip('/')
    url = f"{base}/chat/completions"

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "你是一位专业的短视频IP打造顾问，擅长根据人格特征推荐匹配的博主。请严格按JSON格式输出。"},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": settings.LLM_MAX_TOKENS,
        "temperature": 0.7,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)

    print(f"[LLM推荐] 请求URL: {url}")
    print(f"[LLM推荐] 响应状态: {response.status_code}")

    if response.status_code != 200:
        print(f"[LLM推荐] API错误: {response.text[:300]}")
        return _get_mock_recommendations()

    data = response.json()
    print(f"[LLM推荐] 响应类型: {type(data)}, 键: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")

    # 提取内容
    content = ""
    if isinstance(data, dict) and 'choices' in data and data['choices']:
        content = data['choices'][0].get('message', {}).get('content', '')
    elif isinstance(data, dict) and 'content' in data:
        content = data['content']
    elif isinstance(data, str):
        content = data
    else:
        print(f"[LLM推荐] 未知响应格式: {str(data)[:300]}")
        content = str(data)

    return _parse_llm_response(content)


def _parse_llm_response(content: str) -> list[dict]:
    """解析 LLM 返回的 JSON 内容"""
    # 尝试提取 JSON 块
    content = content.strip()

    # 去掉可能的 markdown 代码块标记
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        data = json.loads(content)
        if isinstance(data, dict) and "creators" in data:
            return data["creators"]
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        print(f"[LLM推荐] JSON 解析失败，原始内容: {content[:200]}...")
        return _get_mock_recommendations()


def _get_mock_recommendations() -> list[dict]:
    """无 API Key 或调用失败时的示例数据"""
    return [
        {
            "name": "刘润",
            "platform": "抖音",
            "style_tags": ["商业洞察", "知识分享"],
            "followers": "2000万+",
            "reason": "适合军师/圣人型人格，善于用框架拆解商业逻辑，内容深度高",
            "shooting_direction": "商业分析、行业洞察、认知升级",
            "videos": [
                {
                    "title": "为什么你的生意越来越难做",
                    "description": "拆解商业环境变化底层逻辑",
                    "url": "https://www.douyin.com/search/刘润",
                },
                {
                    "title": "普通人的逆袭公式",
                    "description": "用系统思维改变命运",
                    "url": "https://www.douyin.com/search/刘润",
                },
            ],
        },
        {
            "name": "张雪峰",
            "platform": "抖音",
            "style_tags": ["教育规划", "真诚建议"],
            "followers": "3000万+",
            "reason": "适合英雄/将军型人格，敢说真话、直击痛点，表达力强",
            "shooting_direction": "教育规划、人生建议、热点评论",
            "videos": [
                {
                    "title": "选专业避坑指南",
                    "description": "用真实案例教你避坑",
                    "url": "https://www.douyin.com/search/张雪峰",
                },
            ],
        },
        {
            "name": "房琪kiki",
            "platform": "抖音",
            "style_tags": ["旅行美学", "治愈文案"],
            "followers": "1000万+",
            "reason": "适合梦想家/王者型人格，文案优美、画面精致，审美在线",
            "shooting_direction": "旅行vlog、生活美学、情感表达",
            "videos": [
                {
                    "title": "总要去一次新疆吧",
                    "description": "治愈系旅行文案天花板",
                    "url": "https://www.douyin.com/search/房琪kiki",
                },
                {
                    "title": "人生是旷野不是轨道",
                    "description": "用脚步丈量世界",
                    "url": "https://www.douyin.com/search/房琪kiki",
                },
            ],
        },
    ]
