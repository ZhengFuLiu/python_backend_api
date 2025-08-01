# pyapi/web/api/data.py - 資料管理 API 路由
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from pyapi.db.dao import DataDAO
from pyapi.db.dependencies import get_db_session
from pyapi.schemas.data_schemas import (
    DataCreate,
    DataUpdate, 
    DataResponse,
    DataListResponse
)
from pyapi.services.data_service import DataService

logger = logging.getLogger(__name__)

# 建立路由器
router = APIRouter()


@router.post("/", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
async def create_data(
    data: DataCreate,
    db: AsyncSession = Depends(get_db_session)
) -> DataResponse:
    """
    建立新資料
    
    接收前端傳送的資料並存入 PostgreSQL 資料庫
    """
    try:
        logger.info(f"建立新資料: {data.name}")
        
        # 使用服務層處理業務邏輯
        data_service = DataService(db)
        result = await data_service.create_data(data)
        
        logger.info(f"資料建立成功 - ID: {result.id}")
        
        return DataResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            config=result.config,
            status=result.status,
            created_at=result.created_at,
            updated_at=result.updated_at,
            message="資料建立成功"
        )
        
    except ValueError as e:
        logger.warning(f"資料驗證錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"資料驗證錯誤: {str(e)}"
        )
    except Exception as e:
        logger.error(f"建立資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"建立資料時發生錯誤: {str(e)}"
        )


@router.get("/", response_model=DataListResponse)
async def get_data_list(
    skip: int = Query(default=0, ge=0, description="跳過筆數"),
    limit: int = Query(default=100, ge=1, le=1000, description="限制筆數"),
    status_filter: Optional[str] = Query(default=None, description="狀態篩選"),
    name_search: Optional[str] = Query(default=None, description="名稱搜尋"),
    db: AsyncSession = Depends(get_db_session)
) -> DataListResponse:
    """
    取得資料列表
    
    支援分頁、狀態篩選和名稱搜尋
    """
    try:
        logger.info(f"查詢資料列表 - skip: {skip}, limit: {limit}")
        
        data_dao = DataDAO(db)
        
        # 取得資料列表
        data_list = await data_dao.get_all(
            skip=skip,
            limit=limit,
            status=status_filter,
            name_search=name_search
        )
        
        # 取得總數
        total_count = await data_dao.count(
            status=status_filter,
            name_search=name_search
        )
        
        logger.info(f"查詢完成 - 共 {total_count} 筆資料")
        
        return DataListResponse(
            data=[
                DataResponse(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    config=item.config,
                    status=item.status,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in data_list
            ],
            total=total_count,
            skip=skip,
            limit=limit,
            message="資料查詢成功"
        )
        
    except Exception as e:
        logger.error(f"查詢資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢資料時發生錯誤: {str(e)}"
        )


@router.get("/{data_id}", response_model=DataResponse)
async def get_data_by_id(
    data_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> DataResponse:
    """
    根據 ID 取得特定資料
    """
    try:
        logger.info(f"查詢資料 ID: {data_id}")
        
        data_dao = DataDAO(db)
        data_item = await data_dao.get_by_id(data_id)
        
        if not data_item:
            logger.warning(f"找不到 ID 為 {data_id} 的資料")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到 ID 為 {data_id} 的資料"
            )
        
        logger.info(f"資料查詢成功 - ID: {data_id}")
        
        return DataResponse(
            id=data_item.id,
            name=data_item.name,
            description=data_item.description,
            config=data_item.config,
            status=data_item.status,
            created_at=data_item.created_at,
            updated_at=data_item.updated_at,
            message="資料查詢成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查詢資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢資料時發生錯誤: {str(e)}"
        )


@router.put("/{data_id}", response_model=DataResponse)
async def update_data(
    data_id: int,
    data: DataUpdate,
    db: AsyncSession = Depends(get_db_session)
) -> DataResponse:
    """
    更新指定資料
    """
    try:
        logger.info(f"更新資料 ID: {data_id}")
        
        data_service = DataService(db)
        result = await data_service.update_data(data_id, data)
        
        if not result:
            logger.warning(f"找不到 ID 為 {data_id} 的資料")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到 ID 為 {data_id} 的資料"
            )
        
        logger.info(f"資料更新成功 - ID: {data_id}")
        
        return DataResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            config=result.config,
            status=result.status,
            created_at=result.created_at,
            updated_at=result.updated_at,
            message="資料更新成功"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"資料驗證錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"資料驗證錯誤: {str(e)}"
        )
    except Exception as e:
        logger.error(f"更新資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新資料時發生錯誤: {str(e)}"
        )


@router.delete("/{data_id}")
async def delete_data(
    data_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    刪除指定資料
    """
    try:
        logger.info(f"刪除資料 ID: {data_id}")
        
        data_dao = DataDAO(db)
        
        # 檢查資料是否存在
        existing_data = await data_dao.get_by_id(data_id)
        if not existing_data:
            logger.warning(f"找不到 ID 為 {data_id} 的資料")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到 ID 為 {data_id} 的資料"
            )
        
        # 執行刪除
        await data_dao.delete(data_id)
        
        logger.info(f"資料刪除成功 - ID: {data_id}")
        
        return {
            "message": f"資料 ID {data_id} 已成功刪除",
            "deleted_id": data_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除資料時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除資料時發生錯誤: {str(e)}"
        )