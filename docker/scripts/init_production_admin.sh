#!/bin/bash

# 生产环境管理员初始化脚本
# 使用方法：docker-compose exec backend bash /app/scripts/init_production_admin.sh

echo "🚀 PCMS 生产环境管理员初始化"

# 进入应用目录
cd /app

# 运行数据库迁移
echo "📊 执行数据库迁移..."
python manage.py migrate

# 创建超级用户（如果不存在）
echo "👤 创建管理员账户..."
python manage.py shell << EOF
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@pui-ching.edu.hk',
            password='pcms_admin_2025'
        )
        print("✅ 管理员账户创建成功: admin/pcms_admin_2025")
    else:
        print("ℹ️ 管理员账户已存在")
except IntegrityError:
    print("❌ 创建管理员账户失败")
EOF

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

echo "✅ 生产环境初始化完成"
echo "🔗 访问地址: https://your-domain.com/admin/"
echo "👤 管理员: admin / pcms_admin_2025"