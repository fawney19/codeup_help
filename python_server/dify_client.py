"""
Dify AI客户端模块
"""
import json
import requests
from typing import List, Dict
from fastapi import HTTPException
from models import DifyRequest
from logger_config import setup_logger, INFO
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger = setup_logger(
    name=__name__,
    level=globals().get(log_level, INFO),
    use_color=True,
    show_time=True,
    filter_libs=True
)


class DifyAIClient:
    """Dify AI客户端，处理AI报告生成"""
    
    def __init__(self):
        self.base_url = os.getenv("DIFY_BASE_URL", "https://dify.hetunai.cn/v1")
        self.api_key = os.getenv("DIFY_API_KEY")
        
        if not self.api_key:
            raise ValueError("DIFY_API_KEY环境变量未设置，请在.env文件中配置")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_report_prompt(self, report_type: str, activities_data: List[Dict], 
                              project_name: str, time_range_desc: str, 
                              additional_context: str = "") -> str:
        """根据报告类型和活动数据生成合适的提示词"""
        
        # 格式化活动数据
        activities_summary = self._format_activities_for_prompt(activities_data)
        
        base_context = f"""
项目名称：{project_name}
时间范围：{time_range_desc}
活动数据：
{activities_summary}

额外说明：{additional_context}
        """.strip()
        
        if report_type == "activity_summary":
            prompt = f"""
请基于以下代码项目活动数据，生成一份详细的活动总结报告：

{base_context}

请按以下结构生成报告：
1. 📊 活动概览
2. 💻 主要贡献
3. 📈 趋势分析  
4. 🎯 重点关注
5. 💡 建议与展望

要求：
- 使用中文撰写
- 内容要专业且有洞察力
- 突出重要的开发活动和趋势
- 提供有价值的分析和建议
"""
        elif report_type == "code_review":
            prompt = f"""
请基于以下代码项目活动数据，生成一份代码审查报告：

{base_context}

请按以下结构生成报告：
1. 🔍 代码变更概览
2. 📝 主要提交分析
3. ⚠️ 潜在关注点
4. ✅ 最佳实践
5. 🚀 改进建议

要求：
- 使用中文撰写
- 重点关注代码质量和开发规范
- 基于提交信息分析潜在问题
- 提供具体的改进建议
"""
        elif report_type == "progress_report":
            prompt = f"""
请基于以下代码项目活动数据，生成一份项目进度报告：

{base_context}

请按以下结构生成报告：
1. 📅 进度概述
2. ✅ 完成情况
3. 🔄 开发活跃度
4. 📊 统计数据
5. 🎯 下一步计划

要求：
- 使用中文撰写
- 突出项目进度和里程碑
- 分析开发效率和团队协作
- 提供项目状态的清晰视图
"""
        else:
            prompt = f"""
请基于以下代码项目活动数据，生成一份综合报告：

{base_context}

请提供专业的分析和洞察，包括活动概览、主要发现和建议。使用中文撰写。
"""
        
        return prompt
    
    def _format_activities_for_prompt(self, activities_data: List[Dict]) -> str:
        """将活动数据格式化为适合AI处理的文本"""
        if not activities_data:
            return "暂无活动数据"
        
        formatted_activities = []
        for activity in activities_data[:20]:  # 限制数量避免token过多
            activity_text = f"• {activity.get('created_at', '')} - {activity.get('author_name', '')} - {activity.get('action_name', '')} - {activity.get('target_title', '')}"
            formatted_activities.append(activity_text)
        
        if len(activities_data) > 20:
            formatted_activities.append(f"... 等共{len(activities_data)}条活动记录")
        
        return "\n".join(formatted_activities)
    
    def create_streaming_response(self, dify_request: DifyRequest):
        """创建流式响应"""
        try:
            url = f"{self.base_url}/chat-messages"
            payload = dify_request.model_dump(exclude_none=True)
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            # 处理流式响应
            complete_answer = ""
            
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # 去掉 'data: ' 前缀
                        if data.get('event') == 'message':
                            # answer字段本身就是增量文本，直接发送
                            incremental_text = data.get('answer', '')
                            if incremental_text:
                                yield f"data: {json.dumps({'type': 'content', 'content': incremental_text}, ensure_ascii=False)}\n\n"
                                complete_answer += incremental_text
                        elif data.get('event') == 'message_end':
                            yield f"data: {json.dumps({'type': 'done', 'message': '生成完成'}, ensure_ascii=False)}\n\n"
                            break
                    except json.JSONDecodeError:
                        continue
            
            # 发送结束事件
            yield f"data: {json.dumps({'type': 'done', 'message': 'AI报告生成完成'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_event = {
                'type': 'error',
                'message': f'AI报告生成失败: {str(e)}'
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
    
    def create_blocking_response(self, dify_request: DifyRequest) -> Dict:
        """创建阻塞式响应"""
        try:
            url = f"{self.base_url}/chat-messages"
            payload = dify_request.model_dump(exclude_none=True)
            payload["response_mode"] = "blocking"  # 确保使用阻塞模式
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Dify API调用失败: {e}")
            raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")


# 创建Dify客户端实例
dify_client = DifyAIClient()