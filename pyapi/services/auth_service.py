# pyapi/services/auth_service.py - 認證服務層
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import secrets
import json

from pyapi.db.auth_models import UserModel, RefreshTokenModel
from pyapi.schemas.auth_schemas import UserCreate, UserUpdate, LoginRequest, TokenResponse
from pyapi.utils.auth import verify_password, get_password_hash, create_access_token, create_refresh_token
from pyapi.settings import settings

class AuthService:
    """認證服務類別"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> UserModel:
        """
        建立新使用者
        
        Args:
            user_data: 使用者建立資料
            
        Returns:
            UserModel: 建立的使用者模型
            
        Raises:
            ValueError: 使用者名稱或電子郵件已存在時
        """
        # 檢查使用者名稱是否已存在
        result = await self.db.execute(
            select(UserModel).where(UserModel.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"使用者名稱 '{user_data.username}' 已存在")
        
        # 檢查電子郵件是否已存在
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"電子郵件 '{user_data.email}' 已存在")
        
        # 建立使用者
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def authenticate_user(self, login_data: LoginRequest) -> Optional[UserModel]:
        """
        驗證使用者登入
        
        Args:
            login_data: 登入資料
            
        Returns:
            Optional[UserModel]: 驗證成功的使用者模型，失敗時回傳 None
        """
        # 取得使用者
        result = await self.db.execute(
            select(UserModel).where(UserModel.username == login_data.username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # 驗證密碼
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        # 檢查使用者是否啟用
        if not user.is_active:
            return None
        
        return user
    
    async def create_tokens(
        self, 
        user: UserModel, 
        user_agent: Optional[str] = None, 
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        """
        建立認證令牌
        
        Args:
            user: 使用者模型
            user_agent: 使用者代理字串
            ip_address: IP 位址
            
        Returns:
            TokenResponse: 令牌回應
        """
        # 建立存取令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # 建立刷新令牌
        refresh_token = create_refresh_token()
        refresh_token_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        # 儲存刷新令牌到資料庫
        db_refresh_token = RefreshTokenModel(
            token=refresh_token,
            user_id=user.id,
            expires_at=refresh_token_expires,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        
        self.db.add(db_refresh_token)
        
        # 更新使用者最後登入時間
        await self.db.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(last_login_at=datetime.utcnow())
        )
        
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """
        使用刷新令牌更新存取令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            Optional[TokenResponse]: 新的令牌回應，失敗時回傳 None
        """
        # 查找有效的刷新令牌
        result = await self.db.execute(
            select(RefreshTokenModel)
            .where(
                RefreshTokenModel.token == refresh_token,
                RefreshTokenModel.is_active == True,
                RefreshTokenModel.expires_at > datetime.utcnow()
            )
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            return None
        
        # 取得使用者
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == db_token.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # 建立新的存取令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # 保持原刷新令牌
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        撤銷刷新令牌
        
        Args:
            refresh_token: 要撤銷的刷新令牌
            
        Returns:
            bool: 是否成功撤銷
        """
        result = await self.db.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token == refresh_token)
            .values(
                is_active=False,
                revoked_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        撤銷使用者的所有刷新令牌
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            int: 撤銷的令牌數量
        """
        result = await self.db.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.is_active == True
            )
            .values(
                is_active=False,
                revoked_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return result.rowcount
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserModel]:
        """
        更新使用者資料
        
        Args:
            user_id: 使用者 ID
            user_data: 更新資料
            
        Returns:
            Optional[UserModel]: 更新後的使用者模型
            
        Raises:
            ValueError: 電子郵件已存在時
        """
        # 檢查使用者是否存在
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None
        
        # 檢查電子郵件是否已被其他使用者使用
        if user_data.email and user_data.email != user.email:
            result = await self.db.execute(
                select(UserModel).where(
                    UserModel.email == user_data.email,
                    UserModel.id != user_id
                )
            )
            if result.scalar_one_or_none():
                raise ValueError(f"電子郵件 '{user_data.email}' 已存在")
        
        # 更新使用者資料
        update_data = user_data.dict(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(user)
        
        return user
    
    async def change_password(
        self, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        變更使用者密碼
        
        Args:
            user_id: 使用者 ID
            current_password: 目前密碼
            new_password: 新密碼
            
        Returns:
            bool: 是否成功變更
        """
        # 取得使用者
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        
        # 驗證目前密碼
        if not verify_password(current_password, user.hashed_password):
            return False
        
        # 更新密碼
        new_hashed_password = get_password_hash(new_password)
        await self.db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        await self.db.commit()
        
        # 撤銷所有刷新令牌（強制重新登入）
        await self.revoke_all_user_tokens(user_id)
        
        return True
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """
        根據 ID 取得使用者
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            Optional[UserModel]: 使用者模型
        """
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """
        根據使用者名稱取得使用者
        
        Args:
            username: 使用者名稱
            
        Returns:
            Optional[UserModel]: 使用者模型
        """
        result = await self.db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> Tuple[list[UserModel], int]:
        """
        取得使用者列表
        
        Args:
            skip: 跳過筆數
            limit: 限制筆數
            
        Returns:
            Tuple[list[UserModel], int]: 使用者列表和總數
        """
        # 取得使用者列表
        result = await self.db.execute(
            select(UserModel)
            .order_by(UserModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()
        
        # 取得總數
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(UserModel.id))
        )
        total = result.scalar()
        
        return list(users), total