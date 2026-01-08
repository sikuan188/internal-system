#!/bin/bash

# PCMS SSL 统一管理脚本
# 支持自签名证书、Let's Encrypt 和动态 SSL 配置
# 兼容 Linux/macOS/Windows(WSL)

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$SSL_DIR")")"

# 默认配置
DOMAIN_NAME="${DOMAIN_NAME:-localhost}"
SSL_TYPE="${SSL_TYPE:-self-signed}"  # self-signed, letsencrypt, dynamic
CERT_DIR="$SSL_DIR/$SSL_TYPE"
EMAIL="${SSL_EMAIL:-admin@${DOMAIN_NAME}}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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
}

# 显示帮助信息
show_help() {
    cat << EOF
PCMS SSL 统一管理脚本

用法: $0 [选项] <命令>

命令:
    generate        生成 SSL 证书
    install         安装 Let's Encrypt 证书
    deploy          部署 SSL 配置
    clean           清理证书文件
    status          检查证书状态

选项:
    --type TYPE     证书类型 (self-signed|letsencrypt|dynamic)
    --domain NAME   域名 (默认: localhost)
    --email EMAIL   邮箱地址 (Let's Encrypt 用)
    --force         强制重新生成证书
    --help          显示此帮助信息

环境变量:
    SSL_TYPE        证书类型
    DOMAIN_NAME     域名
    SSL_EMAIL       邮箱地址

示例:
    $0 generate --type self-signed --domain localhost
    $0 install --type letsencrypt --domain yourdomain.com --email admin@yourdomain.com
    $0 deploy
    $0 status
EOF
}

# 检查依赖
check_dependencies() {
    local deps=("openssl")
    
    if [[ "$SSL_TYPE" == "letsencrypt" ]]; then
        deps+=("docker")
    fi
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "缺少依赖: $dep"
            exit 1
        fi
    done
}

# 生成自签名证书
generate_self_signed() {
    log_info "生成自签名 SSL 证书..."
    
    mkdir -p "$SSL_DIR/self-signed"
    cd "$SSL_DIR/self-signed"
    
    # 创建证书配置
    cat > server.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = HK
ST = Hong Kong
L = Hong Kong
O = Pui Ching Middle School
OU = IT Department
CN = $DOMAIN_NAME

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN_NAME
DNS.2 = localhost
DNS.3 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
    
    # 生成私钥
    openssl genrsa -out server.key 2048
    
    # 生成证书签名请求
    openssl req -new -key server.key -out server.csr -config server.conf
    
    # 生成自签名证书
    openssl x509 -req -in server.csr -signkey server.key -out server.crt -days 365 -extensions v3_req -extfile server.conf
    
    # 设置权限
    chmod 600 server.key
    chmod 644 server.crt
    
    log_success "自签名证书生成完成"
    log_info "证书位置: $SSL_DIR/self-signed/"
    log_warning "浏览器将显示安全警告，这是正常的"
}

# 安装 Let's Encrypt 证书
install_letsencrypt() {
    log_info "安装 Let's Encrypt 证书..."
    
    if [[ "$DOMAIN_NAME" == "localhost" || "$DOMAIN_NAME" =~ ^127\. || "$DOMAIN_NAME" =~ ^192\.168\. ]]; then
        log_error "Let's Encrypt 不支持本地域名: $DOMAIN_NAME"
        log_info "请使用公网域名或选择自签名证书"
        exit 1
    fi
    
    mkdir -p "$SSL_DIR/letsencrypt"
    mkdir -p "$PROJECT_ROOT/docker/data/certbot/webroot"
    
    # 使用 Docker 运行 Certbot
    docker run --rm \
        -v "$SSL_DIR/letsencrypt:/etc/letsencrypt" \
        -v "$PROJECT_ROOT/docker/data/certbot/webroot:/var/www/certbot" \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN_NAME"
    
    # 复制证书到标准位置
    cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" "$SSL_DIR/letsencrypt/server.crt"
    cp "/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem" "$SSL_DIR/letsencrypt/server.key"
    
    log_success "Let's Encrypt 证书安装完成"
    log_info "证书位置: $SSL_DIR/letsencrypt/"
}

# 生成动态 SSL 配置
generate_dynamic() {
    log_info "生成动态 SSL 配置..."
    
    # 根据域名类型选择证书
    if [[ "$DOMAIN_NAME" == "localhost" || "$DOMAIN_NAME" =~ ^127\. || "$DOMAIN_NAME" =~ ^192\.168\. ]]; then
        SSL_TYPE="self-signed"
        generate_self_signed
    else
        SSL_TYPE="letsencrypt"
        install_letsencrypt
    fi
    
    log_success "动态 SSL 配置完成"
}

# 部署 SSL 配置
deploy_ssl() {
    log_info "部署 SSL 配置..."
    
    # 检查证书是否存在
    if [[ ! -f "$CERT_DIR/server.crt" || ! -f "$CERT_DIR/server.key" ]]; then
        log_warning "证书文件不存在，将自动生成"
        generate_certificate
    fi
    
    # 更新 docker-compose 配置
    export SSL_ENABLED=true
    export DOMAIN_NAME="$DOMAIN_NAME"
    
    # 创建环境配置文件
    cat > "$SSL_DIR/docker-ssl.env" << EOF
# PCMS SSL 配置
SSL_ENABLED=true
SSL_TYPE=$SSL_TYPE
DOMAIN_NAME=$DOMAIN_NAME
HTTPS_PORT=443
HTTP_PORT=80

# 自动生成时间戳
GENERATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
    
    log_success "SSL 配置部署完成"
    log_info "使用以下命令启动服务:"
    log_info "  docker-compose --env-file ssl/docker-ssl.env up -d"
}

# 清理证书文件
clean_certificates() {
    log_info "清理证书文件..."
    
    read -p "确定要删除所有证书文件吗? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$SSL_DIR/self-signed"
        rm -rf "$SSL_DIR/letsencrypt" 
        rm -f "$SSL_DIR/docker-ssl.env"
        log_success "证书文件已清理"
    else
        log_info "操作已取消"
    fi
}

# 检查证书状态
check_status() {
    log_info "检查证书状态..."
    
    for cert_type in "self-signed" "letsencrypt"; do
        cert_file="$SSL_DIR/$cert_type/server.crt"
        if [[ -f "$cert_file" ]]; then
            log_info "[$cert_type] 证书信息:"
            openssl x509 -in "$cert_file" -noout -subject -dates -issuer | sed 's/^/  /'
            echo
        else
            log_warning "[$cert_type] 证书不存在: $cert_file"
        fi
    done
}

# 生成证书的统一入口
generate_certificate() {
    case "$SSL_TYPE" in
        "self-signed")
            generate_self_signed
            ;;
        "letsencrypt")
            install_letsencrypt
            ;;
        "dynamic")
            generate_dynamic
            ;;
        *)
            log_error "未知的证书类型: $SSL_TYPE"
            log_info "支持的类型: self-signed, letsencrypt, dynamic"
            exit 1
            ;;
    esac
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)
                SSL_TYPE="$2"
                shift 2
                ;;
            --domain)
                DOMAIN_NAME="$2"
                shift 2
                ;;
            --email)
                EMAIL="$2"
                shift 2
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            generate|install|deploy|clean|status)
                COMMAND="$1"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查命令
    if [[ -z "$COMMAND" ]]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
    
    # 显示配置
    log_info "PCMS SSL 管理器"
    log_info "命令: $COMMAND"
    log_info "证书类型: $SSL_TYPE"
    log_info "域名: $DOMAIN_NAME"
    log_info "邮箱: $EMAIL"
    echo
    
    # 检查依赖
    check_dependencies
    
    # 执行命令
    case "$COMMAND" in
        generate)
            generate_certificate
            ;;
        install)
            install_letsencrypt
            ;;
        deploy)
            deploy_ssl
            ;;
        clean)
            clean_certificates
            ;;
        status)
            check_status
            ;;
    esac
}

# 执行主函数
main "$@"