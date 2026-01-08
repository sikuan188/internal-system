# build stage
FROM node:20-alpine AS build
WORKDIR /app

# 先复制 package.json 和 package-lock.json
COPY package*.json ./

# 清除可能的缓存并重新安装依赖
RUN rm -rf node_modules package-lock.json
RUN npm install

# 然后复制其余文件
COPY . .

# 设置 PATH
ENV PATH /app/node_modules/.bin:$PATH

# 构建
RUN npm run build

# production stage
FROM nginx:stable-alpine AS production

# 複製自定義nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 複製構建文件到鏡像內（保留源以便啟動時同步到 volume）
COPY --from=build /app/build /app/build
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
# 每次啟動都將構建結果同步到 /usr/share/nginx/html（強制覆蓋，確保 volume 內容最新）
CMD ["sh", "-c", "rm -rf /usr/share/nginx/html/* && cp -rf /app/build/. /usr/share/nginx/html/ && nginx -g 'daemon off;'"]
