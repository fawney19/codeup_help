"""
数据模型定义
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class BaseResponse(BaseModel):
    """统一响应基类"""
    status: StatusEnum
    message: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuccessResponse(BaseResponse):
    """成功响应"""
    status: StatusEnum = StatusEnum.SUCCESS
    data: Any


class ErrorResponse(BaseResponse):
    """错误响应"""
    status: StatusEnum = StatusEnum.ERROR
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginationInfo(BaseModel):
    """分页信息"""
    page: int
    per_page: int
    total: int
    total_pages: int


# ===== 请求模型定义 =====

class CookieAuthRequest(BaseModel):
    """Cookie认证请求"""
    cookies: str = Field(..., description="Codeup网站的完整cookies字符串")


class ProjectsQueryParams(BaseModel):
    """项目查询参数"""
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field("", description="搜索关键词")
    archived: bool = Field(False, description="是否包含归档项目")
    all_pages: bool = Field(False, description="是否获取所有页")


class ActivitiesQueryParams(BaseModel):
    """活动查询参数"""
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(20, ge=1, le=100, description="每页数量")
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('日期格式必须为 YYYY-MM-DD')
        return v


# ===== AI报告生成相关模型 =====

class AIReportRequest(BaseModel):
    """AI生成报告请求"""
    project_id: int = Field(..., description="项目ID")
    report_type: str = Field("activity_summary", description="报告类型：activity_summary(活动总结)、code_review(代码审查)、progress_report(进度报告)")
    time_range: str = Field("week", description="时间范围：today(今天)、week(本周)、month(本月)、custom(自定义)")
    start_date: Optional[str] = Field(None, description="自定义开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="自定义结束日期 (YYYY-MM-DD)")
    additional_context: Optional[str] = Field("", description="额外上下文信息")
    response_mode: str = Field("streaming", description="响应模式：streaming(流式)、blocking(阻塞)")
    user: str = Field("codeup_user", description="用户标识")
    conversation_id: Optional[str] = Field(None, description="会话ID，用于继续对话")


class DifyFileInfo(BaseModel):
    """Dify文件信息"""
    type: str = Field(..., description="文件类型")
    transfer_method: str = Field("remote_url", description="传递方式：remote_url、local_file")
    url: Optional[str] = Field(None, description="文件URL（remote_url时使用）")
    upload_file_id: Optional[str] = Field(None, description="上传文件ID（local_file时使用）")


class DifyRequest(BaseModel):
    """Dify API请求模型"""
    query: str = Field(..., description="用户输入/提问内容")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="App定义的变量值")
    response_mode: str = Field("streaming", description="响应模式")
    user: str = Field("codeup_user", description="用户标识")
    conversation_id: Optional[str] = Field(None, description="会话ID")
    files: Optional[List[DifyFileInfo]] = Field(None, description="文件列表")
    auto_generate_name: bool = Field(True, description="自动生成标题")
    workflow_id: Optional[str] = Field(None, description="工作流ID")
    trace_id: Optional[str] = Field(None, description="链路追踪ID")