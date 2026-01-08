#!/bin/bash
# PCMS Staff Management System - Production Docker Entry Point
# 培正中學員工管理系統 - 生產環境Docker入口腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏫 培正中學員工管理系統 - 生產環境啟動${NC}"
echo -e "${BLUE}PCMS Staff Management System - Production Environment Starting${NC}"

# 驗證生產環境必需的環境變量
echo -e "${BLUE}🔍 檢查生產環境配置...${NC}"

required_vars=("SECRET_KEY" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ 缺少必需的環境變量: $var${NC}"
        exit 1
    fi
done

# 確保DEBUG=False
if [ "$DEBUG" = "True" ]; then
    echo -e "${RED}❌ 生產環境不應該啟用DEBUG模式${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 生產環境配置檢查通過${NC}"

# 等待數據庫準備就緒
if [ "$DATABASE_URL" ] && [[ "$DATABASE_URL" =~ ^postgresql:// ]]; then
    echo -e "${YELLOW}⏳ 等待PostgreSQL數據庫準備就緒...${NC}"
    
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    timeout=60
    count=0
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        if [ $count -ge $timeout ]; then
            echo -e "${RED}❌ 數據庫連接超時${NC}"
            exit 1
        fi
        echo -e "${YELLOW}數據庫尚未準備就緒，等待中... ($count/$timeout)${NC}"
        sleep 2
        count=$((count + 2))
    done
    echo -e "${GREEN}✅ 數據庫已準備就緒${NC}"
fi

# 創建必要目錄
echo -e "${BLUE}📁 創建必要目錄...${NC}"
mkdir -p /app/staticfiles /app/media /app/logs /app/db/sqlitedb

# 運行數據庫遷移
echo -e "${BLUE}🗄️ 運行數據庫遷移...${NC}"
if python manage.py migrate --noinput; then
    echo -e "${GREEN}✅ 數據庫遷移完成${NC}"
else
    echo -e "${RED}❌ 數據庫遷移失敗${NC}"
    exit 1
fi

# 收集靜態文件
echo -e "${BLUE}📁 收集靜態文件...${NC}"
if python manage.py collectstatic --noinput; then
    echo -e "${GREEN}✅ 靜態文件收集完成${NC}"
else
    echo -e "${RED}❌ 靜態文件收集失敗${NC}"
    exit 1
fi

# 運行生產環境檢查
echo -e "${BLUE}🔍 運行生產環境檢查...${NC}"
if python manage.py check --deploy --fail-level WARNING; then
    echo -e "${GREEN}✅ 生產環境檢查通過${NC}"
else
    echo -e "${RED}❌ 生產環境檢查失敗${NC}"
    exit 1
fi

# 創建初始超級用戶（如果指定）
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo -e "${BLUE}👤 檢查超級用戶...${NC}"
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('✅ 超級用戶創建完成')
else:
    print('ℹ️ 超級用戶已存在')
" || echo -e "${YELLOW}⚠️ 超級用戶創建跳過${NC}"
fi

echo -e "${GREEN}🚀 生產環境準備就緒，啟動Gunicorn服務器...${NC}"
echo -e "${BLUE}Production environment ready, starting Gunicorn server...${NC}"

# 執行傳入的命令
exec "$@"