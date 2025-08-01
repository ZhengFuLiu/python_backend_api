# pyapi/db/dependencies.py - 資料庫依賴注入
from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    取得資料庫會話的依賴注入函數
    
    從 FastAPI request 中取得 app state 的 session factory
    
    Args:
        request: FastAPI Request 物件
        
    Yields:
        AsyncSession: 資料庫會話
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()