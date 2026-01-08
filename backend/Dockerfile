# PCMS Staff Management System - Backend Dockerfile
# 培正中學員工管理系統 - 後端Docker文件
# 
# 多階段構建：開發環境和生產環境
# Multi-stage build: development and production environments

# =================================================================
# 基礎鏡像 - Base Image
# =================================================================
FROM python:3.11-slim-bullseye as base

# 設置環境變量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=pcms_staff.settings

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    libmariadb-dev \
    pkg-config \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# 創建非root用戶
RUN groupadd -r django && useradd -r -g django django

# =================================================================
# 開發環境階段 - Development Stage  
# =================================================================
FROM base as development

# 安裝開發工具
RUN apt-get update && apt-get install -y \
    sqlite3 \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 複製requirements文件
COPY requirements.txt /app/

# 安裝Python依賴
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 複製項目文件
COPY . /app/

# 創建必要目錄並設置權限
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/db/sqlitedb && \
    chown -R django:django /app

# 收集靜態文件腳本
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 暴露端口
EXPOSE 8000

# 切換到非root用戶
USER django

# 設置入口點
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =================================================================
# 生產環境階段 - Production Stage
# =================================================================
FROM base as production

# 複製requirements文件
COPY requirements.txt /app/

# 安裝生產依賴（不包含開發工具）
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# 複製項目文件
COPY . /app/

# 創建必要目錄並設置權限
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/db/sqlitedb && \
    chown -R django:django /app

# 收集靜態文件
RUN python manage.py collectstatic --noinput || true

# 複製生產環境入口腳本
COPY docker-entrypoint-prod.sh /app/
RUN chmod +x /app/docker-entrypoint-prod.sh

# 暴露端口
EXPOSE 8000

# 切換到非root用戶
USER django

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 設置生產環境入口點
ENTRYPOINT ["/app/docker-entrypoint-prod.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "pcms_staff.wsgi:application"]