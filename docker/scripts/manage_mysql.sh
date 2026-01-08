#!/bin/bash

# ========================================
# 培正中學員工管理系統 - MySQL管理腳本
# PCMS Staff Management System - MySQL Management Script
# ========================================

set -e  # 遇到錯誤立即停止

echo "========================================="
echo "    培正中學員工管理系統"
echo "    MySQL密碼和用戶管理腳本"
echo "========================================="

# 配置變量
DOCKER_COMPOSE_FILE="docker-compose-simple.yml"
MYSQL_CONTAINER="pcms_staff_mysql"
BACKEND_CONTAINER="pcms_staff_backend"
DATABASE_NAME="pcms_staff_db"

# 當前配置
CURRENT_MYSQL_USER="pcms_admin"
CURRENT_MYSQL_PASSWORD="pcms_admin"
CURRENT_ROOT_PASSWORD="pcms_root_2025"

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
    
    # 檢查MySQL容器是否運行
    if ! docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "$MYSQL_CONTAINER.*running"; then
        echo "❌ 錯誤: MySQL容器未運行"
        echo "請先啟動系統: docker-compose -f $DOCKER_COMPOSE_FILE up -d"
        exit 1
    fi
    
    echo "✅ Docker環境檢查通過"
}

# 等待MySQL就緒
wait_for_mysql() {
    echo "等待MySQL服務就緒..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" -e "SELECT 1;" &>/dev/null; then
            echo "✅ MySQL連接成功"
            return 0
        fi
        
        echo "⏳ 等待MySQL... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "❌ 錯誤: MySQL連接失敗"
    exit 1
}

# 修改MySQL用戶密碼
change_mysql_user_password() {
    local username="$1"
    local old_password="$2"
    local new_password="$3"
    
    echo "修改MySQL用戶 '$username' 的密碼..."
    
    # 驗證舊密碼
    if ! docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u "$username" -p"$old_password" -e "SELECT 1;" &>/dev/null; then
        echo "❌ 錯誤: 舊密碼驗證失敗"
        return 1
    fi
    
    # 修改密碼
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" <<EOF
ALTER USER '$username'@'%' IDENTIFIED BY '$new_password';
FLUSH PRIVILEGES;
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ 用戶 '$username' 密碼修改成功"
        
        # 測試新密碼
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u "$username" -p"$new_password" -e "SELECT 1;" &>/dev/null; then
            echo "✅ 新密碼驗證成功"
            return 0
        else
            echo "❌ 錯誤: 新密碼驗證失敗"
            return 1
        fi
    else
        echo "❌ 錯誤: 密碼修改失敗"
        return 1
    fi
}

# 創建新的MySQL用戶
create_mysql_user() {
    local username="$1"
    local password="$2"
    local privileges="$3"
    
    echo "創建MySQL用戶 '$username'..."
    
    # 檢查用戶是否已存在
    local user_exists=$(docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" -e "SELECT COUNT(*) FROM mysql.user WHERE user='$username';" 2>/dev/null | tail -n 1)
    
    if [ "$user_exists" -gt 0 ]; then
        echo "⚠️  用戶 '$username' 已存在，將重置密碼"
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" <<EOF
ALTER USER '$username'@'%' IDENTIFIED BY '$password';
EOF
    else
        echo "創建新用戶..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" <<EOF
CREATE USER '$username'@'%' IDENTIFIED BY '$password';
EOF
    fi
    
    # 設置權限
    case "$privileges" in
        "admin"|"full")
            echo "設置管理員權限..."
            docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" <<EOF
GRANT ALL PRIVILEGES ON $DATABASE_NAME.* TO '$username'@'%';
FLUSH PRIVILEGES;
EOF
            ;;
        "readwrite")
            echo "設置讀寫權限..."
            docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" <<EOF
GRANT SELECT, INSERT, UPDATE, DELETE ON $DATABASE_NAME.* TO '$username'@'%';
FLUSH PRIVILEGES;
EOF
            ;;
        "readonly")
            echo "設置只讀權限..."
            docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" <<EOF
GRANT SELECT ON $DATABASE_NAME.* TO '$username'@'%';
FLUSH PRIVILEGES;
EOF
            ;;
        *)
            echo "❌ 錯誤: 未知權限類型 '$privileges'"
            echo "支持的權限: admin, readwrite, readonly"
            return 1
            ;;
    esac
    
    # 驗證用戶創建
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u "$username" -p"$password" -e "SELECT 1;" &>/dev/null; then
        echo "✅ 用戶 '$username' 創建/更新成功"
        return 0
    else
        echo "❌ 錯誤: 用戶創建/更新失敗"
        return 1
    fi
}

# 更新Django配置文件
update_django_settings() {
    local new_password="$1"
    local settings_file="../backend/pcms_staff/settings.py"
    
    echo "更新Django設置文件..."
    
    if [ ! -f "$settings_file" ]; then
        echo "❌ 錯誤: Django設置文件未找到: $settings_file"
        return 1
    fi
    
    # 創建備份
    cp "$settings_file" "${settings_file}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已創建設置文件備份"
    
    # 更新密碼
    sed -i.tmp "s/'PASSWORD': '[^']*'/'PASSWORD': '$new_password'/g" "$settings_file"
    rm "${settings_file}.tmp" 2>/dev/null || true
    
    echo "✅ Django設置文件已更新"
    echo "⚠️  請重啟後端容器以應用新配置："
    echo "   docker-compose -f $DOCKER_COMPOSE_FILE restart backend"
}

