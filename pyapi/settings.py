# pyapi/settings.py - 應用程式設定配置
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """應用程式設定類別"""
    
    # 設定配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'  # 忽略額外的環境變數
    )
    
    # ==================== 基本設定 ====================
    app_name: str = Field(default="PyAPI", env="APP_NAME", description="應用程式名稱")
    environment: str = Field(default="development", env="ENVIRONMENT", description="執行環境")
    debug: bool = Field(default=True, env="DEBUG", description="除錯模式")
    
    # 伺服器設定
    host: str = Field(default="0.0.0.0", env="HOST", description="伺服器主機")
    port: int = Field(default=8000, env="PORT", description="伺服器埠號")
    reload: bool = Field(default=True, env="RELOAD", description="自動重載")
    
    # ==================== 資料庫設定 ====================
    db_host: str = Field(default="localhost", env="DB_HOST", description="資料庫主機")
    db_port: int = Field(default=5432, env="DB_PORT", description="資料庫埠號")
    db_user: str = Field(default="postgres", env="DB_USER", description="資料庫使用者")
    db_password: str = Field(default="postgres", env="DB_PASSWORD", description="資料庫密碼")
    db_name: str = Field(default="pyapi", env="DB_NAME", description="資料庫名稱")
    
    # 連線池設定
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE", description="連線池大小")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW", description="最大溢出連線")
    db_echo: bool = Field(default=False, env="DB_ECHO", description="顯示 SQL 查詢")
    
    @property
    def database_url(self) -> str:
        """生成資料庫連線 URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # ==================== Redis 設定 ====================
    redis_host: str = Field(default="localhost", env="REDIS_HOST", description="Redis 主機")
    redis_port: int = Field(default=6379, env="REDIS_PORT", description="Redis 埠號")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD", description="Redis 密碼")
    redis_db: int = Field(default=0, env="REDIS_DB", description="Redis 資料庫編號")
    
    @property
    def redis_url(self) -> str:
        """生成 Redis 連線 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ==================== 安全設定 ====================
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY", description="加密密鑰")
    
    # JWT 設定
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES", description="存取令牌過期時間（分鐘）")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS", description="刷新令牌過期時間（天）")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM", description="JWT 演算法")
    
    # CORS 設定
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"],
        env="CORS_ORIGINS",
        description="允許的 CORS 來源"
    )
    
    # ==================== 日誌設定 ====================
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="日誌級別")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT", description="日誌格式")
    log_file: Optional[str] = Field(default="logs/app.log", env="LOG_FILE", description="日誌檔案路徑")
    
    # ==================== API 文件設定 ====================
    docs_url: Optional[str] = Field(default="/docs", env="DOCS_URL", description="Swagger 文件 URL")
    redoc_url: Optional[str] = Field(default="/redoc", env="REDOC_URL", description="ReDoc 文件 URL")
    
    # ==================== 其他設定 ====================
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE", description="最大檔案大小 (bytes)")
    timezone: str = Field(default="Asia/Taipei", env="TIMEZONE", description="時區設定")


@lru_cache()
def get_settings() -> Settings:
    """
    取得應用程式設定 (使用快取)
    
    Returns:
        Settings: 設定物件
    """
    return Settings()


# 建立全域設定實例供其他模組匯入
settings = get_settings()