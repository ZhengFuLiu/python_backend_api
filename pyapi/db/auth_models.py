# pyapi/db/auth_models.py - 認證相關資料模型
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from pyapi.db.meta import meta
from pyapi.db.models import Base


class UserModel(Base):
    """
    使用者資料模型
    """
    __tablename__ = "pyapi_users"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="使用者 ID")
    
    # 基本資訊
    username = Column(String(255), unique=True, index=True, nullable=False, comment="使用者名稱")
    email = Column(String(255), unique=True, index=True, nullable=False, comment="電子郵件")
    full_name = Column(String(500), nullable=True, comment="全名")
    
    # 認證資訊
    hashed_password = Column(String(255), nullable=False, comment="雜湊密碼")
    is_active = Column(Boolean, default=True, comment="是否啟用")
    is_superuser = Column(Boolean, default=False, comment="是否為超級使用者")
    
    # 權限和角色
    roles = Column(Text, nullable=True, comment="角色列表 (JSON)")
    permissions = Column(Text, nullable=True, comment="權限列表 (JSON)")
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="建立時間")
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="更新時間")
    last_login_at = Column(DateTime, nullable=True, comment="最後登入時間")
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>"


class RefreshTokenModel(Base):
    """
    刷新令牌資料模型
    """
    __tablename__ = "pyapi_refresh_tokens"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="令牌 ID")
    
    # 令牌資訊
    token = Column(String(255), unique=True, index=True, nullable=False, comment="刷新令牌")
    user_id = Column(Integer, nullable=False, comment="使用者 ID")
    
    # 狀態管理
    is_active = Column(Boolean, default=True, comment="是否有效")
    expires_at = Column(DateTime, nullable=False, comment="過期時間")
    
    # 額外資訊
    user_agent = Column(String(500), nullable=True, comment="使用者代理")
    ip_address = Column(String(50), nullable=True, comment="IP 位址")
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="建立時間")
    revoked_at = Column(DateTime, nullable=True, comment="撤銷時間")
    
    def __repr__(self):
        return f"<RefreshTokenModel(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"