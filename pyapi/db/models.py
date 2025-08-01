# pyapi/db/models.py - 資料庫模型
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

from pyapi.db.meta import meta
from pyapi.settings import settings

# 使用自定義 metadata 建立 Base
Base = declarative_base(metadata=meta)


class DataModel(Base):
    """
    資料表模型
    
    儲存從前端接收的資料
    """
    __tablename__ = "data_records"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="主鍵 ID")
    
    # 基本資訊
    name = Column(String(255), nullable=False, index=True, comment="資料名稱")
    description = Column(Text, nullable=True, comment="資料描述")
    
    # 配置資料 (JSON 格式儲存)
    config = Column(JSON, nullable=True, comment="配置參數")
    
    # 狀態管理
    status = Column(
        String(50), 
        nullable=False, 
        default="active", 
        index=True,
        comment="資料狀態: active, inactive, pending, completed"
    )
    
    # 時間戳記
    created_at = Column(
        DateTime, 
        nullable=False, 
        default=func.now(),
        comment="建立時間"
    )
    updated_at = Column(
        DateTime, 
        nullable=False, 
        default=func.now(),
        onupdate=func.now(),
        comment="更新時間"
    )
    
    def __repr__(self):
        return f"<DataModel(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def load_all_models() -> None:
    """
    載入所有模型
    
    這個函數用於確保所有模型都被 SQLAlchemy 註冊
    """
    # 這裡會自動載入所有繼承自 Base 的模型
    # 目前只有 DataModel，未來可以加入更多模型
    pass


# 資料庫會話相關函數
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    取得資料庫會話
    
    這個函數會從 FastAPI app state 中取得 session factory
    """
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # 這個函數會在 FastAPI 的依賴注入系統中使用
    # 實際的 session factory 會從 app.state 中取得
    # 這裡提供一個基本的實作，實際使用時會被 FastAPI 的依賴系統取代
    engine = create_async_engine(settings.db_url, echo=settings.db_echo)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()