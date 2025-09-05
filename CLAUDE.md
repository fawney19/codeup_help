# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

这是一个代码活动跟踪和AI报告生成系统，包含：
- **前端**：Vue 3 + Vite + Pinia + TailwindCSS 的单页应用
- **后端**：Python FastAPI 服务器，与阿里云 Codeup 和 Dify AI 集成

## 开发命令

### 前端开发 (Vue.js)
```bash
npm install           # 安装依赖
npm run dev           # 开发模式启动 (Vite开发服务器)
npm run build         # 生产构建
npm run preview       # 预览构建结果
```

### 后端开发 (Python)
```bash
# 进入 python_server 目录
cd python_server

# 启动API服务器
python codeup_api.py
# 或使用特定Python环境
/opt/homebrew/Caskroom/miniconda/base/envs/Test/bin/python codeup_api.py

# 测试AI报告功能
python test_ai_report.py
# 或使用特定Python环境
/opt/homebrew/Caskroom/miniconda/base/envs/Test/bin/python test_ai_report.py
```

### Docker部署
```bash
# 部署步骤
npm run build                  # 本地构建前端
docker-compose up -d --build   # 构建并启动容器

# 其他命令
docker-compose logs -f         # 查看日志
docker-compose down           # 停止服务
```

## 系统架构

### 前端架构 (src/)
- **路由系统**：基于Vue Router的认证路由，支持路由守卫
- **状态管理**：使用Pinia stores，主要包含：
  - `auth.js`: 用户认证状态，Cookie管理
  - `projects.js`: 项目数据管理
- **主要页面**：
  - Login: Cookie认证登录页面
  - ProjectList: 项目列表和统计
  - ProjectDetail: 项目详情和AI报告生成
- **API服务**：`services/api.js` 统一处理HTTP请求和响应

### 后端架构 (python_server/)
- **主服务**：`codeup_api.py` - FastAPI应用，提供RESTful API
- **核心模块**：
  - `codeup_client.py`: 阿里云Codeup API客户端
  - `dify_client.py`: Dify AI服务客户端
  - `models.py`: 数据模型和响应结构
  - `utils.py`: 通用工具函数
  - `logger_config.py`: 日志配置

### 关键集成点
1. **认证流程**：前端通过Cookie认证，后端验证login_ticket
2. **项目数据**：从Codeup API获取项目信息和活动记录
3. **AI报告**：通过Dify API生成项目活动分析报告
4. **流式响应**：支持AI响应的实时流式传输

## 主要功能模块

- **用户认证**：基于阿里云Codeup的Cookie认证机制
- **项目管理**：获取用户授权的项目列表和详情
- **活动跟踪**：按时间范围获取项目提交和活动记录
- **AI报告生成**：整合项目活动数据生成智能分析报告
- **实时通信**：支持流式AI响应和实时数据更新

## Node.js版本要求

需要 Node.js `^20.19.0 || >=22.12.0`