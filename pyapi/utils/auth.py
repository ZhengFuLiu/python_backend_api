# pyapi/utils/auth.py - 認證工具模組
from datetime import datetime, timedelta
from typing import Optional, Union
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from pyapi.settings import settings

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthUtils:
    """認證工具類別"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        驗證密碼
        
        Args:
            plain_password: 明文密碼
            hashed_password: 雜湊密碼
            
        Returns:
            bool: 密碼是否正確
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        取得密碼雜湊值
        
        Args:
            password: 明文密碼
            
        Returns:
            str: 雜湊密碼
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        建立存取令牌
        
        Args:
            data: 要編碼的資料
            expires_delta: 過期時間差
            
        Returns:
            str: JWT 令牌
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token() -> str:
        """
        建立刷新令牌
        
        Returns:
            str: 刷新令牌
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        驗證並解碼令牌
        
        Args:
            token: JWT 令牌
            
        Returns:
            dict: 解碼後的資料
            
        Raises:
            HTTPException: 令牌無效時
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無法驗證憑證",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            return payload
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        解碼令牌（不拋出異常）
        
        Args:
            token: JWT 令牌
            
        Returns:
            Optional[dict]: 解碼後的資料，失敗時回傳 None
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        檢查令牌是否過期
        
        Args:
            token: JWT 令牌
            
        Returns:
            bool: 是否過期
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp) < datetime.utcnow()
            return True
        except JWTError:
            return True


# 便利函數
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼的便利函數"""
    return AuthUtils.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """取得密碼雜湊值的便利函數"""
    return AuthUtils.get_password_hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """建立存取令牌的便利函數"""
    return AuthUtils.create_access_token(data, expires_delta)


def create_refresh_token() -> str:
    """建立刷新令牌的便利函數"""
    return AuthUtils.create_refresh_token()


def verify_token(token: str) -> dict:
    """驗證令牌的便利函數"""
    return AuthUtils.verify_token(token)