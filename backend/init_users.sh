#!/bin/bash
# PCMS Staff Management System - User Initialization Script
# 培正中學員工管理系統 - 用戶初始化腳本
#
# 此腳本用於在Docker容器中創建初始用戶和測試數據
# This script creates initial users and test data in Docker containers

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏫 培正中學員工管理系統 - 用戶初始化${NC}"
echo -e "${BLUE}PCMS Staff Management System - User Initialization${NC}"
echo "================================================================="

# 檢查Django是否可用
echo -e "${CYAN}🔍 檢查Django環境...${NC}"
python manage.py check --deploy > /dev/null 2>&1 || {
    echo -e "${RED}❌ Django環境檢查失敗${NC}"
    exit 1
}
echo -e "${GREEN}✅ Django環境正常${NC}"

# 創建用戶函數
create_user() {
    local username=$1
    local email=$2  
    local password=$3
    local is_superuser=${4:-false}
    local is_staff=${5:-false}
    
    echo -e "${CYAN}👤 創建用戶: $username${NC}"
    
    python manage.py shell << EOF
import os
from django.contrib.auth.models import User
from staff_management.models import UserRole

# 檢查用戶是否已存在
if User.objects.filter(username='$username').exists():
    print('   ℹ️  用戶 $username 已存在，跳過創建')
else:
    # 創建用戶
    user = User.objects.create_user(
        username='$username',
        email='$email',
        password='$password'
    )
    
    user.is_superuser = '$is_superuser' == 'true'
    user.is_staff = '$is_staff' == 'true'
    user.save()
    
    print('   ✅ 用戶 $username 創建成功')
    
    # 為非超級用戶創建角色
    if not ('$is_superuser' == 'true'):
        # 根據用戶名確定角色
        if '$username' == 'hr_manager':
            role_type = 'hr'
            department = '人事部'
        elif '$username' == 'supervisor':
            role_type = 'supervisor'  
            department = '教務部'
        elif '$username' == 'staff_user':
            role_type = 'staff'
            department = '一般員工'
        else:
            role_type = 'readonly'
            department = '訪客'
        
        # 創建用戶角色
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={
                'role': role_type,
                'department': department,
                'is_active': True,
                'can_view_all_staff': role_type in ['hr', 'supervisor'],
                'can_edit_staff_data': role_type in ['hr'],
                'can_export_data': role_type in ['hr', 'supervisor'],
                'can_import_data': role_type in ['hr'],
                'can_manage_users': False,
                'can_view_statistics': True
            }
        )
        
        if created:
            print(f'   ✅ 用戶角色創建成功: {role_type} - {department}')
        else:
            print(f'   ℹ️  用戶角色已存在: {role_type} - {department}')
EOF
}

# 創建測試用戶
echo -e "${YELLOW}📝 創建系統用戶...${NC}"

# 1. 超級管理員 (如果不存在)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    create_user "$DJANGO_SUPERUSER_USERNAME" "$DJANGO_SUPERUSER_EMAIL" "$DJANGO_SUPERUSER_PASSWORD" "true" "true"
else
    create_user "adminkuan" "sikuan@puichingcoloane.edu.mo" "admin-Kuan" "true" "true"
fi

# 2. HR 管理員
create_user "hr_manager" "hr@puichingcoloane.edu.mo" "hrmanager123" "false" "true"

# 3. 主管用戶
create_user "supervisor" "supervisor@puichingcoloane.edu.mo" "supervisor123" "false" "true"

# 4. 一般員工用戶
create_user "staff_user" "staff@puichingcoloane.edu.mo" "staff123" "false" "false"

# 5. 唯讀用戶
create_user "readonly_user" "readonly@puichingcoloane.edu.mo" "readonly123" "false" "false"

echo ""
echo -e "${GREEN}🎉 用戶創建完成！${NC}"
echo "================================================================="
echo -e "${CYAN}📊 用戶列表摘要：${NC}"

# 顯示用戶摘要
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from staff_management.models import UserRole

print("用戶名 | 郵箱 | 管理員 | 員工 | 角色")
print("-" * 60)

for user in User.objects.all().order_by('username'):
    try:
        user_role = UserRole.objects.get(user=user)
        role_info = f"{user_role.get_role_display()} ({user_role.department})"
    except UserRole.DoesNotExist:
        role_info = "超級管理員" if user.is_superuser else "無角色"
    
    admin_status = "是" if user.is_superuser else "否"
    staff_status = "是" if user.is_staff else "否"
    
    print(f"{user.username:<12} | {user.email:<25} | {admin_status:<4} | {staff_status:<4} | {role_info}")
EOF

echo ""
echo -e "${YELLOW}⚠️  重要提醒：${NC}"
echo "   • 這些是測試用戶，生產環境請更改密碼"
echo "   • 超級管理員可以通過 /admin 管理所有用戶"
echo "   • HR管理員可以管理員工數據"
echo "   • 根據需要調整用戶權限"

echo ""
echo -e "${BLUE}🔐 登錄信息：${NC}"
echo "   管理界面: http://your-domain/admin"
echo "   前端界面: http://your-domain"
echo ""
echo -e "${GREEN}✅ 用戶初始化完成${NC}"

# 創建一些測試數據（可選）
if [ "$CREATE_TEST_DATA" = "true" ]; then
    echo -e "${CYAN}🗄️ 創建測試數據...${NC}"
    
    python manage.py shell << 'EOF'
from staff_management.models import StaffProfile
import random
from datetime import date, timedelta

if not StaffProfile.objects.exists():
    # 創建測試員工數據
    test_staff = [
        {
            'staff_id': 'TEST001',
            'staff_name': '張三',
            'name_chinese': '張三',
            'gender': '男',
            'employment_type': '全職',
            'is_active': True,
            'entry_date': date.today() - timedelta(days=365),
            'email': 'zhangsan@example.com'
        },
        {
            'staff_id': 'TEST002', 
            'staff_name': '李四',
            'name_chinese': '李四',
            'gender': '女',
            'employment_type': '兼職',
            'is_active': True,
            'entry_date': date.today() - timedelta(days=730),
            'email': 'lisi@example.com'
        }
    ]
    
    for data in test_staff:
        StaffProfile.objects.create(**data)
    
    print(f"✅ 創建了 {len(test_staff)} 個測試員工記錄")
else:
    print("ℹ️  測試員工數據已存在，跳過創建")
EOF
    
    echo -e "${GREEN}✅ 測試數據創建完成${NC}"
fi

echo "================================================================="
echo -e "${GREEN}🎯 初始化完成！系統已準備就緒。${NC}"