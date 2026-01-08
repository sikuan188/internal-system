#!/bin/bash

# ========================================
# 培正中學員工管理系統 - 管理員Token設置腳本
# PCMS Staff Management System - Admin Token Setup Script
# ========================================

set -e  # 遇到錯誤立即停止

echo "========================================="
echo "    培正中學員工管理系統"
echo "    管理員Token重新生成腳本"
echo "========================================="

# 預設配置
DEFAULT_ADMIN_USERNAME="adminkuan"
DEFAULT_ADMIN_PASSWORD="admin-Kuan"
DOCKER_COMPOSE_FILE="docker-compose-simple.yml"

# 檢查Docker環境
check_docker_environment() {
    echo "檢查Docker環境..."
    if ! command -v docker &> /dev/null; then
        echo "❌ 錯誤: Docker未安裝"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ 錯誤: Docker Compose未安裝"
        exit 1
    fi
    
    # 檢查容器是否運行
    if ! docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "pcms_staff_backend.*running"; then
        echo "❌ 錯誤: 後端容器未運行"
        echo "請先啟動系統: docker-compose -f $DOCKER_COMPOSE_FILE up -d"
        exit 1
    fi
    
    echo "✅ Docker環境檢查通過"
}

# 等待數據庫就緒
wait_for_database() {
    echo "等待數據庫服務就緒..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py check --database default &>/dev/null; then
            echo "✅ 數據庫連接成功"
            return 0
        fi
        
        echo "⏳ 等待數據庫... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ 錯誤: 數據庫連接失敗"
    exit 1
}

# 創建或更新管理員用戶
setup_admin_user() {
    local username="${1:-$DEFAULT_ADMIN_USERNAME}"
    local password="${2:-$DEFAULT_ADMIN_PASSWORD}"
    
    echo "設置管理員用戶: $username"
    
    # 使用Django shell創建或更新管理員
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py shell <<EOF
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

try:
    # 檢查用戶是否存在
    user, created = User.objects.get_or_create(
        username='$username',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'email': 'admin@puichingcoloane.edu.mo'
        }
    )
    
    # 設置密碼
    user.set_password('$password')
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    # 刪除舊Token，創建新Token
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    
    if created:
        print(f"✅ 創建新管理員用戶: {user.username}")
    else:
        print(f"✅ 更新現有管理員用戶: {user.username}")
    
    print(f"🔑 新Token: {token.key}")
    print(f"👤 用戶名: {user.username}")
    print(f"🔐 密碼: $password")
    
except Exception as e:
    print(f"❌ 錯誤: {str(e)}")
    exit(1)
EOF
}

# 驗證Token
verify_token() {
    echo "驗證Token..."
    
    # 獲取Token
    local token=$(docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py shell -c "
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
user = User.objects.get(username='$DEFAULT_ADMIN_USERNAME')
token = Token.objects.get(user=user)
print(token.key)
" 2>/dev/null | tr -d '[:space:]')
    
    if [ -z "$token" ]; then
        echo "❌ 錯誤: 無法獲取Token"
        return 1
    fi
    
    # 測試API訪問
    local api_response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Token $token" \
        "http://localhost:8000/api/staff/profiles/" 2>/dev/null)
    
    if [ "$api_response" = "200" ]; then
        echo "✅ Token驗證成功"
        echo "🔑 當前Token: $token"
        return 0
    else
        echo "❌ Token驗證失敗 (HTTP狀態碼: $api_response)"
        return 1
    fi
}

# 顯示登錄信息
show_login_info() {
    echo ""
    echo "========================================="
    echo "          系統登錄信息"
    echo "========================================="
    echo "🌐 前端地址: http://localhost:3000/"
    echo "🛠️  管理後台: http://localhost:8000/admin/"
    echo "👤 管理員用戶名: $DEFAULT_ADMIN_USERNAME"
    echo "🔐 管理員密碼: $DEFAULT_ADMIN_PASSWORD"
    echo ""
    echo "⚠️  生產環境部署後請立即修改預設密碼！"
    echo ""
    echo "🔧 使用 ./change_mysql_password.sh 腳本修改數據庫密碼"
    echo "========================================="
}

# 主函數
main() {
    local username=""
    local password=""
    
    # 解析命令行參數
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--username)
                username="$2"
                shift 2
                ;;
            -p|--password)
                password="$2"
                shift 2
                ;;
            -h|--help)
                echo "用法: $0 [選項]"
                echo "選項:"
                echo "  -u, --username STRING  指定管理員用戶名 (預設: $DEFAULT_ADMIN_USERNAME)"
                echo "  -p, --password STRING  指定管理員密碼 (預設: $DEFAULT_ADMIN_PASSWORD)"
                echo "  -h, --help             顯示幫助信息"
                echo ""
                echo "範例:"
                echo "  $0                           # 使用預設設置"
                echo "  $0 -u admin -p newpassword  # 自定義用戶名和密碼"
                exit 0
                ;;
            *)
                echo "❌ 未知選項: $1"
                echo "使用 $0 --help 查看幫助"
                exit 1
                ;;
        esac
    done
    
    # 使用預設值（如果未指定）
    username="${username:-$DEFAULT_ADMIN_USERNAME}"
    password="${password:-$DEFAULT_ADMIN_PASSWORD}"
    
    echo "開始設置管理員Token..."
    echo "用戶名: $username"
    echo ""
    
    # 執行設置步驟
    check_docker_environment
    wait_for_database
    setup_admin_user "$username" "$password"
    verify_token
    show_login_info
    
    echo "✅ Token設置完成！"
}

# 當腳本被直接執行時運行main函數
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi