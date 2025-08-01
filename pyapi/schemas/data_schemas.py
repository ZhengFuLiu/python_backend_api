# pyapi/schemas/data_schemas.py - Pydantic 資料驗證模型
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class DataBase(BaseModel):
    """資料基礎模型"""
    name: str = Field(..., min_length=1, max_length=255, description="資料名稱")
    description: Optional[str] = Field(None, max_length=1000, description="資料描述")
    config: Optional[Dict[str, Any]] = Field(None, description="配置參數 (JSON 格式)")
    status: str = Field(default="active", description="資料狀態")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """驗證狀態值"""
        allowed_statuses = ["active", "inactive", "pending", "completed"]
        if v not in allowed_statuses:
            raise ValueError(f"狀態必須是以下之一: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """驗證名稱不能為空"""
        if not v or not v.strip():
            raise ValueError("名稱不能為空")
        return v.strip()


class DataCreate(DataBase):
    """建立資料的請求模型"""
    pass


class DataUpdate(BaseModel):
    """更新資料的請求模型 (部分更新)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="資料名稱")
    description: Optional[str] = Field(None, max_length=1000, description="資料描述")
    config: Optional[Dict[str, Any]] = Field(None, description="配置參數")
    status: Optional[str] = Field(None, description="資料狀態")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """驗證狀態值"""
        if v is not None:
            allowed_statuses = ["active", "inactive", "pending", "completed"]
            if v not in allowed_statuses:
                raise ValueError(f"狀態必須是以下之一: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """驗證名稱不能為空"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("名稱不能為空")
            return v.strip()
        return v


class DataResponse(BaseModel):
    """資料回應模型"""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: int = Field(..., description="資料 ID")
    name: str = Field(..., description="資料名稱")
    description: Optional[str] = Field(None, description="資料描述")
    config: Optional[Dict[str, Any]] = Field(None, description="配置參數")
    status: str = Field(..., description="資料狀態")
    created_at: datetime = Field(..., description="建立時間")
    updated_at: datetime = Field(..., description="更新時間")
    message: Optional[str] = Field(None, description="回應訊息")


class DataListResponse(BaseModel):
    """資料列表回應模型"""
    data: List[DataResponse] = Field(..., description="資料列表")
    total: int = Field(..., description="總筆數")
    skip: int = Field(..., description="跳過筆數")
    limit: int = Field(..., description="限制筆數")
    message: Optional[str] = Field(None, description="回應訊息")


class DataQuery(BaseModel):
    """資料查詢參數模型"""
    skip: int = Field(default=0, ge=0, description="跳過筆數")
    limit: int = Field(default=100, ge=1, le=1000, description="限制筆數")
    status: Optional[str] = Field(None, description="狀態篩選")
    name_search: Optional[str] = Field(None, min_length=1, description="名稱搜尋")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """驗證狀態值"""
        if v is not None:
            allowed_statuses = ["active", "inactive", "pending", "completed"]
            if v not in allowed_statuses:
                raise ValueError(f"狀態必須是以下之一: {', '.join(allowed_statuses)}")
        return v


# 範例資料模型 (用於 API 文件展示)
class DataCreateExample(DataCreate):
    """建立資料的範例模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "ETL 資料處理任務",
                "description": "每日資料同步處理",
                "config": {
                    "source": "postgresql://user:pass@host:5432/db",
                    "target": "s3://bucket/path/",
                    "schedule": "0 9 * * *",
                    "batch_size": 1000,
                    "retry_count": 3
                },
                "status": "active"
            }
        }
    )


class DataUpdateExample(DataUpdate):
    """更新資料的範例模型"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "更新後的任務名稱",
                "description": "更新後的描述",
                "config": {
                    "schedule": "0 10 * * *",
                    "batch_size": 2000
                },
                "status": "inactive"
            }
        }
    )