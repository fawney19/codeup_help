from fastapi import FastAPI, HTTPException, Header, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime, timedelta
import uvicorn
import json
import asyncio
import os

# 导入分离的模块
from models import *
from utils import *
from dify_client import dify_client
from codeup_client import CodeupClient, AuthenticationError, UserInfo
from logger_config import setup_logger, INFO, DEBUG, WARNING

# 配置日志
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger = setup_logger(
    name=__name__,
    level=globals()[log_level] if log_level in ['DEBUG', 'INFO', 'WARNING'] else INFO,
    use_color=True,
    show_time=True,
    filter_libs=True
)

app = FastAPI(
    title="Codeup API v1",
    description="阿里云Codeup代码仓库API服务 - 重构版",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    # 跳过OPTIONS请求的日志
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    
    # 构建请求信息
    query_info = f" ?{dict(request.query_params)}" if request.query_params else ""
    logger.info(f"📥 {request.method} {request.url.path}{query_info}")
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"📤 {response.status_code} - {process_time:.3f}s")
    
    return response


# ===== 异常处理 =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return create_error_response(
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
        status_code=exc.status_code
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """值错误处理器"""
    return create_error_response(
        message=str(exc),
        error_code="VALIDATION_ERROR",
        status_code=400
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return create_error_response(
        message="服务器内部错误",
        error_code="INTERNAL_SERVER_ERROR",
        details={"error": str(exc)} if app.debug else None,
        status_code=500
    )

# ===== API端点 =====

@app.get("/", response_model=SuccessResponse)
async def root():
    """API根目录 - 获取服务信息"""
    return create_success_response({
        "name": "Codeup API v1",
        "version": "1.0.0",
        "description": "阿里云Codeup代码仓库API服务",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "projects": "/api/v1/projects",
            "ai_reports": "/api/v1/projects/{project_id}/reports/ai-generate",
            "ai_reports_stream": "/api/v1/projects/{project_id}/reports/ai-generate-stream",
            "ai_chat": "/api/v1/ai/chat",
            "ai_chat_stream": "/api/v1/ai/chat-stream"
        }
    }, "欢迎使用Codeup API v1")

@app.get("/health", response_model=SuccessResponse)
async def health_check():
    """健康检查端点"""
    return create_success_response({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }, "服务运行正常")

# ===== 认证相关接口 =====



@app.post("/api/v1/auth/login-with-cookies", response_model=SuccessResponse)
async def login_with_cookies(request: CookieAuthRequest):
    """
    使用Cookies登录验证
    
    从cookies字符串中提取login_ticket并验证用户信息
    """
    try:
        # 从cookies中提取login_ticket
        login_ticket = extract_login_ticket_from_cookies(request.cookies)
        
        if not login_ticket:
            return create_error_response(
                "无法从Cookies中找到login_aliyunid_ticket",
                "LOGIN_TICKET_NOT_FOUND",
                details={"provided_cookies": request.cookies[:100] + "..." if len(request.cookies) > 100 else request.cookies},
                status_code=400
            )
        
        # 使用提取的login_ticket创建客户端并验证
        client = CodeupClient(login_ticket)
        user_info = client.get_user_info()
        
        if user_info:
            # 保存客户端实例
            clients[login_ticket] = client
            
            return create_success_response({
                "user": {
                    "id": user_info.id,
                    "name": user_info.name,
                    "email": user_info.email,
                    "avatar_url": user_info.avatar_url
                },
                "cookies": request.cookies,  # 返回完整cookies给前端保存
                "authenticated": True,
                "extracted_login_ticket": login_ticket[:50] + "..." if len(login_ticket) > 50 else login_ticket
            }, "使用Cookies登录成功")
        else:
            return create_error_response(
                "登录失败，提取的Login Ticket无效",
                "AUTH_FAILED",
                details={"extracted_login_ticket": login_ticket[:20] + "..." if len(login_ticket) > 20 else login_ticket},
                status_code=401
            )
    except Exception as e:
        logger.error(f"Cookie login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cookie登录验证失败: {str(e)}")

