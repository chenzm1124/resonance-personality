# 共鸣人格IP打造系统

> 63道情境直觉测试，发现你的九色人格与守护神兽

## 项目简介

一款基于微信小程序的人格测评工具，通过7个维度×9道情境题目，交叉计算出9种人格原型的能量分布，帮助用户发现自身IP人格定位，并获得个性化拍摄方向建议。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | uni-app + Vue 3 + TypeScript + Pinia |
| 后端 | FastAPI + Python 3.11 |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| 迁移 | Alembic |
| 部署 | Docker Compose |

## 项目结构

```
resonance-personality/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/        # API 端点 (auth/quiz/config/events)
│   │   ├── core/          # 核心逻辑 (calculator/config/security)
│   │   ├── db/            # 数据库 (session/migrations)
│   │   ├── models/        # SQLAlchemy ORM 模型
│   │   ├── schemas/       # Pydantic 数据模型
│   │   └── main.py        # FastAPI 入口
│   ├── data/              # 静态配置 (题目/人格/维度)
│   └── tests/             # pytest 测试
├── miniprogram/           # uni-app 微信小程序
│   └── src/
│       ├── api/           # 请求封装
│       ├── components/    # UI 组件
│       ├── composables/   # 组合式函数
│       ├── data/          # 静态配置
│       ├── pages/         # 页面 (landing/quiz/loading/result/privacy)
│       └── stores/        # Pinia 状态管理
├── docker-compose.yml
└── .env.example
```

## 核心功能

- **九色人格计算引擎**：7维度×9题交叉映射，前后端双校验
- **沉浸式答题体验**：7维度背景切换、光粒子动效、背景音乐
- **结果海报生成**：Canvas 2D 绘制能量柱+守护神兽+IP标签
- **微信社交分享**：一键转发、保存到相册
- **埋点追踪系统**：20种核心事件批量上报
- **网络异常处理**：自动重试、离线降级、错误上报

## 快速开始

### 后端

```bash
cd backend
pip install -e ".[dev]"
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd miniprogram
npm install --registry https://registry.npmmirror.com
npm run dev:mp-weixin
```

### 测试

```bash
cd backend
pytest tests/ -v
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/v1/auth/login` | 微信/Mock登录 |
| POST | `/api/v1/quiz/submit` | 提交63题答案 |
| GET | `/api/v1/quiz/result/{id}` | 查询测试结果 |
| GET | `/api/v1/config/questions` | 获取63题配置 |
| GET | `/api/v1/config/personalities` | 获取9种人格配置 |
| GET | `/api/v1/config/dimensions` | 获取7维度配置 |
| POST | `/api/v1/events/batch` | 批量上报事件 |

## 九色人格体系

| 索引 | 人格 | 守护神兽 | IP类型 |
|------|------|----------|--------|
| 0 | 英雄 | 红色雄狮 | 热血挑战者 |
| 1 | 军师 | 深蓝银狐 | 冷静分析者 |
| 2 | 德鲁伊 | 绿色灵鹿 | 自然疗愈者 |
| 3 | 梦想家 | 橙色飞马 | 浪漫冒险家 |
| 4 | 圣人 | 黑色蜘蛛 | 深邃哲思者 |
| 5 | 天真者 | 白色小狗 | 纯真守护者 |
| 6 | 普通人 | 灰色绵羊 | 温暖陪伴者 |
| 7 | 王者 | 紫色巨蟒 | 魅力统治者 |
| 8 | 将军 | 金色金钱豹 | 果敢行动者 |

## License

Private - All rights reserved
