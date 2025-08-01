# PyAPI - FastAPI ETL 排程管理 API

🚀 基於 FastAPI 的 ETL 排程管理後端 API，具備完整的 JWT 認證系統，與 Apache Airflow 共享 PostgreSQL 資料庫。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![uv](https://img.shields.io/badge/uv-package%20manager-orange.svg)](https://github.com/astral-sh/uv)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-compatible-blue.svg)](https://postgresql.org)

## ✨ 功能特色

- 🔄 **資料管理**: 接收前端資料並安全存儲至 PostgreSQL
- 🔐 **JWT 認證**: 完整的使用者註冊、登入、權限管理
- 🔗 **Airflow 整合**: 與 Apache Airflow 共享 PostgreSQL 資料庫
- ⚡ **高效能**: 全異步架構，支援高併發處理
- 📊 **即時監控**: 健康檢查、系統監控端點
- 📚 **自動文件**: Swagger UI 和 ReDoc 自動生成
- 🐳 **容器化**: 完整的 Docker 部署支援
- 🧪 **測試覆蓋**: 完整的測試套件和程式碼品質檢查

## 📁 專案結構

```
pyapi/
├── pyapi/                          # 主要應用程式套件
│   ├── __main__.py                 # 應用程式入口點
│   ├── settings.py                 # 設定配置
│   ├── log.py                     # 日誌配置
│   ├── gunicorn_runner.py         # Gunicorn 執行器
│   │
│   ├── web/                       # Web 層
│   │   ├── application.py         # FastAPI 應用程式
│   │   ├── lifespan.py           # 應用程式生命週期
│   │   └── api/                   # API 路由
│   │       ├── router.py          # 主要路由
│   │       ├── auth.py            # 認證 API
│   │       ├── data.py            # 資料管理 API
│   │       ├── docs.py            # API 文件
│   │       └── monitoring.py      # 監控端點
│   │
│   ├── db/                        # 資料庫層
│   │   ├── meta.py                # 資料庫 Metadata
│   │   ├── models.py              # 資料庫模型
│   │   ├── auth_models.py         # 認證資料模型
│   │   ├── dao.py                 # 資料存取層
│   │   └── dependencies.py        # 資料庫依賴注入
│   │
│   ├── services/                  # 業務邏輯層
│   │   ├── auth_service.py        # 認證業務邏輯
│   │   └── data_service.py        # 資料處理業務邏輯
│   │
│   ├── schemas/                   # 資料驗證層
│   │   ├── auth_schemas.py        # 認證 Pydantic 模型
│   │   └── data_schemas.py        # 資料 Pydantic 模型
│   │
│   └── utils/                     # 工具模組
│       ├── auth.py                # JWT 工具函數
│       └── dependencies.py        # 認證依賴注入
│
├── tests/                         # 測試套件
├── deployment/                    # 部署配置
│   ├── docker-compose.yml        # Docker Compose
│   └── Dockerfile                # Docker 映像檔
├── pyproject.toml                 # uv 依賴管理
├── .env.example                   # 環境變數範例
├── .gitignore                     # Git 忽略檔案
└── README.md                      # 專案說明
```

## 🚀 快速啟用

### 系統需求

- Python 3.10+
- PostgreSQL 12+
- [uv](https://github.com/astral-sh/uv) 套件管理器

### 安裝 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 1. 專案設定

```bash
# 克隆專案
git clone <your-repo-url>
cd pyapi

# 安裝依賴 (包含開發工具)
uv sync --extra dev

# 複製環境變數檔案
cp .env.example .env
```

### 2. 環境變數設定

編輯 `.env` 檔案：

```bash
# 應用程式設定
PYAPI_HOST=127.0.0.1
PYAPI_PORT=8000
PYAPI_ENVIRONMENT=dev
PYAPI_LOG_LEVEL=INFO

# 資料庫設定 (與 Airflow 共享)
DATABASE_URL=postgresql+asyncpg://airflow:airflow@localhost:5432/airflow

# JWT 認證設定
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
PYAPI_ACCESS_TOKEN_EXPIRE_MINUTES=30
PYAPI_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. 啟動應用程式

```bash
# 開發模式
uv run python -m pyapi

# 或使用 uvicorn
uv run uvicorn pyapi.web.application:get_app --reload --host 0.0.0.0 --port 8000
```

### 4. 訪問 API

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **健康檢查**: http://localhost:8000/api/health

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 啟動完整堆疊 (包含 PostgreSQL)
docker-compose up -d

# 查看日誌
docker-compose logs -f pyapi

# 停止服務
docker-compose down
```

### 僅啟動應用程式

```bash
# 建構映像檔
docker build -t pyapi .

# 執行容器
docker run -p 8000:8000 --env-file .env pyapi
```

## 🌐 API 端點

### 認證相關

| 方法 | 路徑 | 功能 | 認證 |
|------|------|------|------|
| `POST` | `/api/auth/register` | 註冊新使用者 | ❌ |
| `POST` | `/api/auth/login` | 使用者登入 | ❌ |
| `POST` | `/api/auth/refresh` | 刷新存取令牌 | ❌ |
| `POST` | `/api/auth/logout` | 使用者登出 | ✅ |
| `GET` | `/api/auth/me` | 取得個人資料 | ✅ |
| `PUT` | `/api/auth/me` | 更新個人資料 | ✅ |
| `POST` | `/api/auth/change-password` | 變更密碼 | ✅ |

### 資料管理

| 方法 | 路徑 | 功能 | 認證 |
|------|------|------|------|
| `POST` | `/api/data/` | 建立新資料 | ✅ |
| `GET` | `/api/data/` | 查詢資料列表 | 🔶 可選 |
| `GET` | `/api/data/{id}` | 查詢特定資料 | 🔶 可選 |
| `PUT` | `/api/data/{id}` | 更新資料 | ✅ |
| `DELETE` | `/api/data/{id}` | 刪除資料 | ✅ |

### 系統監控

| 方法 | 路徑 | 功能 | 認證 |
|------|------|------|------|
| `GET` | `/api/health` | 健康檢查 | ❌ |
| `GET` | `/api/docs` | Swagger UI | ❌ |
| `GET` | `/api/redoc` | ReDoc | ❌ |

## 🐍 Python 使用範例

### 基本設定

```python
import asyncio
import httpx
from typing import Optional

class PyAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def _get_headers(self) -> dict:
        """取得認證標頭"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
```

### 使用者註冊和登入

```python
async def register_and_login():
    """使用者註冊和登入範例"""
    async with httpx.AsyncClient() as client:
        api = PyAPIClient()
        
        # 1. 註冊新使用者
        register_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "SecurePass123",
            "full_name": "John Doe"
        }
        
        response = await client.post(
            f"{api.base_url}/api/auth/register",
            json=register_data,
            headers=api._get_headers()
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"使用者註冊成功: {user['username']}")
        
        # 2. 使用者登入
        login_data = {
            "username": "johndoe",
            "password": "SecurePass123"
        }
        
        response = await client.post(
            f"{api.base_url}/api/auth/login",
            json=login_data,
            headers=api._get_headers()
        )
        
        if response.status_code == 200:
            tokens = response.json()
            api.access_token = tokens["access_token"]
            api.refresh_token = tokens["refresh_token"]
            print("登入成功！")
            return api
        
        return None

# 執行範例
api_client = asyncio.run(register_and_login())
```

### 資料管理操作

```python
async def data_operations():
    """資料 CRUD 操作範例"""
    async with httpx.AsyncClient() as client:
        # 假設已有認證的 API 客戶端
        api = PyAPIClient()
        api.access_token = "your-access-token"
        
        # 1. 建立新資料
        data_payload = {
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
        
        response = await client.post(
            f"{api.base_url}/api/data/",
            json=data_payload,
            headers=api._get_headers()
        )
        
        if response.status_code == 201:
            created_data = response.json()
            data_id = created_data["id"]
            print(f"資料建立成功，ID: {data_id}")
        
        # 2. 查詢資料列表
        response = await client.get(
            f"{api.base_url}/api/data/?skip=0&limit=10&status=active",
            headers=api._get_headers()
        )
        
        if response.status_code == 200:
            data_list = response.json()
            print(f"查詢到 {data_list['total']} 筆資料")
            for item in data_list["data"]:
                print(f"- {item['name']} (ID: {item['id']})")
        
        # 3. 取得特定資料
        response = await client.get(
            f"{api.base_url}/api/data/{data_id}",
            headers=api._get_headers()
        )
        
        if response.status_code == 200:
            data_detail = response.json()
            print(f"資料詳情: {data_detail['name']}")
        
        # 4. 更新資料
        update_payload = {
            "description": "更新後的描述",
            "status": "inactive"
        }
        
        response = await client.put(
            f"{api.base_url}/api/data/{data_id}",
            json=update_payload,
            headers=api._get_headers()
        )
        
        if response.status_code == 200:
            updated_data = response.json()
            print(f"資料更新成功: {updated_data['name']}")
        
        # 5. 刪除資料
        response = await client.delete(
            f"{api.base_url}/api/data/{data_id}",
            headers=api._get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"刪除成功: {result['message']}")

# 執行範例
asyncio.run(data_operations())
```

### 完整使用範例

```python
import asyncio
import httpx
from typing import Optional

class PyAPIManager:
    """PyAPI 管理客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def login(self, username: str, password: str) -> bool:
        """使用者登入"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["access_token"]
                self.refresh_token = tokens["refresh_token"]
                return True
            return False
    
    async def create_etl_job(self, name: str, config: dict) -> Optional[dict]:
        """建立 ETL 作業"""
        async with httpx.AsyncClient() as client:
            payload = {
                "name": name,
                "description": f"ETL 作業: {name}",
                "config": config,
                "status": "active"
            }
            
            response = await client.post(
                f"{self.base_url}/api/data/",
                json=payload,
                headers=self._get_headers()
            )
            
            return response.json() if response.status_code == 201 else None
    
    async def get_jobs(self, status: str = "active") -> list:
        """取得作業列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/data/?status={status}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()["data"]
            return []

async def main():
    """主要示範程式"""
    # 初始化 API 管理器
    api = PyAPIManager()
    
    # 登入 (假設已有使用者)
    if await api.login("admin", "password"):
        print("✅ 登入成功")
        
        # 建立 ETL 作業
        etl_config = {
            "source": {
                "type": "postgresql",
                "host": "localhost",
                "database": "source_db"
            },
            "target": {
                "type": "s3",
                "bucket": "data-lake",
                "prefix": "processed/"
            },
            "schedule": "0 2 * * *",  # 每日凌晨 2 點
            "retries": 3
        }
        
        job = await api.create_etl_job("daily_sync", etl_config)
        if job:
            print(f"✅ ETL 作業建立成功: {job['name']} (ID: {job['id']})")
        
        # 查詢所有活躍作業
        jobs = await api.get_jobs("active")
        print(f"📋 共有 {len(jobs)} 個活躍作業:")
        for job in jobs:
            print(f"   - {job['name']} ({job['status']})")
    
    else:
        print("❌ 登入失敗")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🧪 開發和測試

### 程式碼品質檢查

```bash
# 程式碼格式化
uv run black .
uv run ruff check --fix .

# 型別檢查
uv run mypy pyapi

# 執行測試
uv run pytest

# 測試覆蓋率
uv run pytest --cov=pyapi
```

### 新增依賴

```bash
# 新增一般依賴
uv add package-name

# 新增開發依賴
uv add --dev package-name

# 移除依賴
uv remove package-name
```

## 📊 資料庫結構

### 主要資料表

```sql
-- 資料記錄表
CREATE TABLE pyapi_data_records (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 使用者表
CREATE TABLE pyapi_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 刷新令牌表
CREATE TABLE pyapi_refresh_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 生產環境部署

### 環境變數設定

```bash
# 生產環境設定
export PYAPI_ENVIRONMENT=production
export PYAPI_RELOAD=false
export PYAPI_WORKERS_COUNT=4
export PYAPI_LOG_LEVEL=INFO

# 安全設定
export SECRET_KEY="your-production-secret-key-at-least-32-characters"
export DATABASE_URL="postgresql+asyncpg://user:pass@prod-host:5432/db"
```

### 啟動生產服務

```bash
# 使用 Gunicorn (推薦)
uv run python -m pyapi

# 或手動啟動
uv run gunicorn pyapi.web.application:get_app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000
```
"# python_backend_api" 
"# python_backend_api" 
"# python_backend_api" 
