#!/bin/bash

# ========================================
# 培正中學員工管理系統 - 新伺服器部署初始化腳本
# PCMS Staff Management System - New Server Deployment Script
# ========================================

set -e  # 遇到錯誤立即停止

echo "========================================="
echo "    培正中學員工管理系統"
echo "    新伺服器部署初始化腳本"
echo "========================================="

# 配置變量
DOCKER_COMPOSE_FILE="docker-compose-simple.yml"
ADMIN_USERNAME="adminkuan"
ADMIN_PASSWORD="admin-Kuan"
DEFAULT_MYSQL_PASSWORD="pcms_admin"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輸出函數
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# 檢查必要的工具
check_prerequisites() {
    info "檢查部署環境..."
    
    # 檢查Docker
    if ! command -v docker &> /dev/null; then
        error "Docker未安裝，請先安裝Docker"
        echo "安裝指令 (Ubuntu/Debian): sudo apt-get update && sudo apt-get install docker.io"
        echo "安裝指令 (CentOS/RHEL): sudo yum install docker"
        exit 1
    fi
    
    # 檢查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose未安裝，請先安裝Docker Compose"
        echo "安裝指令: sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose"
        echo "然後執行: sudo chmod +x /usr/local/bin/docker-compose"
        exit 1
    fi
    
    # 檢查Docker服務
    if ! systemctl is-active --quiet docker 2>/dev/null && ! pgrep dockerd &>/dev/null; then
        warning "Docker服務未運行，嘗試啟動..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker
        else
            sudo service docker start
        fi
    fi
    
    success "環境檢查完成"
}

# 檢查配置文件
check_configuration() {
    info "檢查配置文件..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "Docker Compose配置文件未找到: $DOCKER_COMPOSE_FILE"
        echo "請確保您在正確的目錄中運行此腳本"
        exit 1
    fi
    
    if [ ! -f "nginx/simple.conf" ]; then
        error "Nginx配置文件未找到: nginx/simple.conf"
        exit 1
    fi
    
    success "配置文件檢查完成"
}

# 詢問用戶配置
ask_user_configuration() {
    echo ""
    info "配置系統參數..."
    
    # 詢問是否修改MySQL密碼
    echo -n "是否修改預設MySQL密碼？(建議修改) [y/N]: "
    read -r change_mysql_password
    
    if [[ $change_mysql_password =~ ^[Yy]$ ]]; then
        echo -n "請輸入新的MySQL密碼: "
        read -s new_mysql_password
        echo
        echo -n "請再次確認密碼: "
        read -s confirm_mysql_password
        echo
        
        if [ "$new_mysql_password" != "$confirm_mysql_password" ]; then
            error "密碼確認不匹配"
            exit 1
        fi
        
        if [ ${#new_mysql_password} -lt 8 ]; then
            error "密碼長度至少8位"
            exit 1
        fi
        
        MYSQL_PASSWORD="$new_mysql_password"
        CHANGE_MYSQL_PASSWORD=true
    else
        MYSQL_PASSWORD="$DEFAULT_MYSQL_PASSWORD"
        CHANGE_MYSQL_PASSWORD=false
        warning "使用預設MySQL密碼，生產環境建議稍後修改"
    fi
    
    # 詢問是否修改管理員密碼
    echo -n "是否修改預設管理員密碼？(建議修改) [y/N]: "
    read -r change_admin_password
    
    if [[ $change_admin_password =~ ^[Yy]$ ]]; then
        echo -n "請輸入新的管理員密碼: "
        read -s new_admin_password
        echo
        echo -n "請再次確認密碼: "
        read -s confirm_admin_password
        echo
        
        if [ "$new_admin_password" != "$confirm_admin_password" ]; then
            error "密碼確認不匹配"
            exit 1
        fi
        
        ADMIN_PASSWORD="$new_admin_password"
    else
        warning "使用預設管理員密碼，請稍後修改"
    fi
    
    echo ""
    success "配置收集完成"
}

# 更新Docker Compose配置
update_docker_compose_config() {
    if [ "$CHANGE_MYSQL_PASSWORD" = true ]; then
        info "更新Docker Compose配置..."
        
        # 創建備份
        cp "$DOCKER_COMPOSE_FILE" "${DOCKER_COMPOSE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        
        # 更新MySQL密碼
        sed -i.tmp "s/MYSQL_PASSWORD: [^[:space:]]*/MYSQL_PASSWORD: $MYSQL_PASSWORD/g" "$DOCKER_COMPOSE_FILE"
        rm "${DOCKER_COMPOSE_FILE}.tmp" 2>/dev/null || true
        
        success "Docker Compose配置已更新"
    fi
}

# 更新Django設置
update_django_config() {
    if [ "$CHANGE_MYSQL_PASSWORD" = true ]; then
        info "更新Django設置..."
        
        local settings_file="../backend/pcms_staff/settings.py"
        
        if [ -f "$settings_file" ]; then
            # 創建備份
            cp "$settings_file" "${settings_file}.backup.$(date +%Y%m%d_%H%M%S)"
            
            # 更新密碼
            sed -i.tmp "s/'PASSWORD': '[^']*'/'PASSWORD': '$MYSQL_PASSWORD'/g" "$settings_file"
            rm "${settings_file}.tmp" 2>/dev/null || true
            
            success "Django設置已更新"
        else
            warning "Django設置文件未找到，稍後手動更新"
        fi
    fi
}

# 啟動服務
start_services() {
    info "啟動系統服務..."
    
    # 停止可能存在的舊容器
    docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
    
    # 拉取最新鏡像
    info "拉取Docker鏡像..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    # 構建並啟動服務
    info "構建並啟動服務..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "服務啟動完成"
}

# 等待服務就緒
wait_for_services() {
    info "等待服務就緒..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        # 檢查MySQL
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -ppcms_root_2025 -e "SELECT 1;" &>/dev/null; then
            success "MySQL服務就緒"
            break
        fi
        
        echo "⏳ 等待MySQL服務... ($attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "MySQL服務啟動超時"
        return 1
    fi
    
    # 等待後端服務
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py check --database default &>/dev/null; then
            success "後端服務就緒"
            break
        fi
        
        echo "⏳ 等待後端服務... ($attempt/$max_attempts)"
        sleep 3
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "後端服務啟動超時"
        return 1
    fi
}

# 初始化數據庫
initialize_database() {
    info "初始化數據庫..."
    
    # 執行數據庫遷移
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py migrate
    
    success "數據庫初始化完成"
}

# 設置管理員用戶和Token
setup_admin() {
    info "設置管理員用戶..."
    
    # 調用Token設置腳本
    if [ -f "scripts/setup_admin_token.sh" ]; then
        ./scripts/setup_admin_token.sh -u "$ADMIN_USERNAME" -p "$ADMIN_PASSWORD"
    else
        # 手動設置（如果腳本不存在）
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py shell <<EOF
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user, created = User.objects.get_or_create(
    username='$ADMIN_USERNAME',
    defaults={
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'email': 'admin@puichingcoloane.edu.mo'
    }
)

user.set_password('$ADMIN_PASSWORD')
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

Token.objects.filter(user=user).delete()
token = Token.objects.create(user=user)

print(f"管理員設置完成 - Token: {token.key}")
EOF
    fi
    
    success "管理員設置完成"
}

# 驗證部署
verify_deployment() {
    info "驗證系統部署..."
    
    # 檢查前端
    local frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null || echo "000")
    if [ "$frontend_status" = "200" ]; then
        success "前端服務正常"
    else
        warning "前端服務檢查失敗 (狀態碼: $frontend_status)"
    fi
    
    # 檢查後端
    local backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/ 2>/dev/null || echo "000")
    if [ "$backend_status" = "200" ] || [ "$backend_status" = "302" ]; then
        success "後端服務正常"
    else
        warning "後端服務檢查失敗 (狀態碼: $backend_status)"
    fi
    
    # 檢查數據庫
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u pcms_admin -p"$MYSQL_PASSWORD" pcms_staff_db -e "SHOW TABLES;" &>/dev/null; then
        success "數據庫連接正常"
    else
        warning "數據庫連接檢查失敗"
    fi
}

