# Dify 智能体配置指南

## 📖 概述

本指南说明如何创建和配置 Dify 聊天助手，用于生成代码项目周报。

### 应用场景
- 分析开发者的代码活动记录
- 生成结构化的周工作报告
- 支持项目进度分析

### 核心功能
- 生成简明工作内容列表（1. 2. 3. 格式）
- 过滤无意义提交（版本更新、代码格式化、Merge等）
- 自动生成下周工作计划建议
- 输出结构化JSON格式报告

---

## 🚀 第一步：创建 Dify 应用

### 登录 Dify 控制台
1. 访问 https://dify.hetunai.cn
2. 使用账号登录

### 创建新应用
1. 点击左侧 **"创建应用"** 按钮
2. 选择应用类型：**聊天助手 (Chat Assistant)** ✅
3. 命名应用：`代码活动周报生成器` 或 `CodeUp周报生成`
4. 点击 **创建**

---

## 🎯 第二步：配置系统提示词

### 进入提示词编辑页面
1. 应用创建后，自动进入配置页面
2. 找到 **系统提示词** / **System Prompt** 区域
3. 清空默认文本

### 复制以下完整提示词

```markdown
你是一个专业的代码项目活动分析助手，擅长分析开发者的工作记录并生成结构化的周报。

## 核心能力
1. 分析代码提交记录和项目活动数据
2. 生成专业的中文技术报告
3. 提供有洞察力的开发建议

## 输出格式要求 - 非常重要！
你必须严格按照以下JSON格式输出，不要添加任何markdown代码块标记（如```json```）：

{
  "developer": "开发者姓名",
  "position": "开发者岗位",
  "work_summary": "工作完成情况的详细描述，支持markdown格式，按日期分组",
  "next_plan": ["计划1", "计划2", "计划3"]
}

## work_summary 格式规范
必须按以下格式组织内容，使用 \n 作为换行符，不按日期分组，直接列出所有工作项：

1. 第一项工作
2. 第二项工作
3. 第三项工作
4. 第四项工作

示例：
1. 完成用户认证模块的开发和测试
2. 修复登录页面的样式问题
3. 优化数据库查询性能
4. 实现AI报告生成功能

## 过滤无意义提交 - 关键要求
必须排除以下内容，只保留有实际业务价值的工作：

❌ **版本号更改**：
- 如：bump version to 1.0.1
- 如：update version
- 如：v1.0.2
- 如：release 2.0.0

❌ **代码格式化/代码风格**：
- 如：format code
- 如：prettier
- 如：eslint fix
- 如：code style update

❌ **Merge 提交**：
- 如：Merge branch 'feature/xxx'
- 如：Merge pull request #123
- 如：Merge develop into main

❌ **构建文件/自动化**：
- 如：update package-lock.json
- 如：rebuild
- 如：update dist
- 如：ci: update dependencies
- 如：deps: update packages

✅ 只保留有实际业务价值的工作，如：
- 功能开发和实现
- Bug 修复
- 性能优化
- 文档更新
- API 接口改进

## next_plan 要求
- 必须是字符串数组格式
- 至少包含3-5个具体的工作计划
- 每个计划要具体可执行
- 基于本周工作内容合理延伸

示例：
["完善用户认证模块的单元测试覆盖率", "优化AI报告生成的前端展示效果", "进行代码review并处理技术债务"]

## 分析要求
- 使用中文撰写
- 内容要专业且有洞察力
- 基于实际活动数据进行分析
- developer字段必须从"用户补充信息"或活动数据中提取真实姓名
- position字段必须从"用户补充信息"中提取，如未提供则推测（如：前端工程师、后端工程师、全栈工程师等）

## 关键注意事项
⚠️ 必须输出纯JSON格式，没有 ```json ``` 标记
⚠️ 不要添加任何解释性文字
⚠️ 确保JSON格式完全正确，可被JSON.parse()解析
⚠️ 如果无法从提供的数据中提取developer或position，请合理推测但要保持专业
⚠️ work_summary中的日期必须准确，按照提供的活动数据时间
```

---

## ⚙️ 第三步：配置模型参数

### 找到模型配置区域
通常在应用界面的右侧或上方

### 设置以下参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| **模型** | GPT-4 / Claude-3.5-Sonnet | 选择支持长文本的模型 |
| **温度 (Temperature)** | 0.7 | 平衡创意性和准确性 |
| **最大Token** | 3000-4000 | 确保能输出完整报告 |
| **Top P** | 0.9 | 默认值即可 |

### 启用选项
- ✅ **JSON Mode** （如果可用）- 强制JSON格式输出
- ✅ **流式响应** (Streaming) - 支持实时返回内容

---

## 🧪 第四步：在 Dify 中测试

### 进入测试区域
在应用界面找到 **测试** 或 **预览** 按钮

### 输入测试数据

将以下内容复制到输入框：

