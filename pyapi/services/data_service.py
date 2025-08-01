# pyapi/services/data_service.py - 資料處理服務
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from pyapi.db.dao import DataDAO
from pyapi.db.models import DataModel
from pyapi.schemas.data_schemas import DataCreate, DataUpdate


class DataService:
    """
    資料處理服務層
    
    負責處理業務邏輯和資料驗證
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.data_dao = DataDAO(session)
    
    async def create_data(self, data: DataCreate) -> DataModel:
        """
        建立新資料
        
        Args:
            data: 要建立的資料
            
        Returns:
            DataModel: 建立的資料模型
            
        Raises:
            ValueError: 當資料驗證失敗時
        """
        # 檢查名稱是否已存在
        existing_data = await self.data_dao.get_by_name(data.name)
        if existing_data:
            raise ValueError(f"名稱 '{data.name}' 已存在")
        
        # 建立資料
        return await self.data_dao.create(data)
    
    async def update_data(self, data_id: int, data: DataUpdate) -> Optional[DataModel]:
        """
        更新資料
        
        Args:
            data_id: 要更新的資料 ID
            data: 更新的資料內容
            
        Returns:
            Optional[DataModel]: 更新後的資料模型，若不存在則回傳 None
            
        Raises:
            ValueError: 當資料驗證失敗時
        """
        # 檢查資料是否存在
        existing_data = await self.data_dao.get_by_id(data_id)
        if not existing_data:
            return None
        
        # 如果要更新名稱，檢查新名稱