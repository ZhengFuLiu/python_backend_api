# 依賴安裝階段
FROM python:3.11.4-slim-bullseye AS deps

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN pip install uv

# 設定工作目錄
WORKDIR /app

# 複製依賴檔案
COPY pyproject.toml ./

# 生產環境依賴
FROM deps AS prod-deps
RUN uv sync --no-dev

# 開發環境依賴
FROM deps AS dev-deps
RUN uv sync --dev

# 生產環境映像
FROM python:3.11.4-slim-bullseye AS prod

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 安裝最小運行時依賴
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 建立應用程式使用者
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 設定工作目錄
WORKDIR /app

# 從依賴階段複製虛擬環境
COPY --from=prod-deps /app/.venv /app/.venv

# 複製應用程式碼
COPY . .

# 設定檔案擁有者
RUN chown -R appuser:appuser /app

# 切換到非 root 使用者
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/monitoring/health || exit 1

# 暴露埠號
EXPOSE 8000

# 啟動命令
CMD ["python", "-m", "pyapi"]

# 開發環境映像
FROM python:3.11.4-slim-bullseye AS dev

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN pip install uv

# 建立開發使用者
RUN groupadd -r devuser && useradd -r -g devuser devuser

# 設定工作目錄
WORKDIR /app

# 從開發依賴階段複製虛擬環境
COPY --from=dev-deps /app/.venv /app/.venv

# 複製應用程式碼
COPY . .

# 設定檔案擁有者
RUN chown -R devuser:devuser /app

# 切換到開發使用者
USER devuser

# 安裝 pre-commit hooks（如果失敗不影響構建）
RUN uv run pre-commit install || true

# 暴露埠號
EXPOSE 8000

# 開發模式啟動
CMD ["uv", "run", "uvicorn", "pyapi.web.application:get_app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--factory"]