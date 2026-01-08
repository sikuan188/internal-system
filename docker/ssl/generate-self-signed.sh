#!/bin/bash

# PCMS 自簽名SSL憑證生成器 (Bash版本)
# 培正中學員工管理系統 - 跨平台SSL憑證生成
# 支援: macOS, Linux, Docker, Windows (WSL/Git Bash)

set -e

# 腳本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SELF_SIGNED_DIR="$SCRIPT_DIR/self-signed"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# 預設配置
DEFAULT_DOMAIN="pcmshrsystem"
DEFAULT_VALIDITY_DAYS=7300  # 20年
DEFAULT_KEY_SIZE=4096
DEFAULT_COUNTRY="MO"
DEFAULT_STATE="Macau"
DEFAULT_CITY="Macau"
DEFAULT_ORG="Pui Ching Middle School"
DEFAULT_OU="IT Department"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

log_header() {
    echo -e "${CYAN}=================================================================${NC}"
    echo -e "${CYAN}🔐 PCMS 自簽名SSL憑證生成器${NC}"
    echo -e "${CYAN}PCMS Self-Signed SSL Certificate Generator${NC}"
    echo -e "${CYAN}=================================================================${NC}"
}

# 顯示幫助
show_help() {
    log_header
    cat << EOF

用法: $0 [選項]

選項:
  -d, --domain DOMAIN        主域名 (預設: $DEFAULT_DOMAIN)
  -v, --validity DAYS        有效期天數 (預設: $DEFAULT_VALIDITY_DAYS)
  -k, --key-size SIZE        密鑰大小 (預設: $DEFAULT_KEY_SIZE)
  -c, --country CODE         國家代碼 (預設: $DEFAULT_COUNTRY)
  -s, --state STATE          省份/州 (預設: $DEFAULT_STATE)
  -l, --city CITY           城市 (預設: $DEFAULT_CITY)
  -o, --org ORGANIZATION    組織名稱 (預設: $DEFAULT_ORG)
  -u, --ou UNIT            組織單位 (預設: $DEFAULT_OU)
  --backup                  備份現有憑證
  --no-backup              不備份現有憑證
  --force                   強制覆蓋現有憑證
  --detect-ip              自動檢測本機IP並添加到憑證
  -h, --help               顯示此幫助資訊

範例:
  # 使用預設配置生成憑證
  $0
  
  # 指定自訂域名和有效期
  $0 --domain "pcmshrsystem" --validity 3650
  
  # 強制重新生成並備份舊憑證
  $0 --force --backup
  
  # 自動檢測IP並生成憑證
  $0 --detect-ip

注意:
  - 憑證將保存到: $SELF_SIGNED_DIR/
  - 需要安裝 openssl 命令
  - 在Windows上請使用 Git Bash 或 WSL

EOF
}

# 檢查依賴
check_dependencies() {
    log_info "檢查系統依賴..."
    
    # 檢查 openssl
    if ! command -v openssl &> /dev/null; then
        log_error "需要安裝 openssl 命令"
    fi
    
    # 檢查作業系統
    case "$(uname -s)" in
        Linux*)     OS="Linux";;
        Darwin*)    OS="macOS";;
        CYGWIN*|MINGW32*|MSYS*|MINGW*) OS="Windows";;
        *)          OS="Unknown";;
    esac
    
    log_success "檢測到作業系統: $OS"
    log_success "openssl 版本: $(openssl version)"
}

