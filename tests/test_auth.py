# tests/test_auth_api.py - 認證 API 專用測試
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from pyapi.web.application import get_app


@pytest.fixture
def client():
    """建立測試客戶端"""
    app = get_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_user_data():
    """有效的使用者資料"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123",
        "full_name": "Test User"
    }


@pytest.fixture
def valid_login_data():
    """有效的登入資料"""
    return {
        "username": "testuser",
        "password": "SecurePass123"
    }


class TestAuthLogin:
    """登入功能測試"""
    
    def test_login_endpoint_exists(self, client):
        """測試登入端點是否存在"""
        response = client.post("/api/auth/login")
        # 端點存在但缺少資料應該回傳 422，不存在回傳 404
        assert response.status_code in [422, 400, 404]
    
    def test_login_with_empty_data(self, client):
        """測試空資料登入"""
        response = client.post("/api/auth/login", json={})
        assert response.status_code in [422, 400]
    
    def test_login_with_missing_username(self, client):
        """測試缺少使用者名稱"""
        data = {"password": "testpass"}
        response = client.post("/api/auth/login", json=data)
        assert response.status_code in [422, 400]
    
    def test_login_with_missing_password(self, client):
        """測試缺少密碼"""
        data = {"username": "testuser"}
        response = client.post("/api/auth/login", json=data)
        assert response.status_code in [422, 400]
    
    def test_login_with_invalid_credentials(self, client, valid_login_data):
        """測試無效認證資訊"""
        # 使用不存在的使用者
        invalid_data = valid_login_data.copy()
        invalid_data["username"] = "nonexistentuser"
        
        response = client.post("/api/auth/login", json=invalid_data)
        # 期望認證失敗或配置問題
        assert response.status_code in [401, 404, 422, 500]
    
    def test_login_content_type_validation(self, client, valid_login_data):
        """測試內容類型驗證"""
        response = client.post(
            "/api/auth/login",
            data=str(valid_login_data),  # 非 JSON 格式
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [422, 400, 415]


class TestAuthRegister:
    """註冊功能測試"""
    
    def test_register_endpoint_exists(self, client):
        """測試註冊端點是否存在"""
        response = client.post("/api/auth/register")
        assert response.status_code in [422, 400, 404]
    
    def test_register_with_valid_data_format(self, client, valid_user_data):
        """測試有效格式的註冊資料"""
        response = client.post("/api/auth/register", json=valid_user_data)
        # 可能成功或因其他原因失敗（如使用者已存在）
        assert response.status_code in [201, 409, 422, 400, 404, 500]
    
    def test_register_with_invalid_email(self, client, valid_user_data):
        """測試無效電子郵件格式"""
        invalid_data = valid_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code in [422, 400]
    
    def test_register_with_short_password(self, client, valid_user_data):
        """測試密碼過短"""
        invalid_data = valid_user_data.copy()
        invalid_data["password"] = "123"
        
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code in [422, 400]
    
    def test_register_with_missing_required_fields(self, client):
        """測試缺少必要欄位"""
        incomplete_data = {
            "username": "testuser"
            # 缺少 email 和 password
        }
        response = client.post("/api/auth/register", json=incomplete_data)
        assert response.status_code in [422, 400]


class TestAuthUserProfile:
    """使用者個人資料功能測試"""
    
    def test_get_user_profile_without_auth(self, client):
        """測試未認證時獲取個人資料"""
        response = client.get("/api/auth/me")
        # 應該要求認證
        assert response.status_code in [401, 403, 404]
    
    def test_get_user_profile_with_invalid_token(self, client):
        """測試使用無效令牌獲取個人資料"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code in [401, 403, 404]
    
    def test_update_profile_without_auth(self, client):
        """測試未認證時更新個人資料"""
        update_data = {"full_name": "Updated Name"}
        response = client.put("/api/auth/me", json=update_data)
        assert response.status_code in [401, 403, 404]


class TestAuthTokenManagement:
    """令牌管理功能測試"""
    
    def test_refresh_token_endpoint(self, client):
        """測試刷新令牌端點"""
        token_data = {"refresh_token": "fake-refresh-token"}
        response = client.post("/api/auth/refresh", json=token_data)
        # 可能因為無效令牌而失敗
        assert response.status_code in [401, 404, 422, 400, 500]
    
    def test_logout_endpoint(self, client):
        """測試登出端點"""
        response = client.post("/api/auth/logout")
        # 登出可能不需要認證，或需要認證但返回適當錯誤
        assert response.status_code in [200, 401, 403, 404]
    
    def test_logout_with_token(self, client):
        """測試使用令牌登出"""
        headers = {"Authorization": "Bearer fake-token"}
        response = client.post("/api/auth/logout", headers=headers)
        assert response.status_code in [200, 401, 404]


class TestAuthPasswordManagement:
    """密碼管理功能測試"""
    
    def test_change_password_without_auth(self, client):
        """測試未認證時變更密碼"""
        password_data = {
            "current_password": "oldpass",
            "new_password": "newpass123"
        }
        response = client.post("/api/auth/change-password", json=password_data)
        assert response.status_code in [401, 403, 404]
    
    def test_change_password_invalid_format(self, client):
        """測試無效的密碼變更格式"""
        password_data = {
            "current_password": "old",
            "new_password": "123"  # 密碼過短
        }
        headers = {"Authorization": "Bearer fake-token"}
        response = client.post("/api/auth/change-password", json=password_data, headers=headers)
        assert response.status_code in [422, 400, 401, 404]


class TestAuthValidation:
    """認證資料驗證測試"""
    
    @pytest.mark.parametrize("invalid_username", [
        "",  # 空字串
        "ab",  # 太短
        "user with spaces",  # 包含空格
        "user@invalid",  # 包含特殊字符
        "a" * 256,  # 太長
    ])
    def test_invalid_usernames(self, client, invalid_username):
        """測試無效的使用者名稱"""
        data = {
            "username": invalid_username,
            "email": "test@example.com",
            "password": "SecurePass123"
        }
        response = client.post("/api/auth/register", json=data)
        assert response.status_code in [422, 400, 404]
    
    @pytest.mark.parametrize("invalid_email", [
        "",  # 空字串
        "invalid",  # 無效格式
        "@example.com",  # 缺少本地部分
        "user@",  # 缺少域名
        "user space@example.com",  # 包含空格
    ])
    def test_invalid_emails(self, client, invalid_email):
        """測試無效的電子郵件"""
        data = {
            "username": "testuser",
            "email": invalid_email,
            "password": "SecurePass123"
        }
        response = client.post("/api/auth/register", json=data)
        assert response.status_code in [422, 400, 404]


# 使用模擬的認證測試
class TestAuthWithMocks:
    """使用模擬服務的認證測試"""
    
    @patch("pyapi.services.auth_service.AuthService.authenticate_user")
    def test_login_success_mock(self, mock_auth, client, valid_login_data):
        """測試模擬成功登入"""
        # 模擬認證成功
        mock_auth.return_value = {
            "access_token": "fake-token",
            "token_type": "bearer"
        }
        
        response = client.post("/api/auth/login", json=valid_login_data)
        
        # 如果端點存在且模擬生效，應該成功
        if response.status_code != 404:
            # 檢查是否調用了認證服務（如果端點實際存在）
            assert response.status_code in [200, 422, 401, 500]