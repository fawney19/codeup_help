"""
工具函数模块
"""
from typing import Dict, Optional, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from models import SuccessResponse, ErrorResponse
from codeup_client import CodeupClient


# 存储客户端实例（生产环境中应该使用Redis等）
clients: Dict[str, CodeupClient] = {}


def parse_cookies(cookie_string: str) -> Dict[str, str]:
    """解析cookie字符串为字典"""
    cookies = {}
    for item in cookie_string.split(';'):
        if '=' in item:
            key, value = item.strip().split('=', 1)
            cookies[key] = value
    return cookies


def extract_login_ticket_from_cookies(cookie_string: str) -> Optional[str]:
    """从cookie字符串中提取login_aliyunid_ticket"""
    cookies = parse_cookies(cookie_string)
    return cookies.get('login_aliyunid_ticket')


def get_client(login_ticket: str) -> CodeupClient:
    """获取或创建客户端实例"""
    if login_ticket not in clients:
        clients[login_ticket] = CodeupClient(login_ticket)
    return clients[login_ticket]


def get_client_from_cookies(cookies: str) -> CodeupClient:
    """从cookies中提取login_ticket并获取客户端实例"""
    login_ticket = extract_login_ticket_from_cookies(cookies)
    if not login_ticket:
        raise HTTPException(status_code=401, detail="无效的cookies或缺少认证信息")
    return get_client(login_ticket)


def create_success_response(data: Any = None, message: str = "操作成功") -> SuccessResponse:
    """创建成功响应"""
    return SuccessResponse(data=data, message=message)


def create_error_response(message: str, error_code: str = None, 
                         details: Dict = None, status_code: int = 400) -> JSONResponse:
    """创建错误响应"""
    error_response = ErrorResponse(
        message=message,
        error_code=error_code,
        details=details
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )