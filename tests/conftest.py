# tests/conftest.py - 測試配置檔案
import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
import asyncio

# 設定測試環境變數
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DB_ECHO"] = "false"
# 設定測試資料庫為 SQLite 記憶體資料庫
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_NAME"] = "test"

from pyapi.web.application import get_app


@pytest.fixture(scope="session")
def event_loop():
    """建立測試事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app():
    """建立 FastAPI 應用程式實例（會話級別）"""
    with patch("pyapi.web.lifespan._setup_db") as mock_setup, \
         patch("pyapi.web.lifespan._create_tables") as mock_create:
        
        # 模擬資料庫設定
        mock_setup.return_value = None
        mock_create.return_value = AsyncMock()
        
        return get_app()


@pytest.fixture
def client(app):
    """建立測試客戶端"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_database():
    """模擬資料庫相關功能"""
    with patch("pyapi.web.lifespan._setup_db") as mock_setup, \
         patch("pyapi.web.lifespan._create_tables") as mock_create:
        
        mock_setup.return_value = None
        mock_create.return_value = AsyncMock()
        
        yield {
            "setup_db": mock_setup,
            "create_tables": mock_create
        }


@pytest.fixture
def mock_db_session():
    """模擬資料庫 session"""
    mock_session = AsyncMock()
    with patch("pyapi.db.dependencies.get_db_session") as mock_get_session:
        mock_get_session.return_value = mock_session
        yield mock_session


@pytest.fixture
def sample_user_data():
    """範例使用者資料"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_data_item():
    """範例資料項目"""
    return {
        "name": "Test Data Item",
        "description": "This is a test data item",
        "config": {
            "setting1": "value1",
            "setting2": 42
        },
        "status": "active"
    }


@pytest.fixture
def auth_headers():
    """認證標頭（模擬）"""
    return {
        "Authorization": "Bearer fake-jwt-token-for-testing"
    }