# 更新Docker Compose配置
update_docker_compose() {
    local new_password="$1"
    
    echo "更新Docker Compose配置..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "❌ 錯誤: Docker Compose文件未找到: $DOCKER_COMPOSE_FILE"
        return 1
    fi
    
    # 創建備份
    cp "$DOCKER_COMPOSE_FILE" "${DOCKER_COMPOSE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已創建Docker Compose備份"
    
    # 更新密碼（使用sed處理YAML）
    sed -i.tmp "s/MYSQL_PASSWORD: [^[:space:]]*/MYSQL_PASSWORD: $new_password/g" "$DOCKER_COMPOSE_FILE"
    rm "${DOCKER_COMPOSE_FILE}.tmp" 2>/dev/null || true
    
    echo "✅ Docker Compose配置已更新"
    echo "⚠️  下次重新部署時將使用新密碼"
}

# 測試數據庫連接
test_database_connection() {
    local username="$1"
    local password="$2"
    
    echo "測試數據庫連接..."
    
    # 測試MySQL連接
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u "$username" -p"$password" "$DATABASE_NAME" -e "SHOW TABLES;" &>/dev/null; then
        echo "✅ MySQL連接測試成功"
    else
        echo "❌ MySQL連接測試失敗"
        return 1
    fi
    
    # 測試Django連接
    echo "測試Django數據庫連接..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python manage.py check --database default &>/dev/null; then
        echo "✅ Django數據庫連接測試成功"
    else
        echo "❌ Django數據庫連接測試失敗"
        echo "請檢查Django設置並重啟後端容器"
        return 1
    fi
}

# 顯示幫助信息
show_help() {
    echo "用法: $0 <命令> [選項]"
    echo ""
    echo "命令:"
    echo "  change-password <username> <old_password> <new_password>"
    echo "                   修改指定用戶的密碼"
    echo ""
    echo "  change-main-password <new_password>"
    echo "                   修改主用戶(pcms_admin)密碼並更新配置"
    echo ""
    echo "  create-user <username> <password> <privileges>"
    echo "                   創建新用戶，權限: admin|readwrite|readonly"
    echo ""
    echo "  test-connection [username] [password]"
    echo "                   測試數據庫連接 (預設使用主用戶)"
    echo ""
    echo "  list-users       列出所有MySQL用戶"
    echo ""
    echo "範例:"
    echo "  $0 change-main-password MyNewSecurePassword123"
    echo "  $0 create-user backup_user backup123 readonly"
    echo "  $0 change-password pcms_admin pcms_admin NewPassword123"
    echo "  $0 test-connection"
}

# 列出MySQL用戶
list_mysql_users() {
    echo "MySQL用戶列表:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec mysql mysql -u root -p"$CURRENT_ROOT_PASSWORD" -e "
SELECT 
    User as '用戶名',
    Host as '主機'
FROM mysql.user 
WHERE User NOT IN ('mysql.sys', 'mysql.session', 'mysql.infoschema', 'root')
ORDER BY User;
"
}

# 主函數
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    local command="$1"
    shift
    
    # 檢查環境（對於所有命令除了help）
    if [ "$command" != "help" ] && [ "$command" != "-h" ] && [ "$command" != "--help" ]; then
        check_docker_environment
        wait_for_mysql
    fi
    
    case "$command" in
        "change-password")
            if [ $# -ne 3 ]; then
                echo "❌ 錯誤: 需要3個參數 - 用戶名、舊密碼、新密碼"
                echo "用法: $0 change-password <username> <old_password> <new_password>"
                exit 1
            fi
            change_mysql_user_password "$1" "$2" "$3"
            ;;
        
        "change-main-password")
            if [ $# -ne 1 ]; then
                echo "❌ 錯誤: 需要1個參數 - 新密碼"
                echo "用法: $0 change-main-password <new_password>"
                exit 1
            fi
            
            local new_password="$1"
            echo "修改主用戶密碼並更新所有配置..."
            
            if change_mysql_user_password "$CURRENT_MYSQL_USER" "$CURRENT_MYSQL_PASSWORD" "$new_password"; then
                update_django_settings "$new_password"
                update_docker_compose "$new_password"
                echo ""
                echo "✅ 主用戶密碼修改完成！"
                echo "📝 更新記錄:"
                echo "   - MySQL用戶密碼已更新"
                echo "   - Django設置已更新"
                echo "   - Docker Compose配置已更新"
                echo ""
                echo "⚠️  請執行以下命令重啟服務："
                echo "   docker-compose -f $DOCKER_COMPOSE_FILE restart backend"
                echo ""
                echo "🔑 新的連接信息:"
                echo "   用戶名: $CURRENT_MYSQL_USER"
                echo "   新密碼: $new_password"
            fi
            ;;
        
        "create-user")
            if [ $# -ne 3 ]; then
                echo "❌ 錯誤: 需要3個參數 - 用戶名、密碼、權限"
                echo "用法: $0 create-user <username> <password> <privileges>"
                echo "權限選項: admin, readwrite, readonly"
                exit 1
            fi
            create_mysql_user "$1" "$2" "$3"
            ;;
        
        "test-connection")
            local test_user="${1:-$CURRENT_MYSQL_USER}"
            local test_pass="${2:-$CURRENT_MYSQL_PASSWORD}"
            test_database_connection "$test_user" "$test_pass"
            ;;
        
        "list-users")
            list_mysql_users
            ;;
        
        "help"|"-h"|"--help")
            show_help
            ;;
        
        *)
            echo "❌ 錯誤: 未知命令 '$command'"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 當腳本被直接執行時運行main函數
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi