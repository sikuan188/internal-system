#啟動步驟

- 1. 確認 Docker Desktop 已啟動
- 2. 進入專案根目錄後執行：

```
mkdir -p backend/logs docker/backup

cd docker/ssl
chmod +x generate-self-signed.sh
./generate-self-signed.sh --domain localhost --force
cd ..

docker compose up --build
```
