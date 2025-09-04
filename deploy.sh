#!/bin/bash

# 一键部署脚本

echo "🚀 开始部署代码活动跟踪系统..."

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置你的 Dify API 密钥"
    echo "   然后重新运行此脚本"
    exit 1
fi

# 构建并启动
echo "🔨 构建并启动服务..."
docker-compose up -d --build

echo "✅ 部署完成！"
echo "🌐 访问地址: http://localhost:3000"
echo "📊 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"