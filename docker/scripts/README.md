# 培正中學員工管理系統 - 管理腳本
## PCMS Staff Management System - Management Scripts

本目錄包含系統管理和部署的自動化腳本。

## 📋 腳本清單

### 🚀 `deploy_new_server.sh` - 新伺服器一鍵部署
**功能：** 完整的新伺服器部署初始化
**使用場景：** 在全新伺服器上首次部署系統

```bash
# 基本使用
./deploy_new_server.sh

# 功能包括：
# - 檢查Docker環境
# - 互動式配置密碼
# - 自動更新配置文件
# - 啟動所有服務
# - 初始化數據庫
# - 創建管理員和Token
# - 驗證部署
```

### 🔑 `setup_admin_token.sh` - 管理員Token管理
**功能：** 設置或重新生成管理員用戶和Token
**使用場景：** Token重置、忘記密碼、安全維護

```bash
# 使用預設設置
./setup_admin_token.sh

# 自定義用戶名和密碼
./setup_admin_token.sh -u newadmin -p NewPassword123

# 查看幫助
./setup_admin_token.sh --help
```

### 🗄️ `manage_mysql.sh` - MySQL管理
**功能：** MySQL用戶和密碼管理
**使用場景：** 修改密碼、創建用戶、權限管理

```bash
# 修改主用戶密碼（推薦）
./manage_mysql.sh change-main-password "NewSecurePassword"

# 創建新用戶
./manage_mysql.sh create-user backup_user BackupPass123 readonly

# 列出所有用戶
./manage_mysql.sh list-users

# 測試連接
./manage_mysql.sh test-connection

# 查看幫助
./manage_mysql.sh help
```

## 🔧 使用前準備

### 1. 設置執行權限
```bash
chmod +x *.sh
```

### 2. 確認Docker環境
```bash
# 檢查Docker
docker --version

# 檢查Docker Compose
docker-compose --version

# 確保在docker目錄中執行腳本
pwd  # 應該顯示 .../pcms-staff/docker
```

## 📖 詳細使用指南

### 新伺服器部署流程

1. **克隆代碼**
   ```bash
   git clone https://github.com/your-org/pcms-staff.git
   cd pcms-staff/docker
   ```

2. **執行一鍵部署**
   ```bash
   ./scripts/deploy_new_server.sh
   ```

3. **跟隨提示操作**
   - 選擇是否修改MySQL密碼
   - 選擇是否修改管理員密碼
   - 等待自動部署完成

4. **驗證部署**
   - 前端：http://localhost:3000/
   - 後端：http://localhost:8000/admin/

### Token管理場景

**場景1：忘記管理員密碼**
```bash
./scripts/setup_admin_token.sh -u adminkuan -p "NewPassword123"
```

**場景2：安全重置Token**
```bash
./scripts/setup_admin_token.sh
```

**場景3：創建新管理員**
```bash
./scripts/setup_admin_token.sh -u newadmin -p "AdminPass456"
```

### MySQL管理場景

**場景1：部署後立即修改預設密碼**
```bash
./scripts/manage_mysql.sh change-main-password "ProductionPassword123"
```

**場景2：創建備份用戶**
```bash
./scripts/manage_mysql.sh create-user backup_service BackupPass123 readonly
```

**場景3：創建應用程序用戶**
```bash
./scripts/manage_mysql.sh create-user app_service AppPass123 readwrite
```

## ⚠️ 安全最佳實踐

### 1. 密碼策略
- **長度：** 至少12位字符
- **複雜度：** 包含大小寫字母、數字、特殊符號
- **唯一性：** 每個環境使用不同密碼
- **定期更新：** 建議每3-6個月更新一次

### 2. Token管理
- **定期重置：** 定期重新生成Token
- **環境隔離：** 不同環境使用不同Token
- **記錄備份：** 安全地記錄新Token

### 3. 腳本安全
- **權限控制：** 僅授權用戶可執行腳本
- **日誌審計：** 記錄腳本執行日誌
- **備份驗證：** 執行前確保有數據備份

## 🚨 故障排除

### 常見問題

**問題1：腳本無法執行**
```bash
# 解決方案：設置執行權限
chmod +x scripts/*.sh
```

**問題2：Docker連接失敗**
```bash
# 檢查Docker服務
sudo systemctl status docker
sudo systemctl start docker
```

**問題3：MySQL連接超時**
```bash
# 檢查MySQL容器狀態
docker-compose -f docker-compose-simple.yml ps
docker-compose -f docker-compose-simple.yml logs mysql
```

**問題4：配置文件更新失敗**
```bash
# 檢查文件權限
ls -la ../backend/pcms_staff/settings.py
chmod 664 ../backend/pcms_staff/settings.py
```

### 緊急恢復

**如果部署失敗：**
```bash
# 停止所有服務
docker-compose -f docker-compose-simple.yml down

# 清理容器
docker system prune -f

# 重新部署
./scripts/deploy_new_server.sh
```

**如果配置文件損壞：**
```bash
# 恢復備份文件
ls -la *.backup.*  # 查看備份文件
cp settings.py.backup.20250826_143022 ../backend/pcms_staff/settings.py
```

## 📞 技術支援

如遇問題，請聯繫：
- **系統管理員：** C.K.
- **郵件：** sikuan@puiching.edu.mo
- **文檔：** 參考 ADMIN_TECHNICAL_GUIDE.md

## 📝 更新日誌

- **v1.0.0** (2025-08-26): 初始版本，包含所有基本管理腳本
- 新增一鍵部署腳本
- 新增Token自動管理
- 新增MySQL用戶管理
- 新增配置自動更新