# ===== 用户相关接口 =====

@app.get("/api/v1/users/me", response_model=SuccessResponse)
async def get_current_user(cookies: str = Header(..., alias="X-Codeup-Cookies")):
    """获取当前用户信息"""
    try:
        client = get_client_from_cookies(cookies)
        user_info = client.get_user_info()
        
        if user_info:
            return create_success_response({
                "id": user_info.id,
                "name": user_info.name,
                "email": user_info.email,
                "avatar_url": user_info.avatar_url
            }, "获取用户信息成功")
        else:
            return create_error_response(
                "用户信息未找到",
                "USER_NOT_FOUND",
                status_code=404
            )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

# ===== 项目相关接口 =====

@app.get("/api/v1/projects/stats", response_model=SuccessResponse)
async def get_project_statistics(
    search: str = Query("", description="搜索关键词"),
    archived: bool = Query(False, description="是否包含归档项目"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """获取项目统计信息"""
    try:
        client = get_client_from_cookies(cookies)
        stats = client.get_project_counts(search=search, archived=archived)
        
        return create_success_response({
            "total": stats.get('all', 0),
            "authorized": stats.get('authorized', 0),
            "search_keyword": search,
            "include_archived": archived
        }, "获取项目统计成功")
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目统计失败: {str(e)}")

@app.get("/api/v1/projects", response_model=SuccessResponse)
async def get_projects(
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query("", description="搜索关键词"),
    archived: bool = Query(False, description="是否包含归档项目"),
    all_pages: bool = Query(False, description="是否获取所有页"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """
    获取项目列表
    
    支持分页、搜索、归档项目过滤
    """
    try:
        client = get_client_from_cookies(cookies)
        
        if all_pages:
            # 获取所有项目
            projects = client.get_all_projects(archived=archived, search=search)
            total = len(projects)
            pagination = PaginationInfo(
                page=1,
                per_page=total,
                total=total,
                total_pages=1
            )
        else:
            # 获取指定页的项目
            projects = client.get_authorized_projects(
                page=page, 
                per_page=per_page, 
                archived=archived,
                search=search
            )
            # 获取总数用于分页计算
            stats = client.get_project_counts(search=search, archived=archived)
            total = stats.get('authorized', 0)
            total_pages = (total + per_page - 1) // per_page
            
            pagination = PaginationInfo(
                page=page,
                per_page=per_page,
                total=total,
                total_pages=total_pages
            )
        
        return create_success_response({
            "projects": projects or [],
            "pagination": pagination.dict(),
            "filters": {
                "search": search,
                "archived": archived,
                "all_pages": all_pages
            }
        }, f"获取项目列表成功，共{len(projects or [])}个项目")
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")

@app.get("/api/v1/projects/{project_id}", response_model=SuccessResponse)
async def get_project_overview(
    project_id: int = Path(..., description="项目ID"),
    revision: str = Query("refs/heads/master", description="分支引用"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """获取项目概览信息"""
    try:
        client = get_client_from_cookies(cookies)
        overview = client.get_project_overview(project_id, revision=revision)
        
        if overview:
            return create_success_response({
                "project_id": project_id,
                "revision": revision,
                "overview": overview
            }, "获取项目概览成功")
        else:
            return create_error_response(
                f"项目 {project_id} 概览未找到",
                "PROJECT_NOT_FOUND",
                status_code=404
            )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目概览失败: {str(e)}")

@app.get("/api/v1/projects/{project_id}/activities", response_model=SuccessResponse)
async def get_project_activities(
    project_id: int = Path(..., description="项目ID"),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """
    获取项目活动记录
    
    支持日期范围筛选和用户过滤
    """
    try:
        # 验证日期格式
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return create_error_response(
                    "开始日期格式错误，应为 YYYY-MM-DD",
                    "INVALID_DATE_FORMAT",
                    status_code=400
                )
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                return create_error_response(
                    "结束日期格式错误，应为 YYYY-MM-DD",
                    "INVALID_DATE_FORMAT",
                    status_code=400
                )
        
        client = get_client_from_cookies(cookies)
        result = client.get_project_activities(
            project_id=project_id,
            page=page,
            per_page=per_page,
            start_date=start_dt,
            end_date=end_dt,
            filter_by_user=True
        )
        
        return create_success_response({
            "project_id": project_id,
            "activities": result.get('activities', []),
            "overview": result.get('overview'),
            "pagination": result.get('pagination'),
            "filters": {
                "date_range": result.get('date_range')
            }
        }, f"获取项目活动成功，共{len(result.get('activities', []))}条记录")
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目活动失败: {str(e)}")

# 便捷的时间范围查询端点
@app.get("/api/v1/projects/{project_id}/activities/today", response_model=SuccessResponse)
async def get_today_activities(
    project_id: int = Path(..., description="项目ID"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """获取今日项目活动"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    return await get_project_activities(
        project_id=project_id,
        page=1,
        per_page=50,
        start_date=today,
        end_date=today,
        cookies=cookies
    )

@app.get("/api/v1/projects/{project_id}/activities/week", response_model=SuccessResponse)
async def get_week_activities(
    project_id: int = Path(..., description="项目ID"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """获取本周项目活动"""
    try:
        client = get_client_from_cookies(cookies)
        result = client.get_week_activities(
            project_id=project_id,
            filter_by_user=True
        )
        
        return create_success_response({
            "project_id": project_id,
            "activities": result.get('activities', []),
            "overview": result.get('overview'),
            "pagination": result.get('pagination'),
            "filters": {
                "date_range": result.get('date_range'),
                "period": "week"
            }
        }, f"获取本周活动成功，共{len(result.get('activities', []))}条记录")
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取本周活动失败: {str(e)}")

@app.get("/api/v1/projects/{project_id}/activities/month", response_model=SuccessResponse)
async def get_month_activities(
    project_id: int = Path(..., description="项目ID"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """获取本月项目活动"""
    try:
        client = get_client_from_cookies(cookies)
        today = datetime.now()
        start_dt = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 计算下个月第一天
        if today.month == 12:
            end_dt = today.replace(year=today.year+1, month=1, day=1)
        else:
            end_dt = today.replace(month=today.month+1, day=1)
        end_dt = end_dt - timedelta(seconds=1)  # 本月最后一秒
        
        result = client.get_project_activities(
            project_id=project_id,
            start_date=start_dt,
            end_date=end_dt,
            per_page=100,
            filter_by_user=True
        )
        
        return create_success_response({
            "project_id": project_id,
            "activities": result.get('activities', []),
            "overview": result.get('overview'),
            "pagination": result.get('pagination'),
            "filters": {
                "date_range": {
                    "start_date": start_dt.strftime('%Y-%m-%d'),
                    "end_date": end_dt.strftime('%Y-%m-%d')
                },
                "period": "month"
            }
        }, f"获取本月活动成功，共{len(result.get('activities', []))}条记录")
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"认证失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取本月活动失败: {str(e)}")

# ===== AI报告生成接口 =====

@app.post("/api/v1/projects/{project_id}/reports/ai-generate", response_model=SuccessResponse)
async def generate_ai_report(
    request_body: dict,
    project_id: int = Path(..., description="项目ID"),
    cookies: str = Header(..., alias="X-Codeup-Cookies")
):
    """
    AI生成项目报告
    
    支持多种报告类型：活动总结、代码审查、进度报告
    """
    try:
        # 直接使用Dify API，参考test_ai_report.py的成功实现
        import requests
        import os
        
        dify_url = os.getenv("DIFY_BASE_URL", "https://dify.hetunai.cn/v1") + "/chat-messages"
        api_key = os.getenv("DIFY_API_KEY")
        
        if not api_key:
            raise HTTPException(status_code=500, detail="DIFY_API_KEY环境变量未设置")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 直接使用前端传过来的数据构建prompt
        additional_context = request_body.get('additional_context', '')

        # 阻塞式请求数据
        test_data = {
            "inputs": {},
            "query": additional_context,
            "response_mode": "blocking",
            "conversation_id": "",
            "user": request_body.get('user', 'frontend_user'),
            "files": [],
            "auto_generate_name": False
        }
        
        logger.info(f"🤖 调用Dify API生成项目 {project_id} 的AI报告")
        
        response = requests.post(dify_url, json=test_data, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        return create_success_response({
            "project_id": project_id,
            "report_type": request_body.get('report_type', 'activity_summary'),
            "time_range": request_body.get('time_range', 'custom'), 
            "answer": result.get('answer', ''),
            "ai_response": result,
            "request_info": {
                "response_mode": "blocking",
                "user": request_body.get('user', 'frontend_user')
            }
        }, f"项目 {project_id} AI报告生成成功")
            
    except Exception as e:
        logger.error(f"AI报告生成失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI报告生成失败: {str(e)}")

@app.post("/api/v1/ai/chat", response_model=SuccessResponse)
async def ai_chat(chat_request: AIReportRequest):
    """
    通用AI聊天接口
    
    直接与Dify AI进行对话，不需要项目数据
    """
    try:
        # 构建Dify请求
        dify_request = DifyRequest(
            query=chat_request.additional_context or "请介绍一下自己",
            response_mode="blocking",
            user=chat_request.user,
            conversation_id="",
            files=None,
            auto_generate_name=True,
            workflow_id=None,
            trace_id=None
        )
        
        # 调用Dify API - 阻塞响应
        response_data = dify_client.create_blocking_response(dify_request)
        
        return create_success_response({
            "ai_response": response_data,
            "request_info": {
                "query": chat_request.additional_context,
                "user": chat_request.user
            }
        }, "AI对话成功")
            
    except Exception as e:
        logger.error(f"AI对话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI对话失败: {str(e)}")

@app.get("/api/v1/projects/{project_id}/reports/ai-generate-stream")
async def generate_ai_report_stream(
    project_id: int = Path(..., description="项目ID"),
    report_type: str = Query("activity_summary", description="报告类型"),
    time_range: str = Query("week", description="时间范围"),
    additional_context: str = Query("", description="额外上下文"),
    user: str = Query("frontend_user", description="用户标识"),
    cookies: Optional[str] = Query(None, alias="X-Codeup-Cookies", description="认证Cookies")
):
    """
    AI生成项目报告 - 流式响应
    """
    try:
        # 验证认证
        if not cookies:
            async def auth_error_stream():
                yield f"data: {json.dumps({'type': 'error', 'message': '缺少认证信息'}, ensure_ascii=False)}\n\n"
            
            return StreamingResponse(
                auth_error_stream(),
                media_type="text/event-stream"
            )
        
        client = get_client_from_cookies(cookies)
        
        # 构建请求对象
        request = AIReportRequest(
            project_id=project_id,
            report_type=report_type,
            time_range=time_range,
            additional_context=additional_context,
            response_mode="streaming",
            user=user,
            start_date=None,
            end_date=None,
            conversation_id=""
        )
        
        # 获取项目信息
        projects = client.get_authorized_projects(per_page=100)
        project_info = None
        for project in projects:
            if project.get('id') == project_id:
                project_info = project
                break
        
        if not project_info:
            async def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'message': f'项目 {project_id} 未找到或无权限访问'}, ensure_ascii=False)}\n\n"
            
            return StreamingResponse(
                error_stream(),
                media_type="text/event-stream"
            )
        
        project_name = project_info.get('name', f'Project-{project_id}')
        
        # 根据时间范围获取活动数据
        activities_data = []
        time_range_desc = ""
        
        if request.time_range == "today":
            today = datetime.now().strftime('%Y-%m-%d')
            start_dt = datetime.strptime(today, '%Y-%m-%d')
            end_dt = start_dt.replace(hour=23, minute=59, second=59)
            time_range_desc = "今日"
        elif request.time_range == "week":
            result = client.get_week_activities(project_id=project_id, filter_by_user=True)
            activities_data = result.get('activities', [])
            time_range_desc = "本周"
        elif request.time_range == "month":
            today = datetime.now()
            start_dt = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if today.month == 12:
                end_dt = today.replace(year=today.year+1, month=1, day=1)
            else:
                end_dt = today.replace(month=today.month+1, day=1)
            end_dt = end_dt - timedelta(seconds=1)
            time_range_desc = "本月"
        else:
            # 默认使用本周数据
            result = client.get_week_activities(project_id=project_id, filter_by_user=True)
            activities_data = result.get('activities', [])
            time_range_desc = "本周"
        
        # 如果不是从week活动获取的数据，需要手动获取
        if not activities_data and request.time_range != "week":
            result = client.get_project_activities(
                project_id=project_id,
                start_date=start_dt if 'start_dt' in locals() else None,
                end_date=end_dt if 'end_dt' in locals() else None,
                per_page=100,
                filter_by_user=True
            )
            activities_data = result.get('activities', [])
        
        # 生成AI报告提示词
        prompt = dify_client.generate_report_prompt(
            report_type=request.report_type,
            activities_data=activities_data,
            project_name=project_name,
            time_range_desc=time_range_desc,
            additional_context=request.additional_context
        )
        
        # 构建Dify请求
        dify_request = DifyRequest(
            query=prompt,
            inputs={
                "project_name": project_name,
                "project_id": str(project_id),
                "report_type": request.report_type,
                "time_range": time_range_desc,
                "activities_count": len(activities_data)
            },
            response_mode="streaming",
            user=request.user,
            conversation_id=None,
            files=None,
            auto_generate_name=True,
            workflow_id=None,
            trace_id=None
        )
        
        # 调用Dify API - 流式响应
        return StreamingResponse(
            dify_client.create_streaming_response(dify_request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except AuthenticationError as e:
        async def auth_error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': f'认证失败: {str(e)}'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            auth_error_stream(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"AI报告生成失败: {str(e)}", exc_info=True)
        error_msg = str(e)
        
        async def general_error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': f'服务器错误: {error_msg}'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            general_error_stream(),
            media_type="text/event-stream"
        )

@app.get("/api/v1/ai/chat-stream")
async def ai_chat_stream(
    query: str = Query(..., description="聊天内容"),
    user: str = Query("frontend_user", description="用户标识"),
    conversation_id: Optional[str] = Query(None, description="会话ID")
):
    """
    AI聊天 - 流式响应
    """
    try:
        # 构建Dify请求
        dify_request = DifyRequest(
            query=query,
            inputs={},
            response_mode="streaming",
            user=user,
            conversation_id=conversation_id or "",
            files=None,
            auto_generate_name=False,
            workflow_id=None,
            trace_id=None
        )
        
        # 调用Dify API - 流式响应
        return StreamingResponse(
            dify_client.create_streaming_response(dify_request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"AI聊天失败: {str(e)}", exc_info=True)
        
        async def chat_error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': f'服务器错误: {str(e)}'}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            chat_error_stream(),
            media_type="text/event-stream"
        )

@app.get("/api/v1/test-stream")
async def test_stream():
    """测试流式响应端点"""
    async def test_generator():
        for i in range(5):
            yield f"data: {json.dumps({'type': 'content', 'content': f'测试消息 {i+1}'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1)  # 模拟延迟
        yield f"data: {json.dumps({'type': 'done', 'message': '测试完成'}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        test_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    # 使用logger替代print
    logger.info("="*50)
    logger.info("🚀 Codeup API v1 Server 启动中...")
    logger.info(f"📝 API 文档: http://localhost:{port}/docs")
    logger.info(f"🔗 交互式文档: http://localhost:{port}/redoc")
    logger.info("✨ 新特性: 统一响应格式、完善错误处理、RESTful设计")
    logger.info(f"📊 日志级别: {log_level}")
    logger.info("="*50)
    
    # 设置uvicorn日志级别
    uvicorn_log_level = "warning" if log_level != "DEBUG" else "debug"
    
    uvicorn.run(
        "codeup_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=uvicorn_log_level,
        access_log=False  # 禁用访问日志，我们会在middleware中处理
    )