# pyapi/db/dao.py - 資料存取層 (Data Access Object)
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.orm import selectinload

from pyapi.db.models import DataModel
from pyapi.schemas.data_schemas import DataCreate, DataUpdate


class DataDAO:
    """
    資料存取物件
    
    負責所有與 DataModel 相關的資料庫操作
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data_create: DataCreate) -> DataModel:
        """
        建立新資料
        
        Args:
            data_create: 要建立的資料
            
        Returns:
            DataModel: 建立的資料模型
        """
        db_data = DataModel(
            name=data_create.name,
            description=data_create.description,
            config=data_create.config,
            status=data_create.status,
        )
        
        self.session.add(db_data)
        await self.session.commit()
        await self.session.refresh(db_data)
        
        return db_data
    
    async def get_by_id(self, data_id: int) -> Optional[DataModel]:
        """
        根據 ID 取得資料
        
        Args:
            data_id: 資料 ID
            
        Returns:
            Optional[DataModel]: 資料模型，如果不存在則回傳 None
        """
        result = await self.session.execute(
            select(DataModel).where(DataModel.id == data_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[DataModel]:
        """
        根據名稱取得資料
        
        Args:
            name: 資料名稱
            
        Returns:
            Optional[DataModel]: 資料模型，如果不存在則回傳 None
        """
        result = await self.session.execute(
            select(DataModel).where(DataModel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        name_search: Optional[str] = None,
    ) -> List[DataModel]:
        """
        取得資料列表
        
        Args:
            skip: 跳過筆數
            limit: 限制筆數
            status: 狀態篩選
            name_search: 名稱搜尋
            
        Returns:
            List[DataModel]: 資料列表
        """
        query = select(DataModel)
        
        # 加入篩選條件
        conditions = []
        if status:
            conditions.append(DataModel.status == status)
        if name_search:
            conditions.append(DataModel.name.contains(name_search))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 加入排序、分頁
        query = query.order_by(DataModel.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DataModel]:
        """
        根據狀態取得資料列表
        
        Args:
            status: 資料狀態
            skip: 跳過筆數
            limit: 限制筆數
            
        Returns:
            List[DataModel]: 資料列表
        """
        result = await self.session.execute(
            select(DataModel)
            .where(DataModel.status == status)
            .order_by(DataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, data_id: int, data_update: DataUpdate) -> Optional[DataModel]:
        """
        更新資料
        
        Args:
            data_id: 要更新的資料 ID
            data_update: 更新內容
            
        Returns:
            Optional[DataModel]: 更新後的資料模型，如果不存在則回傳 None
        """
        # 先取得資料
        existing_data = await self.get_by_id(data_id)
        if not existing_data:
            return None
        
        # 準備更新資料
        update_data = data_update.dict(exclude_unset=True)
        if not update_data:
            return existing_data
        
        # 執行更新
        await self.session.execute(
            update(DataModel)
            .where(DataModel.id == data_id)
            .values(**update_data)
        )
        await self.session.commit()
        
        # 重新取得更新後的資料
        return await self.get_by_id(data_id)
    
    async def delete(self, data_id: int) -> bool:
        """
        刪除資料
        
        Args:
            data_id: 要刪除的資料 ID
            
        Returns:
            bool: 是否成功刪除
        """
        result = await self.session.execute(
            delete(DataModel).where(DataModel.id == data_id)
        )
        await self.session.commit()
        
        return result.rowcount > 0
    
    async def count(
        self,
        status: Optional[str] = None,
        name_search: Optional[str] = None,
    ) -> int:
        """
        計算資料總數
        
        Args:
            status: 狀態篩選
            name_search: 名稱搜尋
            
        Returns:
            int: 資料總數
        """
        query = select(func.count(DataModel.id))
        
        # 加入篩選條件
        conditions = []
        if status:
            conditions.append(DataModel.status == status)
        if name_search:
            conditions.append(DataModel.name.contains(name_search))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def exists(self, data_id: int) -> bool:
        """
        檢查資料是否存在
        
        Args:
            data_id: 資料 ID
            
        Returns:
            bool: 是否存在
        """
        result = await self.session.execute(
            select(func.count(DataModel.id)).where(DataModel.id == data_id)
        )
        count = result.scalar()
        return count > 0