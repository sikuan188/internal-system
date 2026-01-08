#!/bin/bash
# PCMS Staff Management System - Docker Entry Point
# 培正中學員工管理系統 - Docker 入口腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏫 培正中學員工管理系統 - 後端服務啟動${NC}"
echo -e "${BLUE}PCMS Staff Management System - Backend Service Starting${NC}"

# 等待數據庫準備就緒（如果使用外部數據庫）
if [ "$DATABASE_URL" ] && [[ "$DATABASE_URL" =~ ^postgresql:// ]]; then
    echo -e "${YELLOW}⏳ 等待PostgreSQL數據庫準備就緒...${NC}"
    
    # 從DATABASE_URL中提取主機和端口
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        echo -e "${YELLOW}數據庫尚未準備就緒，等待中...${NC}"
        sleep 2
    done
    echo -e "${GREEN}✅ PostgreSQL數據庫已準備就緒${NC}"
fi

# 等待MySQL數據庫準備就緒（如果使用MySQL）
if [ "$DB_ENGINE" = "mysql" ]; then
    echo -e "${YELLOW}⏳ 等待MySQL數據庫準備就緒...${NC}"
    
    # 使用Docker容器名稱和默認端口
    DB_HOST="pcms_staff_mysql"
    DB_PORT="3306"
    
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        echo -e "${YELLOW}MySQL數據庫尚未準備就緒，等待中...${NC}"
        sleep 3
    done
    echo -e "${GREEN}✅ MySQL數據庫已準備就緒${NC}"
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
    echo -e "${YELLOW}⚠️ 靜態文件收集跳過（可能是開發環境）${NC}"
fi

# 檢查是否需要創建超級用戶
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo -e "${BLUE}👤 檢查超級用戶...${NC}"
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('✅ 超級用戶創建完成')
else:
    print('ℹ️ 超級用戶已存在')
" || echo -e "${YELLOW}⚠️ 超級用戶創建失敗或已存在${NC}"
fi

# 運行系統檢查
echo -e "${BLUE}🔍 運行系統檢查...${NC}"
if python manage.py check --deploy; then
    echo -e "${GREEN}✅ 系統檢查通過${NC}"
else
    echo -e "${YELLOW}⚠️ 系統檢查發現警告（可能是開發環境）${NC}"
fi

echo -e "${GREEN}🚀 後端服務準備就緒，啟動中...${NC}"
echo -e "${BLUE}Backend service ready, starting...${NC}"

# 執行傳入的命令
exec "$@"