# 獲取本機IP
get_local_ips() {
    local ips=()
    
    if command -v ip &> /dev/null; then
        # Linux
        ips+=($(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' || true))
    elif command -v ifconfig &> /dev/null; then
        # macOS/BSD
        ips+=($(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -3))
    elif command -v ipconfig &> /dev/null; then
        # Windows (在Git Bash中)
        ips+=($(ipconfig | grep 'IPv4' | awk '{print $NF}' | head -3))
    fi
    
    # 移除空值和重複
    printf '%s\n' "${ips[@]}" | sort -u | grep -v '^$' || echo "127.0.0.1"
}

# 備份現有憑證
backup_existing_certs() {
    if [[ -f "$SELF_SIGNED_DIR/server.crt" ]]; then
        local backup_dir="$SELF_SIGNED_DIR/backup_$(date +%Y%m%d_%H%M%S)"
        log_info "備份現有憑證到: $backup_dir"
        mkdir -p "$backup_dir"
        cp -r "$SELF_SIGNED_DIR"/*.{crt,key,csr,conf} "$backup_dir/" 2>/dev/null || true
        log_success "憑證備份完成"
    fi
}

# 生成憑證配置文件
generate_config() {
    local domain="$1"
    local country="$2"
    local state="$3"
    local city="$4"
    local org="$5"
    local ou="$6"
    local detect_ip="$7"
    
    log_info "生成憑證配置文件..."
    
    # 創建配置文件
    cat > "$SELF_SIGNED_DIR/server.conf" << EOF
[req]
default_bits = $KEY_SIZE
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C = $country
ST = $state
L = $city
O = $org
OU = $ou
CN = $domain

[v3_req]
keyUsage = digitalSignature, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
# 本地開發域名
DNS.1 = $domain
DNS.2 = localhost
DNS.3 = *.$domain
DNS.4 = pcms-staff.local
DNS.5 = pcms-local.test
DNS.6 = *.pcms-local.test
DNS.7 = pcmshrsystem.local
DNS.8 = pcmshrsystem

# 網段泛域名
DNS.7 = *.192.168.1.local
DNS.8 = *.192.168.12.local
DNS.9 = *.172.16.0.local
DNS.10 = *.10.0.0.local

# 基礎IP地址
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

    # 添加檢測到的IP地址
    if [[ "$detect_ip" == "true" ]]; then
        log_info "檢測本機IP地址..."
        local ip_counter=3
        while IFS= read -r ip; do
            if [[ -n "$ip" && "$ip" != "127.0.0.1" ]]; then
                echo "IP.$ip_counter = $ip" >> "$SELF_SIGNED_DIR/server.conf"
                log_info "添加IP: $ip"
                ((ip_counter++))
            fi
        done <<< "$(get_local_ips)"
    else
        # 添加常用網段IP
        cat >> "$SELF_SIGNED_DIR/server.conf" << EOF

# 常用網段IP
IP.3 = 192.168.1.1
IP.4 = 192.168.1.100
IP.5 = 192.168.12.1
IP.6 = 192.168.12.100
IP.7 = 172.16.0.1
IP.8 = 10.0.0.1
IP.11 = 172.188.118.42

EOF
    fi
    
    log_success "配置文件已生成: $SELF_SIGNED_DIR/server.conf"
}

# 生成SSL憑證
generate_certificate() {
    local domain="$1"
    
    log_info "生成SSL憑證和私鑰..."
    
    # 生成私鑰
    log_info "生成私鑰 ($KEY_SIZE bits)..."
    openssl genrsa -out "$SELF_SIGNED_DIR/server.key" $KEY_SIZE
    chmod 600 "$SELF_SIGNED_DIR/server.key"
    
    # 生成證書請求
    log_info "生成證書請求..."
    openssl req -new \
        -key "$SELF_SIGNED_DIR/server.key" \
        -out "$SELF_SIGNED_DIR/server.csr" \
        -config "$SELF_SIGNED_DIR/server.conf"
    
    # 生成自簽名證書
    log_info "生成自簽名證書 (有效期: $VALIDITY_DAYS 天)..."
    openssl x509 -req \
        -days $VALIDITY_DAYS \
        -in "$SELF_SIGNED_DIR/server.csr" \
        -signkey "$SELF_SIGNED_DIR/server.key" \
        -out "$SELF_SIGNED_DIR/server.crt" \
        -extensions v3_req \
        -extfile "$SELF_SIGNED_DIR/server.conf"
    
    log_success "憑證生成完成!"
}

# 驗證憑證
verify_certificate() {
    log_info "驗證憑證..."
    
    # 檢查憑證基本資訊
    log_info "憑證基本資訊:"
    openssl x509 -in "$SELF_SIGNED_DIR/server.crt" -noout -subject -dates
    
    # 檢查憑證和私鑰是否匹配
    local cert_hash=$(openssl x509 -in "$SELF_SIGNED_DIR/server.crt" -noout -modulus | openssl md5)
    local key_hash=$(openssl rsa -in "$SELF_SIGNED_DIR/server.key" -noout -modulus | openssl md5)
    
    if [[ "$cert_hash" == "$key_hash" ]]; then
        log_success "憑證和私鑰匹配 ✓"
    else
        log_error "憑證和私鑰不匹配!"
    fi
    
    # 顯示SAN域名
    log_info "支援的域名和IP:"
    openssl x509 -in "$SELF_SIGNED_DIR/server.crt" -noout -text | grep -A 10 "Subject Alternative Name" || true
}

# 顯示使用說明
show_usage_instructions() {
    log_header
    echo ""
    log_success "憑證生成完成! 檔案位置:"
    echo -e "${CYAN}  📄 憑證文件: $SELF_SIGNED_DIR/server.crt${NC}"
    echo -e "${CYAN}  🔑 私鑰文件: $SELF_SIGNED_DIR/server.key${NC}"
    echo -e "${CYAN}  📋 配置文件: $SELF_SIGNED_DIR/server.conf${NC}"
    echo ""
    
    log_info "使用方法:"
    echo "  1. 在 docker-compose.yml 中使用這些憑證"
    echo "  2. 將 server.crt 添加到系統信任的根憑證"
    echo "  3. 在瀏覽器中訪問 https://$DOMAIN"
    echo ""
    
    log_warning "信任憑證方法:"
    case "$OS" in
        "macOS")
            echo "  macOS: 雙擊 server.crt，在鑰匙圈中設定為「永遠信任」"
            ;;
        "Linux")
            echo "  Linux: sudo cp server.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates"
            ;;
        "Windows")
            echo "  Windows: 在 server.crt 上右鍵 → 安裝憑證 → 本機電腦 → 受信任的根憑證授權單位"
            ;;
    esac
    echo ""
}

# 主要執行邏輯
main() {
    # 預設值
    DOMAIN="$DEFAULT_DOMAIN"
    VALIDITY_DAYS="$DEFAULT_VALIDITY_DAYS"
    KEY_SIZE="$DEFAULT_KEY_SIZE"
    COUNTRY="$DEFAULT_COUNTRY"
    STATE="$DEFAULT_STATE"
    CITY="$DEFAULT_CITY"
    ORG="$DEFAULT_ORG"
    OU="$DEFAULT_OU"
    BACKUP="true"
    FORCE="false"
    DETECT_IP="false"
    
    # 解析命令列參數
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -v|--validity)
                VALIDITY_DAYS="$2"
                shift 2
                ;;
            -k|--key-size)
                KEY_SIZE="$2"
                shift 2
                ;;
            -c|--country)
                COUNTRY="$2"
                shift 2
                ;;
            -s|--state)
                STATE="$2"
                shift 2
                ;;
            -l|--city)
                CITY="$2"
                shift 2
                ;;
            -o|--org)
                ORG="$2"
                shift 2
                ;;
            -u|--ou)
                OU="$2"
                shift 2
                ;;
            --backup)
                BACKUP="true"
                shift
                ;;
            --no-backup)
                BACKUP="false"
                shift
                ;;
            --force)
                FORCE="true"
                shift
                ;;
            --detect-ip)
                DETECT_IP="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知選項: $1. 使用 -h 查看幫助"
                ;;
        esac
    done
    
    # 開始執行
    log_header
    
    # 檢查依賴
    check_dependencies
    
    # 顯示配置
    log_info "憑證配置:"
    echo -e "  域名: ${YELLOW}$DOMAIN${NC}"
    echo -e "  有效期: ${YELLOW}$VALIDITY_DAYS${NC} 天"
    echo -e "  密鑰大小: ${YELLOW}$KEY_SIZE${NC} bits"
    echo -e "  組織: ${YELLOW}$ORG${NC}"
    echo -e "  輸出目錄: ${YELLOW}$SELF_SIGNED_DIR${NC}"
    echo ""
    
    # 檢查現有憑證
    if [[ -f "$SELF_SIGNED_DIR/server.crt" ]] && [[ "$FORCE" != "true" ]]; then
        log_warning "發現現有憑證!"
        read -p "是否要覆蓋現有憑證? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "操作取消"
            exit 0
        fi
    fi
    
    # 創建目錄
    mkdir -p "$SELF_SIGNED_DIR"
    
    # 備份現有憑證
    if [[ "$BACKUP" == "true" ]]; then
        backup_existing_certs
    fi
    
    # 生成憑證
    generate_config "$DOMAIN" "$COUNTRY" "$STATE" "$CITY" "$ORG" "$OU" "$DETECT_IP"
    generate_certificate "$DOMAIN"
    verify_certificate
    
    # 顯示使用說明
    show_usage_instructions
}

# 執行主邏輯
main "$@"
