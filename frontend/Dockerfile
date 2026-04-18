# 构建阶段
FROM node:22-alpine AS build-stage
WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖（使用 --ignore-engines 忽略版本警告，确保安装继续）
RUN npm ci --legacy-peer-deps --ignore-engines

# 复制项目文件
COPY . .

# 设置环境变量
ENV NODE_ENV=production

# 执行构建
RUN npm run build

# 运行阶段
FROM nginx:stable-alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]