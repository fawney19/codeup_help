# 单容器部署 - 前后端一体化（使用已构建的前端）
FROM python:3.11-slim

WORKDIR /app

# 安装nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# 复制已构建的前端产物到nginx目录
COPY dist/ /var/www/html/

# 复制Python代码和依赖
COPY python_server/ ./

# 配置pip超时和镜像源，然后安装依赖
RUN pip config set global.timeout 300 && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir --timeout 300 -r requirements.txt

# 完整的nginx配置
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /var/www/html; \
    index index.html; \
    \
    # 前端路由 \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # API反向代理 \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_buffering off; \
        proxy_cache_bypass $http_upgrade; \
        proxy_connect_timeout 60s; \
        proxy_send_timeout 60s; \
        proxy_read_timeout 60s; \
    } \
}' > /etc/nginx/sites-available/default

# 启动脚本
RUN echo '#!/bin/bash\n\
nginx -g "daemon on;"\n\
uvicorn codeup_api:app --host 0.0.0.0 --port 8000\n\
' > /start.sh && chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]