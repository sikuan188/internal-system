# Windows SSL 部署指南
# PCMS Staff Management System

## 🎯 概述

本指南專門為培正中學員工管理系統在 Windows 環境下的 SSL 證書部署而設計，解決了原有證書配置中缺少服務器 IP `172.188.188.225` 的問題。

## 🚀 快速部署

### 方法一：PowerShell 自動部署（推薦）

1. **以管理員身份打開 PowerShell**
2. **執行部署腳本**：
   ```powershell
   cd docker\ssl\scripts
   .\deploy-windows-ssl.ps1 -AutoInstall
   ```

### 方法二：僅生成證書（無需管理員權限）

```powershell
cd docker\ssl\scripts
.\deploy-windows-ssl.ps1
```

然後手動安裝生成的證書文件。

## 📋 部署選項

### 基本選項

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-ServerIP` | 服務器IP地址 | `172.188.188.225` |
| `-DomainName` | 域名 | `pcms-staff.local` |
| `-Days` | 證書有效期（天） | `1825`（5年） |
| `-AutoInstall` | 自動安裝證書 | `false` |

### 範例用法

```powershell
# 生成5年有效期證書並自動安裝
.\deploy-windows-ssl.ps1 -ServerIP "172.188.188.225" -Days 1825 -AutoInstall

# 僅生成證書，自定義域名
.\deploy-windows-ssl.ps1 -DomainName "pcms.company.com" -Days 365

# 詳細輸出模式
.\deploy-windows-ssl.ps1 -Verbose
```

## 📁 生成的文件

部署完成後，將在 `docker/ssl/windows-deployment/` 目錄下生成：

```
windows-deployment/
├── server.crt              # SSL 證書
├── server.key              # 私鑰
├── server.csr              # 證書簽名請求
├── server-config.conf      # OpenSSL 配置
└── ../windows-deployment.env  # Docker 環境變量
```

## 🔧 手動安裝證書

如果未使用 `-AutoInstall` 參數，請按以下步驟手動安裝：

### 圖形界面安裝

1. 找到生成的 `server.crt` 文件
2. 雙擊打開證書
3. 點擊「安裝證書」
4. 選擇「本地計算機」
5. 選擇「將所有證書放入下列存放區」
6. 瀏覽並選擇「受信任的根憑證授權單位」
7. 完成安裝

### PowerShell 命令安裝

```powershell
# 需要管理員權限
Import-Certificate -FilePath "docker\ssl\windows-deployment\server.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

### 驗證安裝

```powershell
# 檢查證書是否已安裝
Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*172.188.188.225*"}
```

## 🐳 Docker Compose 配置

### 更新環境變量

將生成的 `windows-deployment.env` 內容添加到您的 `.env` 文件中：

```env
# SSL Configuration
SSL_CERT_PATH=./ssl/windows-deployment/server.crt
SSL_KEY_PATH=./ssl/windows-deployment/server.key
SSL_ENABLED=true
FORCE_HTTPS=true
SERVER_IP=172.188.188.225
DOMAIN_NAME=pcms-staff.local
```

### 啟動 HTTPS 服務

```bash
# 使用 HTTPS 配置啟動
docker-compose -f docker-compose-https.yml --env-file windows-deployment.env up -d --build
```

## 🌐 訪問服務

部署完成後，可通過以下地址訪問：

- **HTTPS**: `https://172.188.188.225`
- **域名訪問**: `https://pcms-staff.local`（需配置 hosts）

### 配置 hosts 文件（可選）

編輯 `C:\Windows\System32\drivers\etc\hosts`，添加：

```
172.188.188.225    pcms-staff.local
172.188.188.225    pcms.puichingcoloane.edu.mo
```

## 🔍 故障排除

### 常見問題

#### 1. "無法確認此憑證的發行者信任鏈"

**解決方案**：
- 確保證書已安裝到「受信任的根憑證授權單位」
- 不是「個人」或「其他人」證書存儲

#### 2. PowerShell 執行策略限制

**解決方案**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. OpenSSL 不可用

**解決方案**：
- 下載並安裝 OpenSSL for Windows
- 或下載便攜版本到腳本目錄

#### 4. 瀏覽器仍顯示不安全

**檢查項目**：
- 證書是否包含正確的 IP/域名
- 證書是否已過期
- 是否使用了正確的協議（HTTPS）

### 日誌檢查

查看 Docker 服務日誌：

```bash
# 檢查 Nginx 日誌
docker-compose logs nginx

# 檢查後端服務日誌
docker-compose logs backend
```

## 📞 技術支援

如遇到問題，請聯絡：

- **IT 部門**: sikuan@puichingcoloane.edu.mo
- **校內分機**: 170

## ⚠️ 安全提醒

1. **私鑰保護**: `server.key` 文件包含私鑰，請妥善保管
2. **證書有效期**: 預設5年有效期，請注意到期時間
3. **僅限內網**: 此為自簽證書，僅適用於內網環境
4. **生產環境**: 建議使用正式 CA 頒發的證書

## 📅 維護計劃

- **證書更新**: 建議每年檢查證書有效期
- **安全審計**: 定期檢查證書使用情況
- **備份**: 定期備份證書和私鑰文件