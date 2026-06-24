"""Pytest 配置 — 共享 fixtures"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_login(client):
    """Mock登录并返回 token"""
    resp = client.post("/api/v1/auth/login", json={"code": "mock_test_user"})
    assert resp.status_code == 200
    data = resp.json()
    return data["data"]["token"]


@pytest.fixture
def auth_headers(mock_login):
    """带认证的请求头"""
    return {"Authorization": f"Bearer {mock_login}"}
