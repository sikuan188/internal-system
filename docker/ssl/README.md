# PCMS SSL Certificate Directory
# 培正中學員工管理系統 SSL 證書目錄

This directory contains SSL/TLS certificates for HTTPS configuration.
此目錄包含用於 HTTPS 配置的 SSL/TLS 證書。

## Directory Structure 目錄結構

```
ssl/
├── README.md                 # This file
├── self-signed/             # Self-signed certificates (development)
│   ├── server.crt          # Self-signed certificate
│   ├── server.key          # Private key
│   └── server.csr          # Certificate signing request
├── letsencrypt/             # Let's Encrypt certificates (production)
│   ├── cert.pem            # Let's Encrypt certificate
│   ├── privkey.pem         # Private key
│   ├── chain.pem           # Certificate chain
│   └── fullchain.pem       # Full certificate chain
├── commercial/              # Commercial CA certificates (enterprise)
│   ├── domain.crt          # Commercial certificate
│   ├── domain.key          # Private key
│   └── intermediate.crt    # Intermediate certificate
└── scripts/                 # Certificate management scripts
    ├── generate-self-signed.sh   # Generate self-signed certificates
    ├── generate-ssl-windows.ps1  # Windows SSL certificate generator
    ├── deploy-windows-ssl.ps1    # Windows deployment script (NEW)
    ├── install-letsencrypt.sh    # Install Let's Encrypt certificates
    └── renew-certificates.sh     # Renew certificates
```

## Windows 部署 Windows Deployment

### 🖥️ Windows 專用 SSL 部署

為了解決 Windows 環境下的 SSL 證書安裝問題，我們提供了專用的部署腳本：

```powershell
# 快速部署（自動安裝證書）
cd docker\ssl\scripts
.\deploy-windows-ssl.ps1 -AutoInstall

# 僅生成證書（手動安裝）
.\deploy-windows-ssl.ps1 -ServerIP "172.188.188.225" -Days 1825
```

**特點**：
- ✅ 自動包含服務器 IP: `172.188.188.225`
- ✅ 5年有效期 (1825天)
- ✅ 自動安裝到 Windows 證書存儲
- ✅ 生成 Docker 環境變量配置
- ✅ 完整的故障排除指南

詳細說明請參考: [Windows 部署指南](./WINDOWS_DEPLOYMENT.md)



### 1. Self-Signed Certificates (自簽證書)
- **用途**: 開發和測試環境
- **優點**: 免費，快速生成
- **缺點**: 瀏覽器安全警告，不適合生產環境
- **文件**: `self-signed/server.crt`, `self-signed/server.key`

### 2. Let's Encrypt Certificates (Let's Encrypt 證書)
- **用途**: 生產環境，免費 SSL
- **優點**: 免費，受信任，自動更新
- **缺點**: 需要域名和公網訪問
- **文件**: `letsencrypt/fullchain.pem`, `letsencrypt/privkey.pem`

### 3. Commercial CA Certificates (商業 CA 證書)
- **用途**: 企業生產環境
- **優點**: 最高信任度，Extended Validation 可用
- **缺點**: 需要費用，申請流程較複雜
- **文件**: `commercial/domain.crt`, `commercial/domain.key`

## Important Security Notes 重要安全提醒

⚠️ **Never commit private keys to version control!**
⚠️ **絕不要將私鑰提交到版本控制系統！**

- Add `*.key` and `*.pem` to `.gitignore`
- Store private keys securely
- Use proper file permissions (600 for private keys)
- Regularly rotate certificates
- Monitor certificate expiration dates

## File Permissions 文件權限

```bash
# Set proper permissions for certificates
chmod 644 *.crt *.pem *.cert         # Certificates (read-only)
chmod 600 *.key                      # Private keys (owner read-only)
chmod 755 scripts/*.sh               # Scripts (executable)
```

## Contact 聯絡方式

For SSL certificate issues, contact IT Department:
SSL 證書相關問題，請聯絡 IT 部門：

- Email: sikuan@puichingcoloane.edu.mo
- Phone: 170 (校內分機)