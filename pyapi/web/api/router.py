# pyapi/web/api/router.py - 主要 API 路由
from fastapi.routing import APIRouter

from pyapi.web.api import docs, monitoring
from pyapi.web.api.data import router as data_router
from pyapi.web.api.auth import router as auth_router

api_router = APIRouter()

# 包含各個子模組的路由
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(auth_router, prefix="/auth", tags=["認證"])
api_router.include_router(data_router, prefix="/data", tags=["資料管理"])