# pyapi/schemas/auth_schemas.py - 認證相關 Pydantic 模型
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
import re


class UserBase(BaseModel):
    """使用者基礎模型"""
    username: str = Field(..., min_length=3, max_length=255, description="使用者名稱")
    email: EmailStr = Field(..., description="電子郵件")
    full_name: Optional[str] = Field(None, max_length=500, description="全名")
    is_active: bool = Field(default=True, description="是否啟用")
    is_superuser: bool = Field(default=False, description="是否為超級使用者")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """驗證使用者名稱格式"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("使用者名稱只能包含字母、數字、底線和連字號")
        return v.lower()


class UserCreate(UserBase):
    """建立使用者的請求模型"""
    password: str = Field(..., min_length=8, max_length=128, description="密碼")
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """驗證密碼強度"""
        if len(v) < 8:
            raise ValueError("密碼長度至少 8 個字元")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密碼必須包含至少一個字母")
        if not re.search(r"\d", v):
            raise ValueError("密碼必須包含至少一個數字")
        return v


class UserUpdate(BaseModel):
    """更新使用者的請求模型"""
    email: Optional[EmailStr] = Field(None, description="電子郵件")
    full_name: Optional[str] = Field(None, max_length=500, description="全名")
    is_active: Optional[bool] = Field(None, description="是否啟用")
    is_superuser: Optional[bool] = Field(None, description="是否為超級使用者")


class UserResponse(BaseModel):
    """使用者回應模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")
    email: str = Field(..., description="電子郵件")
    full_name: Optional[str] = Field(None, description="全名")
    is_active: bool = Field(..., description="是否啟用")
    is_superuser: bool = Field(..., description="是否為超級使用者")
    created_at: datetime = Field(..., description="建立時間")
    last_login_at: Optional[datetime] = Field(None, description="最後登入時間")


class LoginRequest(BaseModel):
    """登入請求模型"""
    username: str = Field(..., min_length=1, description="使用者名稱")
    password: str = Field(..., min_length=1, description="密碼")


class TokenResponse(BaseModel):
    """令牌回應模型"""
    access_token: str = Field(..., description="存取令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌類型")
    expires_in: int = Field(..., description="過期時間（秒）")


class TokenRefreshRequest(BaseModel):
    """令牌刷新請求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


class ChangePasswordRequest(BaseModel):
    """變更密碼請求模型"""
    current_password: str = Field(..., description="目前密碼")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密碼")
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """驗證新密碼強度"""
        if len(v) < 8:
            raise ValueError("密碼長度至少 8 個字元")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密碼必須包含至少一個字母")
        if not re.search(r"\d", v):
            raise ValueError("密碼必須包含至少一個數字")
        return v


class UserProfile(BaseModel):
    """使用者個人資料模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="使用者 ID")
    username: str = Field(..., description="使用者名稱")
    email: str = Field(..., description="電子郵件")
    full_name: Optional[str] = Field(None, description="全名")
    created_at: datetime = Field(..., description="建立時間")
    last_login_at: Optional[datetime] = Field(None, description="最後登入時間")


class UserListResponse(BaseModel):
    """使用者列表回應模型"""
    users: List[UserResponse] = Field(..., description="使用者列表")
    total: int = Field(..., description="總筆數")
    skip: int = Field(..., description="跳過筆數")
    limit: int = Field(..., description="限制筆數")
    
    
# 範例模型
class UserCreateExample(UserCreate):
    """建立使用者的範例模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "password": "SecurePass123",
                "is_active": True,
                "is_superuser": False
            }
        }
    )


class LoginExample(LoginRequest):
    """登入範例模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "password": "SecurePass123"
            }
        }
    )