# 顯示部署結果
show_deployment_summary() {
    echo ""
    echo "========================================="
    echo "          部署完成！"
    echo "========================================="
    echo ""
    success "系統已成功部署並初始化"
    echo ""
    echo "📋 系統資訊:"
    echo "   🌐 前端地址: http://localhost:3000/"
    echo "   🛠️  管理後台: http://localhost:8000/admin/"
    echo "   📊 API文檔: http://localhost:8000/api/"
    echo ""
    echo "🔑 登錄資訊:"
    echo "   👤 管理員用戶名: $ADMIN_USERNAME"
    echo "   🔐 管理員密碼: $ADMIN_PASSWORD"
    echo ""
    echo "🗄️ 數據庫資訊:"
    echo "   📍 MySQL主機: localhost:3307"
    echo "   🎯 數據庫名: pcms_staff_db"
    echo "   👤 用戶名: pcms_admin"
    echo "   🔐 密碼: $MYSQL_PASSWORD"
    echo ""
    warning "安全提醒:"
    echo "   🔒 請立即修改所有預設密碼"
    echo "   🛡️  配置防火牆限制數據庫訪問"
    echo "   📜 定期備份數據"
    echo ""
    echo "🔧 管理工具:"
    echo "   📝 修改MySQL密碼: ./scripts/manage_mysql.sh change-main-password <新密碼>"
    echo "   🔑 重新生成Token: ./scripts/setup_admin_token.sh"
    echo "   🔍 健康檢查: ./scripts/health_check.sh"
    echo ""
    echo "========================================="
}

# 主函數
main() {
    echo "開始新伺服器部署初始化..."
    echo ""
    
    # 執行部署步驟
    check_prerequisites
    check_configuration
    ask_user_configuration
    update_docker_compose_config
    update_django_config
    start_services
    wait_for_services
    initialize_database
    setup_admin
    verify_deployment
    show_deployment_summary
    
    success "部署初始化完成！"
    echo ""
    info "請使用上述資訊登錄系統並開始使用"
}

# 當腳本被直接執行時運行main函數
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi