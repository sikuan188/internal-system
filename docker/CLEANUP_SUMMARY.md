# PCMS Docker 配置清理完成

## 清理总结

### ✅ 已删除的文件：
- `pcms_staff_db_volume_holder` 服务（SQLite 相关）
- `docker-compose-simple.yml` 
- `docker-compose.prod.yml`
- 冗余的 nginx 配置文件 (4个 → 2个)
- 冗余的 SSL 脚本 (4个 → 1个统一脚本)

### 📁 当前核心文件结构：
```
docker/
├── docker-compose.yml          # 主配置文件（支持 MySQL + 环境变量控制）
├── docker-compose.windows.yml  # Windows 兼容版本（建议保留）
├── docker-compose-https.yml    # HTTPS 配置（可选保留）
├── nginx/
│   ├── unified.conf            # 统一配置（支持 HTTP/HTTPS 切换）
│   ├── security.conf           # 安全配置
│   ├── default.conf            # 基础配置（备用）
│   └── default-https.conf      # HTTPS 配置（备用）
├── ssl/
│   ├── manage-ssl.sh           # 统一 SSL 管理脚本 🆕
│   └── scripts/                # Windows PowerShell 脚本
└── scripts/
    └── init_production_admin.sh # 生产环境管理员初始化 🆕
```

## 🚀 使用方法

### 1. 开发环境启动
```bash
docker-compose up --build
```

### 2. 生产环境启动（HTTPS）
```bash
# 生成 SSL 证书
./ssl/manage-ssl.sh generate --type self-signed --domain your-domain.com

# 启动服务
SSL_ENABLED=true DOMAIN_NAME=your-domain.com docker-compose up -d --build
```

### 3. 生产环境管理员初始化
```bash
# 启动后执行一次
docker-compose exec backend bash /app/scripts/init_production_admin.sh
```

### 4. SSL 证书管理
```bash
# 查看帮助
./ssl/manage-ssl.sh --help

# 生成自签名证书
./ssl/manage-ssl.sh generate --type self-signed

# 安装 Let's Encrypt 证书
./ssl/manage-ssl.sh generate --type letsencrypt --domain yourdomain.com --email admin@yourdomain.com

# 检查证书状态
./ssl/manage-ssl.sh status
```

## 🌍 跨平台兼容性

### macOS / Linux
使用主配置文件：
```bash
docker-compose -f docker-compose.yml up
```

### Windows
使用 Windows 优化版本：
```bash
docker-compose -f docker-compose.windows.yml up
```

## 环境变量控制

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SSL_ENABLED` | `false` | 启用 HTTPS |
| `DEV_MODE` | `true` | 开发模式（禁用缓存） |
| `DOMAIN_NAME` | `localhost` | 域名设置 |

## 注意事项

1. **数据库**：现在使用 MySQL，SQLite 相关配置已清理
2. **证书**：统一脚本支持自签名和 Let's Encrypt
3. **Windows 兼容**：保留了 Windows 专用配置和 PowerShell 脚本
4. **生产部署**：使用 `init_production_admin.sh` 替代 `init_users` 服务