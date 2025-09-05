# 代码活动跟踪和AI报告生成系统

这是一个代码活动跟踪和AI报告生成系统，包含：
- **前端**：Vue 3 + Vite + Pinia + TailwindCSS 的单页应用
- **后端**：Python FastAPI 服务器，与阿里云 Codeup 和 Dify AI 集成

## 功能特性

- **用户认证**：基于阿里云Codeup的Cookie认证机制
- **项目管理**：获取用户授权的项目列表和详情
- **活动跟踪**：按时间范围获取项目提交和活动记录
- **AI报告生成**：整合项目活动数据生成智能分析报告
- **实时通信**：支持流式AI响应和实时数据更新

## 开发环境

### 前端开发 (Vue.js)
```bash
npm install           # 安装依赖
npm run dev           # 开发模式启动 (Vite开发服务器)
npm run build         # 生产构建
```

### 后端开发 (Python)
```bash
# 进入 python_server 目录
cd python_server

# 启动API服务器
python codeup_api.py

# 测试AI报告功能
python test_ai_report.py
```

## Docker部署

### 部署步骤
1. 构建前端：
```bash
npm run build
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件配置 Dify API 密钥
```

3. 启动服务：
```bash
docker-compose up -d --build
```

### 其他命令
```bash
docker-compose logs -f         # 查看日志
docker-compose down           # 停止服务
```

访问地址：http://localhost:5111

## Node.js版本要求

需要 Node.js `^20.19.0 || >=22.12.0`