```
项目：测试项目
时间范围：本周
活动总结：
统计概览：
• 推送次数：5 次
• 提交数量：12 个
• 文件变更：45 处
• 活跃天数：3 天

详细提交记录：
=== 2025年1月15日 星期一 ===
1. [09:30] Push to master
   提交内容:
   1) a1b2c3d - 实现用户认证功能
   2) e4f5g6h - 修复登录bug

=== 2025年1月16日 星期二 ===
1. [14:20] Push to develop
   提交内容:
   1) i7j8k9l - 添加AI报告生成接口

用户补充信息：
我叫张三，是前端工程师。本周主要聚焦在用户认证模块的开发，下周计划开始项目管理功能的开发。
```

### 验证输出

**预期输出示例：**

```json
{
  "developer": "张三",
  "position": "前端工程师",
  "work_summary": "1. 实现用户认证功能，包括登录、注册、密码重置\n2. 修复登录相关bug，提升系统稳定性\n3. 添加AI报告生成接口，完善后端服务",
  "next_plan": ["完善用户认证模块的单元测试覆盖率", "优化AI报告生成的前端展示效果", "进行代码review并处理技术债务"]
}
```

### ✅ 验证清单

- [ ] 输出是纯JSON，没有 ``` 标记
- [ ] 可以直接用 `JSON.parse()` 解析
- [ ] developer 字段正确提取
- [ ] position 字段正确提取
- [ ] work_summary 是简单列表格式（1. 2. 3.），不包含日期
- [ ] next_plan 是数组，包含 3-5 个计划

如果测试不通过，调整系统提示词，重点强调"必须输出纯JSON"和"不要添加代码块标记"。

---

## 🔑 第五步：发布应用并获取 API Key

### 点击发布
1. 应用配置完成后，点击右上角 **"发布"** 按钮
2. 等待应用发布完成

### 获取 API 密钥
1. 进入应用详情页
2. 找到 **API 访问** 或 **API Keys** 部分
3. 点击 **创建 API 密钥** 或 **New API Key**
4. 为密钥命名：`codeup-report-generator`
5. 系统生成密钥（格式：`app-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
6. ⚠️ **立即复制密钥**，此页面关闭后将无法再看到

---

## 🔧 第六步：配置环境变量

### 创建或编辑 .env 文件

**文件位置**: `python_server/.env`

```bash
# Dify AI 配置
DIFY_BASE_URL=https://dify.hetunai.cn/v1
DIFY_API_KEY=app-你从Dify复制的密钥

# 可选：日志级别
LOG_LEVEL=INFO
```

### ⚠️ 重要说明

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `DIFY_BASE_URL` | `https://dify.hetunai.cn/v1` | 必须以 `/v1` 结尾，不要加 `/chat-messages` |
| `DIFY_API_KEY` | `app-xxxxx` | 从Dify控制台复制，必须以 `app-` 开头 |

### .env 文件安全说明
- ✅ 已在 `.gitignore` 中，不会被提交到仓库
- ⚠️ 不要在公开场合分享 API Key
- ⚠️ 如果 Key 泄露，立即在 Dify 中删除并重新生成

---

## ✅ 第七步：验证集成

### 运行后端测试脚本

```bash
cd python_server
python test_ai_report.py
```

**预期输出：**
```
🚀 直接测试Dify AI功能
==================================================
📊 开始测试Dify AI流式报告生成...
📡 请求URL: https://dify.hetunai.cn/v1/chat-messages
📝 正在生成报告...

{"developer": "张三", "position": "前端工程师", ...}

✅ Dify AI报告生成测试成功!
✨ 所有测试完成!
```

### 启动完整系统

```bash
# 终端1：启动后端
cd python_server
python codeup_api.py

# 终端2：启动前端
cd /Users/elky/WebstormProjects/code_up_help
npm run dev
```

### 前端测试

1. 登录系统
2. 选择一个项目
3. 选择时间范围（如本周）
4. 点击 **生成 AI 报告**
5. 在弹出框的补充信息中输入：
   ```
   我是李四，岗位是全栈工程师。这周主要完成了用户认证功能的开发。
   ```
6. 点击 **生成报告**
7. 验证报告是否正确显示

---

## 🐛 故障排查

### 问题 1: 返回的不是纯 JSON

**症状**: 输出包含 ` ```json ``` ` 标记或有额外文本

**原因**: 模型在输出中添加了 markdown 代码块

**解决方案**:
1. 回到 Dify 系统提示词
2. 在开头添加更强的指示：
   ```
   你必须严格遵循以下规则：
   1. 只输出纯JSON，不要添加任何其他文本
   2. 不要使用 ```json 或 ``` 标记
   3. 不要添加任何解释或说明
   ```
3. 尝试启用 **JSON Mode**（如果模型支持）
4. 降低温度参数到 0.5

### 问题 2: JSON 解析失败

**症状**: 前端显示 "JSON解析失败"

