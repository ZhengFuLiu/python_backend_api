# pyapi/web/api/auth.py - 認證 API 路由
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from pyapi.db.dependencies import get_db_session
from pyapi.db.auth_models import UserModel
from pyapi.schemas.auth_schemas import (
    UserCreate, UserUpdate, UserResponse, UserProfile, UserListResponse,
    LoginRequest, TokenResponse, TokenRefreshRequest, ChangePasswordRequest
)
from pyapi.services.auth_service import AuthService
from pyapi.utils.dependencies import (
    get_current_user, get_current_active_user, get_current_superuser, get_request_info
)

logger = logging.getLogger(__name__)

# 建立路由器
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    註冊新使用者
    
    建立新的使用者帳號
    """
    try:
        logger.info(f"註冊新使用者: {user_data.username}")
        
        auth_service = AuthService(db)
        user = await auth_service.create_user(user_data)
        
        logger.info(f"使用者註冊成功 - ID: {user.id}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        
    except ValueError as e:
        logger.warning(f"使用者註冊失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"註冊使用者時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="註冊使用者時發生錯誤"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    """
    使用者登入
    
    驗證使用者憑證並回傳 JWT 令牌
    """
    try:
        logger.info(f"使用者登入嘗試: {login_data.username}")
        
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(login_data)
        
        if not user:
            logger.warning(f"登入失敗 - 無效憑證: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="使用者名稱或密碼錯誤",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 取得請求資訊
        request_info = await get_request_info(request)
        
        # 建立令牌
        tokens = await auth_service.create_tokens(
            user=user,
            user_agent=request_info.get("user_agent"),
            ip_address=request_info.get("ip_address")
        )
        
        logger.info(f"使用者登入成功: {user.username}")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登入時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登入時發生錯誤"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db_session)
) -> TokenResponse:
    """
    刷新存取令牌
    
    使用刷新令牌取得新的存取令牌
    """
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
        
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌時發生錯誤"
        )


@router.post("/logout")
async def logout(
    refresh_data: TokenRefreshRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    使用者登出
    
    撤銷指定的刷新令牌
    """
    try:
        auth_service = AuthService(db)
        revoked = await auth_service.revoke_refresh_token(refresh_data.refresh_token)
        
        if revoked:
            logger.info(f"使用者登出成功: {current_user.username}")
            return {"message": "登出成功"}
        else:
            return {"message": "令牌已失效"}
            
    except Exception as e:
        logger.error(f"登出時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出時發生錯誤"
        )


@router.post("/logout-all")
async def logout_all(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    登出所有裝置
    
    撤銷使用者的所有刷新令牌
    """
    try:
        auth_service = AuthService(db)
        revoked_count = await auth_service.revoke_all_user_tokens(current_user.id)
        
        logger.info(f"使用者從所有裝置登出: {current_user.username}, 撤銷 {revoked_count} 個令牌")
        
        return {
            "message": f"已從所有裝置登出，撤銷了 {revoked_count} 個令牌"
        }
        
    except Exception as e:
        logger.error(f"登出所有裝置時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出所有裝置時發生錯誤"
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_active_user)
) -> UserProfile:
    """
    取得當前使用者個人資料
    """
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    更新當前使用者個人資料
    """
    try:
        logger.info(f"更新使用者資料: {current_user.username}")
        
        auth_service = AuthService(db)
        updated_user = await auth_service.update_user(current_user.id, user_update)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="使用者不存在"
            )
        
        logger.info(f"使用者資料更新成功: {current_user.username}")
        
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
            is_superuser=updated_user.is_superuser,
            created_at=updated_user.created_at,
            last_login_at=updated_user.last_login_at
        )
        
    except ValueError as e:
        logger.warning(f"更新使用者資料失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新使用者資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新使用者資料時發生錯誤"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    變更密碼
    """
    try:
        logger.info(f"變更密碼請求: {current_user.username}")
        
        auth_service = AuthService(db)
        success = await auth_service.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="目前密碼錯誤"
            )
        
        logger.info(f"密碼變更成功: {current_user.username}")
        
        return {
            "message": "密碼變更成功，請重新登入"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"變更密碼時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="變更密碼時發生錯誤"
        )


# ==================== 管理員專用端點 ====================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db_session)
) -> UserListResponse:
    """
    取得使用者列表 (僅限管理員)
    """
    try:
        auth_service = AuthService(db)
        users, total = await auth_service.list_users(skip=skip, limit=limit)
        
        return UserListResponse(
            users=[
                UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    created_at=user.created_at,
                    last_login_at=user.last_login_at
                )
                for user in users
            ],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"取得使用者列表時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取得使用者列表時發生錯誤"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    根據 ID 取得使用者 (僅限管理員)
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="使用者不存在"
            )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得使用者時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取得使用者時發生錯誤"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    """
    更新指定使用者 (僅限管理員)
    """
    try:
        logger.info(f"管理員更新使用者: {user_id}")
        
        auth_service = AuthService(db)
        updated_user = await auth_service.update_user(user_id, user_update)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="使用者不存在"
            )
        
        logger.info(f"使用者更新成功: {updated_user.username}")
        
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
            is_superuser=updated_user.is_superuser,
            created_at=updated_user.created_at,
            last_login_at=updated_user.last_login_at
        )
        
    except ValueError as e:
        logger.warning(f"更新使用者失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新使用者時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新使用者時發生錯誤"
        )


@router.post("/users/{user_id}/revoke-tokens")
async def revoke_user_tokens(
    user_id: int,
    current_user: UserModel = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    撤銷指定使用者的所有令牌 (僅限管理員)
    """
    try:
        auth_service = AuthService(db)
        
        # 檢查使用者是否存在
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="使用者不存在"
            )
        
        revoked_count = await auth_service.revoke_all_user_tokens(user_id)
        
        logger.info(f"管理員撤銷使用者令牌: {user.username}, 撤銷 {revoked_count} 個令牌")
        
        return {
            "message": f"已撤銷使用者 {user.username} 的 {revoked_count} 個令牌"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"撤銷使用者令牌時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="撤銷使用者令牌時發生錯誤"
        )