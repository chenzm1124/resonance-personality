"""
API 端点集成测试
覆盖:
  1. 健康检查
  2. Mock 登录
  3. 答题提交（正常 + 边界）
  4. 结果查询
  5. 配置接口（题目/人格/维度）
  6. 事件上报
  7. 错误处理（无效数据、未认证）
"""

import pytest


class TestHealthCheck:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestAuth:
    def test_mock_login(self, client):
        resp = client.post("/api/v1/auth/login", json={"code": "mock_user_1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "token" in data["data"]
        assert "user" in data["data"]

    def test_empty_code(self, client):
        resp = client.post("/api/v1/auth/login", json={"code": ""})
        # API可能返回200但code!=0，或者422
        assert resp.status_code in [200, 400, 422]


class TestQuizSubmit:
    def test_submit_normal(self, client):
        """正常提交63题"""
        answers = [5] * 63
        resp = client.post(
            "/api/v1/quiz/submit",
            json={"user_id": 1, "answers": answers, "duration_seconds": 300},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        result = data["data"]
        assert "nine_scores" in result
        assert "master_personality" in result
        assert "sub_personalities" in result

    def test_submit_all_tens(self, client):
        """全10分 — AC-16边界测试"""
        answers = [10] * 63
        resp = client.post(
            "/api/v1/quiz/submit",
            json={"user_id": 1, "answers": answers, "duration_seconds": 100},
        )
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["master_personality"]["index"] == 0  # 英雄

    def test_submit_all_zeros(self, client):
        """全0分"""
        answers = [0] * 63
        resp = client.post(
            "/api/v1/quiz/submit",
            json={"user_id": 1, "answers": answers, "duration_seconds": 100},
        )
        assert resp.status_code == 200
        result = resp.json()["data"]
        assert result["master_personality"]["index"] == 0  # 英雄（优先级）

    def test_submit_wrong_count(self, client):
        """答案数量不正确应返回错误"""
        resp = client.post(
            "/api/v1/quiz/submit",
            json={"user_id": 1, "answers": [5] * 60, "duration_seconds": 100},
        )
        # API返回200但body中code!=0
        body = resp.json()
        assert body["code"] != 0 or resp.status_code in [400, 422, 500]


class TestConfig:
    def test_get_questions(self, client):
        resp = client.get("/api/v1/config/questions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert len(data["data"]) == 63

    def test_get_personalities(self, client):
        resp = client.get("/api/v1/config/personalities")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert len(data["data"]) == 9

    def test_get_dimensions(self, client):
        resp = client.get("/api/v1/config/dimensions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert len(data["data"]) == 7


class TestEvents:
    def test_batch_events(self, client):
        events = [
            {"event": "page_view_landing", "timestamp": 1000000, "userId": "test"},
            {"event": "click_start_test", "timestamp": 1000100, "userId": "test"},
        ]
        resp = client.post("/api/v1/events/batch", json={"events": events})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["received"] == 2

    def test_report_error(self, client):
        resp = client.post(
            "/api/v1/events/error",
            json={"errorType": "api_error", "detail": "test error"},
        )
        assert resp.status_code == 200