**原因**: JSON 格式不规范（如未转义的引号、非法字符等）

**解决方案**:
1. 在 Dify 测试区检查原始输出
2. 使用在线 JSON 验证器：https://jsonlint.com/
3. 检查 work_summary 中的特殊字符是否正确转义
4. 确保所有的换行都使用 `\n` 而不是实际的换行符

### 问题 3: developer 或 position 为空

**症状**: 这两个字段的值是空字符串或 null

**原因**: 未从用户补充信息中提取

**解决方案**:
1. 更新系统提示词，明确要求：
   ```
   developer字段必须从"用户补充信息"中提取
   如果找不到，可以推测但必须保持专业
   ```
2. 在测试数据中确保包含用户补充信息
3. 提供更清晰的补充信息格式，如：
   ```
   用户补充信息：
   姓名：李四
   岗位：全栈工程师
   ```

### 问题 4: API 连接失败

**症状**: 错误信息 "连接AI服务失败" 或 "DIFY_API_KEY未设置"

**原因**: 环境变量配置错误

**解决方案**:
1. 检查 .env 文件是否存在：
   ```bash
   ls -la python_server/.env
   ```
2. 验证环境变量格式：
   ```bash
   cat python_server/.env
   # 输出应该是：
   # DIFY_BASE_URL=https://dify.hetunai.cn/v1
   # DIFY_API_KEY=app-xxxxx
   ```
3. 确保密钥以 `app-` 开头
4. URL 以 `/v1` 结尾，不包含 `/chat-messages`
5. 重启后端服务使配置生效

### 问题 5: 超时错误

**症状**: 生成报告时出现超时错误

**原因**: Dify 响应太慢或网络连接问题

**解决方案**:
1. 检查网络连接
2. 在 Dify 中测试接口是否响应正常
3. 检查后端日志中的详细错误信息
4. 增加后端超时时间（codeup_api.py:524）

---

## 📊 数据流程

```
前端用户点击"生成AI报告"
    ↓
前端收集项目活动数据 + 用户补充信息
    ↓
调用后端 API /api/v1/projects/{id}/reports/ai-generate
    ↓
后端使用 DifyClient 调用 Dify API
    ↓
Dify 根据系统提示词分析数据
    ↓
Dify 返回 JSON 格式报告
    ↓
后端返回响应给前端
    ↓
前端解析 JSON 并展示结构化报告
```

---

## 📝 API 集成示例

### 后端调用 Dify

```python
from dify_client import dify_client
from models import DifyRequest

# 构建请求
dify_request = DifyRequest(
    query="项目：xxx\n活动数据：...",
    response_mode="blocking",
    user="frontend_user",
    conversation_id=""
)

# 调用 Dify API
response = dify_client.create_blocking_response(dify_request)
print(response)  # 返回 JSON 格式的报告
```

### 前端接收报告

```javascript
// src/views/ProjectDetail.vue
const response = await projectsApi.generateAIReportBlocking(projectId, reportData)

if (response && response.data && response.data.answer) {
  const reportContent = response.data.answer

  try {
    // 尝试解析为 JSON
    const parsedReport = JSON.parse(reportContent)
    if (parsedReport.developer && parsedReport.position) {
      // 使用结构化展示
      aiReportData.value = parsedReport
    }
  } catch (error) {
    // 降级为文本展示
    aiReport.value = reportContent
  }
}
```

---

## 🔄 后续维护

### 定期检查
- [ ] 每周测试一次报告生成功能
- [ ] 如果 API Key 泄露，立即重新生成
- [ ] 定期查看 Dify 的使用配额和费用

### 优化提示词
如果发现报告质量不佳，可以：
1. 收集实际的差质量报告样本
2. 在系统提示词中添加更具体的要求
3. 提供更多的示例数据
4. 调整模型参数

### 版本更新
- Dify 平台更新后，可能需要调整 API 调用方式
- 定期检查官方文档：https://docs.dify.ai/

---

## 📞 相关链接

- Dify 官方网站：https://dify.hetunai.cn
- Dify 文档：https://docs.dify.ai/
- 项目代码：`python_server/dify_client.py`、`python_server/codeup_api.py`
- 前端集成：`src/views/ProjectDetail.vue`、`src/components/AIReportDisplay.vue`

---

## 📋 快速参考

### 环境变量模板
```bash
DIFY_BASE_URL=https://dify.hetunai.cn/v1
DIFY_API_KEY=app-your-key-here
LOG_LEVEL=INFO
```

### 测试命令
```bash
cd python_server
python test_ai_report.py
```

### 启动命令
```bash
# 后端
python python_server/codeup_api.py

# 前端
npm run dev
```

### JSON 验证工具
- Online JSON Validator: https://jsonlint.com/
- JSON Formatter: https://jsonformatter.org/

---

**文档最后更新**: 2025年1月

**维护人员**: 开发团队

**版本**: 1.0
