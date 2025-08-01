# pyapi/utils/dependencies.py - 認證依賴注入
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from pyapi.db.dependencies import get_db_session
from pyapi.db.auth_models import UserModel
from pyapi.utils.auth import verify_token
from pyapi.schemas.auth_schemas import UserResponse

# HTTP Bearer 認證方案
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> UserModel:
    """
    取得當前使用者
    
    Args:
        credentials: HTTP Bearer 憑證
        db: 資料庫會話
        
    Returns:
        UserModel: 當前使用者模型
        
    Raises:
        HTTPException: 認證失敗時
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 驗證令牌
        payload = verify_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # 從資料庫取得使用者
    from sqlalchemy import select
    result = await db.execute(
        select(UserModel).where(UserModel.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    取得當前啟用的使用者
    
    Args:
        current_user: 當前使用者
        
    Returns:
        UserModel: 啟用的使用者模型
        
    Raises:
        HTTPException: 使用者未啟用時
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者帳號已停用"
        )
    return current_user


async def get_current_superuser(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    """
    取得當前超級使用者
    
    Args:
        current_user: 當前啟用使用者
        
    Returns:
        UserModel: 超級使用者模型
        
    Raises:
        HTTPException: 非超級使用者時
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足，需要超級使用者權限"
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[UserModel]:
    """
    取得可選的當前使用者（不強制要求認證）
    
    Args:
        credentials: 可選的 HTTP Bearer 憑證
        db: 資料庫會話
        
    Returns:
        Optional[UserModel]: 使用者模型，未認證時回傳 None
    """
    if credentials is None:
        return None
        
    try:
        # 驗證令牌
        payload = verify_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            return None
            
        # 從資料庫取得使用者
        from sqlalchemy import select
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user = result.scalar_one_or_none()
        
        if user and user.is_active:
            return user
            
    except Exception:
        pass
        
    return None


def require_permissions(*required_permissions: str):
    """
    需要特定權限的裝飾器工廠
    
    Args:
        *required_permissions: 需要的權限列表
        
    Returns:
        函數: 權限檢查依賴函數
    """
    async def permission_checker(
        current_user: UserModel = Depends(get_current_active_user)
    ) -> UserModel:
        # 超級使用者有所有權限
        if current_user.is_superuser:
            return current_user
            
        # 檢查使用者權限
        user_permissions = set()
        if current_user.permissions:
            import json
            try:
                user_permissions = set(json.loads(current_user.permissions))
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 檢查是否有所需權限
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"權限不足，需要權限: {', '.join(required_permissions)}"
            )
            
        return current_user
    
    return permission_checker


def require_roles(*required_roles: str):
    """
    需要特定角色的裝飾器工廠
    
    Args:
        *required_roles: 需要的角色列表
        
    Returns:
        函數: 角色檢查依賴函數
    """
    async def role_checker(
        current_user: UserModel = Depends(get_current_active_user)
    ) -> UserModel:
        # 超級使用者有所有角色
        if current_user.is_superuser:
            return current_user
            
        # 檢查使用者角色
        user_roles = set()
        if current_user.roles:
            import json
            try:
                user_roles = set(json.loads(current_user.roles))
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 檢查是否有所需角色
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"權限不足，需要角色: {', '.join(required_roles)}"
            )
            
        return current_user
    
    return role_checker


async def get_request_info(request: Request) -> dict:
    """
    取得請求資訊
    
    Args:
        request: FastAPI 請求物件
        
    Returns:
        dict: 請求資訊
    """
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "method": request.method,
        "url": str(request.url),
    }