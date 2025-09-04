import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import re
import logging


class AuthenticationError(Exception):
    """认证失败异常"""
    pass


@dataclass
class UserInfo:
    """用户信息数据类"""
    id: str
    name: str
    email: str
    avatar_url: str


@dataclass
class ProjectActivity:
    """项目活动数据类"""
    action: int
    created_at: datetime
    user_name: str
    project_name: str
    branch: str
    commits: List[Dict[str, Any]]


class CodeupClient:
    """阿里云 Codeup 代码仓库客户端"""
    
    BASE_URL = "https://codeup.aliyun.com/api/v3"
    DEVOPS_URL = "https://devops.aliyun.com/uiless/api/sdk"
    
    @staticmethod
    def extract_login_ticket(cookies_string: str) -> Optional[str]:
        """
        从完整的cookies字符串中提取login_aliyunid_ticket值
        
        Args:
            cookies_string: 完整的cookies字符串，如浏览器复制的格式
            
        Returns:
            提取的login_ticket值，如果未找到则返回None
            
        Example:
            cookies = "bs_n_lang=zh_CN; login_aliyunid_ticket=3RctYK12wch...; other=value"
            ticket = CodeupClient.extract_login_ticket(cookies)
        """
        if not cookies_string:
            return None
            
        # 使用正则表达式匹配 login_aliyunid_ticket 的值
        pattern = r'login_aliyunid_ticket=([^;]+)'
        match = re.search(pattern, cookies_string)
        
        if match:
            ticket = match.group(1).strip()
            print(f"成功提取login_ticket: {ticket[:20]}...")
            return ticket
        else:
            print("在cookies字符串中未找到login_aliyunid_ticket")
            return None
    
    def __init__(self, login_ticket: str):
        """
        初始化 Codeup 客户端
        
        Args:
            login_ticket: 登录凭证
        """
        self.cookies = {
            'login_aliyunid_ticket': login_ticket
        }
        self._current_user: Optional[UserInfo] = None
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        发送 HTTP 请求的通用方法
        
        Args:
            url: 请求 URL
            params: 请求参数
            
        Returns:
            响应数据或 None
            
        Raises:
            AuthenticationError: 当返回 302 状态码时（通常表示认证失败）
        """
        if params is None:
            params = {}
        params['_input_charset'] = 'utf-8'
        
        with httpx.Client() as client:
            try:
                response = client.get(url, params=params, cookies=self.cookies)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 302:
                    print(f"认证失败: cookies已过期 (状态码: 302)")
                    raise AuthenticationError("登录凭证已过期，请重新登录")
                else:
                    print(f"请求失败: {response.status_code}")
                    return None
            except AuthenticationError:
                raise
            except Exception as e:
                print(f"请求异常: {e}")
                return None
    
    def get_user_info(self) -> Optional[UserInfo]:
        """
        获取当前用户信息
        
        Returns:
            用户信息对象或 None
        """
        if self._current_user:
            return self._current_user
            
        url = f"{self.DEVOPS_URL}/users/me"
        data = self._make_request(url)
        
        if data and data.get('success') and data.get('result'):
            user_data = data['result'].get('user', {})
            self._current_user = UserInfo(
                id=user_data.get('id', ''),
                name=user_data.get('name', ''),
                email=user_data.get('email', ''),
                avatar_url=user_data.get('avatarUrl', '')
            )
            return self._current_user
        
        print("获取用户信息失败")
        return None
    
    def get_project_counts(self, search: str = "", archived: bool = False) -> Dict[str, int]:
        """
        获取项目统计信息
        
        Args:
            search: 搜索关键词
            archived: 是否包含已归档项目
            
        Returns:
            包含 'all' 和 'authorized' 的字典
        """
        url = f"{self.BASE_URL}/projects/counts"
        params = {
            'search': search,
            'contains_sub_projects': 'true',
            'archived': str(archived).lower()
        }
        
        data = self._make_request(url, params)
        if data:
            return data
        return {'all': 0, 'authorized': 0}
    
    def get_authorized_projects(self, page: int = 1, per_page: int = 20, 
                               archived: bool = False, search: str = '') -> Optional[List[Dict]]:
        """
        获取授权的项目列表（支持分页和搜索）
        
        Args:
            page: 页码
            per_page: 每页项目数
            archived: 是否包含已归档项目
            search: 搜索关键词
            
        Returns:
            项目列表或 None
        """
        url = f"{self.BASE_URL}/projects/authorized/list"
        params = {
            'page': str(page),
            'per_page': str(per_page),
            'order_by': 'last_activity_at',
            'contains_sub_projects': 'true',
            'archived': str(archived).lower()
        }
        
        if search.strip():
            params['search'] = search.strip()
        
        data = self._make_request(url, params)
        return data
    
    def get_all_projects(self, archived: bool = False, search: str = '') -> List[Dict]:
        """
        获取所有授权项目（自动分页和搜索）
        
        Args:
            archived: 是否包含已归档项目
            search: 搜索关键词
            
        Returns:
            所有项目列表
        """
        counts = self.get_project_counts(archived=archived, search=search)
        authorized_count = counts.get('authorized', 0)
        
        if authorized_count == 0:
            if search.strip():
                print(f"没有找到匹配 '{search}' 的项目")
            else:
                print("没有找到您有权限访问的项目")
            return []
        
        per_page = 20
        total_pages = (authorized_count + per_page - 1) // per_page
        
        if search.strip():
            print(f"搜索 '{search}' 找到 {authorized_count} 个项目，需要获取 {total_pages} 页")
        else:
            print(f"您有权限访问 {authorized_count} 个项目，需要获取 {total_pages} 页")
        print("-" * 80)
        
        all_projects = []
        for page in range(1, total_pages + 1):
            print(f"正在获取第 {page}/{total_pages} 页...")
            projects = self.get_authorized_projects(page=page, per_page=per_page, archived=archived, search=search)
            
            if projects:
                all_projects.extend(projects)
            else:
                print(f"第 {page} 页获取失败")
                break
        
        print(f"\n实际获取到 {len(all_projects)} 个项目")
        return all_projects
    
    def get_project_overview(self, project_id: int, revision: str = "refs/heads/master") -> Optional[Dict]:
        """
        获取项目概览信息
        
        Args:
            project_id: 项目 ID
            revision: 分支引用
            
        Returns:
            项目概览信息或 None
        """
        url = f"{self.BASE_URL}/projects/{project_id}/overview"
        params = {'revision': revision}
        
        return self._make_request(url, params)
    
    def get_project_activities(self, project_id: int, page: int = 1, per_page: int = 10,
                               start_date: Optional[datetime] = None, 
                               end_date: Optional[datetime] = None,
                               filter_by_user: bool = False) -> Dict[str, Any]:
        """
        获取项目活动（支持日期范围筛选和用户过滤）
        
        Args:
            project_id: 项目 ID
            page: 页码
            per_page: 每页条数
            start_date: 开始日期
            end_date: 结束日期
            filter_by_user: 是否只显示当前用户的活动
            
        Returns:
            包含活动记录、概览信息和分页信息的字典
        """
        # 处理日期参数
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
        
        # 自动补全日期范围
        if start_date and not end_date:
            end_date = datetime.now()
        if end_date and not start_date:
            start_date = end_date - timedelta(days=30)
        
        # 获取项目概览
        overview_info = self.get_project_overview(project_id)
        total_commits = overview_info.get('commit_count', 0) if overview_info else 0
        total_pages = (total_commits + per_page - 1) // per_page if total_commits > 0 else 0
        
        # 获取当前用户信息（如果需要过滤）
        current_user_name = None
        if filter_by_user:
            user_info = self.get_user_info()
            if user_info:
                current_user_name = user_info.name
                # 只在调试模式下输出
                self.logger.debug(f"当前用户: {current_user_name}")
        
        # 获取活动记录
        all_activities = self._fetch_activities(
            project_id, page, per_page, start_date, end_date, current_user_name
        )
        
        # 显示结果
        if all_activities:
            self._display_activities_summary(
                project_id, all_activities, start_date, end_date, current_user_name
            )
            self._parse_and_display_activities(all_activities)
        
        # 过滤Claude Code相关内容
        cleaned_activities = self._filter_claude_code_content(all_activities)
        
        # 返回结果
        filtered_count = len(cleaned_activities)
        return {
            'activities': cleaned_activities,
            'overview': overview_info,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages if not (start_date and end_date) else (filtered_count + per_page - 1) // per_page,
                'per_page': per_page,
                'total_commits': total_commits,
                'filtered_count': filtered_count
            },
            'date_range': {
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
            }
        }
    
    def _fetch_activities(self, project_id: int, page: int, per_page: int,
                         start_date: Optional[datetime], end_date: Optional[datetime],
                         current_user_name: Optional[str]) -> List[Dict]:
        """
        获取活动记录的内部方法
        """
        all_activities = []
        current_page = page
        filtered_count = 0
        
        while True:
            url = f"{self.BASE_URL}/projects/{project_id}/activities"
            params = {
                'page': str(current_page),
                'per_page': str(per_page if not (start_date and end_date) else 100)
            }
            
            data = self._make_request(url, params)
            if not data:
                break
            
            # 应用筛选条件
            if start_date and end_date:
                for activity in data:
                    # 用户过滤
                    if current_user_name:
                        user = activity.get('user', {})
                        if user.get('name') != current_user_name:
                            continue
                    
                    # 日期过滤
                    created_at_str = activity.get('createdAt', '')
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace('+08:00', ''))
                        if start_date <= created_at <= end_date:
                            all_activities.append(activity)
                            filtered_count += 1
                        elif created_at < start_date:
                            break
                
                # 检查是否需要继续获取下一页
                if data and filtered_count < page * per_page:
                    last_activity_time_str = data[-1].get('createdAt', '')
                    if last_activity_time_str:
                        last_activity_time = datetime.fromisoformat(last_activity_time_str.replace('+08:00', ''))
                        if last_activity_time >= start_date:
                            current_page += 1
                            continue
                
                # 只保留当前页需要的记录
                if filtered_count >= page * per_page:
                    start_idx = (page - 1) * per_page
                    end_idx = page * per_page
                    all_activities = all_activities[start_idx:end_idx]
                break
            else:
                # 没有日期筛选，但可能有用户筛选
                if current_user_name:
                    for activity in data:
                        user = activity.get('user', {})
                        if user.get('name') == current_user_name:
                            all_activities.append(activity)
                else:
                    all_activities = data
                break
        
        return all_activities
    
    def _display_activities_summary(self, project_id: int, activities: List[Dict],
                                   start_date: Optional[datetime], end_date: Optional[datetime],
                                   current_user_name: Optional[str]):
        """显示活动摘要信息"""
        # 仅在调试模式下显示详细信息
        self.logger.debug(f"项目 {project_id} - 共 {len(activities)} 条活动记录")
        if start_date and end_date:
            self.logger.debug(f"日期范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    
    def _parse_and_display_activities(self, activities: List[Dict]):
        """解析并显示活动数据（按日期分组）"""
        self.logger.info(f"共 {len(activities)} 条活动记录")
        
        # 按日期分组活动
        activities_by_date = {}
        for activity in activities:
            created_at_str = activity.get('createdAt', '')
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str.replace('+08:00', ''))
                date_key = created_at.strftime('%Y-%m-%d')
                weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][created_at.weekday()]
                
                if date_key not in activities_by_date:
                    activities_by_date[date_key] = {'weekday': weekday, 'activities': []}
                activities_by_date[date_key]['activities'].append(activity)
        
        # 按日期排序并显示
        for date in sorted(activities_by_date.keys(), reverse=True):
            date_info = activities_by_date[date]
            self._display_date_activities(date, date_info)
    
    def _display_date_activities(self, date: str, date_info: Dict):
        """显示某一天的活动"""
        date_activities = date_info['activities']
        weekday = date_info['weekday']
        
        # 简化输出
        self.logger.debug(f"{date} ({weekday}) - {len(date_activities)} 条记录")
        
        for activity in date_activities:
            self._display_single_activity(activity)
    
    def _display_single_activity(self, activity: Dict):
        """显示单个活动详情"""
        # 活动类型
        action_type = "Push" if activity.get('action') == 5 else f"Action {activity.get('action')}"
        
        # 时间
        created_at_str = activity.get('createdAt', '')
        if created_at_str:
            created_at = datetime.fromisoformat(created_at_str.replace('+08:00', ''))
            time_str = created_at.strftime('%H:%M:%S')
        else:
            time_str = 'N/A'
        
        # 用户和项目信息
        user_name = activity.get('user', {}).get('name', 'N/A')
        project_name = activity.get('project', {}).get('name', 'N/A')
        
        # 简化单行输出
        self.logger.debug(f"  {time_str} - {action_type} | {user_name} | {project_name}")
        
        # 解析提交信息
        if 'dataMap' in activity:
            data_map = activity['dataMap']
            ref = data_map.get(':ref', '').replace('refs/heads/', '')
            commits = data_map.get(':commits', [])
            
            if ref:
                self.logger.debug(f"     分支: {ref}")
            
            if commits:
                self.logger.debug(f"     {len(commits)} 个提交")
                # 仅在DEBUG模式下显示提交详情
                for i, commit in enumerate(commits):
                    commit_id = commit.get(':id', 'N/A')[:8]
                    message = commit.get(':message', '')
                    lines = message.split('\n') if message else ['N/A']
                    author_name = commit.get(':author', {}).get(':name', 'N/A')
                    # 只输出第一行消息的前50个字符
                    msg_summary = lines[0][:50] + '...' if len(lines[0]) > 50 else lines[0]
                    self.logger.debug(f"       [{i+1}] {commit_id} - {author_name}: {msg_summary}")
        
        # 移除空行输出
    
    def get_week_activities(self, project_id: int, filter_by_user: bool = False) -> Dict[str, Any]:
        """
        获取本周的项目活动
        
        Args:
            project_id: 项目 ID
            filter_by_user: 是否只显示当前用户的活动
            
        Returns:
            活动数据
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        sunday = monday + timedelta(days=6)
        sunday = sunday.replace(hour=23, minute=59, second=59)
        
        # 仅在调试时输出
        self.logger.info(f"获取本周的项目活动 ({monday.strftime('%Y-%m-%d')} 至 {sunday.strftime('%Y-%m-%d')})")
        
        return self.get_project_activities(
            project_id,
            start_date=monday,
            end_date=sunday,
            per_page=50,
            filter_by_user=filter_by_user
        )
    
    def _filter_claude_code_content(self, activities):
        """简单的Claude Code内容过滤方法"""
        if not activities:
            return activities
        
        try:
            filtered_activities = []
            
            for activity in activities:
                try:
                    # 创建活动副本以避免修改原始数据
                    cleaned_activity = activity.copy()
                    
                    # 检查并清理dataMap中的commits
                    if isinstance(cleaned_activity.get('dataMap'), dict):
                        data_map = cleaned_activity['dataMap'].copy()
                        if ':commits' in data_map and isinstance(data_map[':commits'], list):
                            cleaned_commits = []
                            for commit in data_map[':commits']:
                                if isinstance(commit, dict) and ':message' in commit:
                                    message = commit[':message']
                                    
                                    # 更简单直接的过滤方法
                                    cleaned_message = self._clean_commit_message(message)
                                    
                                    cleaned_commit = commit.copy()
                                    cleaned_commit[':message'] = cleaned_message
                                    cleaned_commits.append(cleaned_commit)
                                else:
                                    cleaned_commits.append(commit)
                            
                            data_map[':commits'] = cleaned_commits
                            cleaned_activity['dataMap'] = data_map
                    
                    filtered_activities.append(cleaned_activity)
                    
                except Exception as e:
                    # 如果单个活动处理失败，使用原始活动
                    filtered_activities.append(activity)
                    
            return filtered_activities
            
        except Exception as e:
            # 如果整个过滤过程失败，返回原始数据
            return activities
    
    def _clean_commit_message(self, message):
        """清理单个提交消息中的Claude Code内容"""
        if not message:
            return message
        
        try:
            # 按行分割消息
            lines = message.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # 跳过包含Claude Code标识的行
                if "🤖 Generated with [Claude Code]" in line:
                    continue
                if "Co-Authored-By: Claude <noreply@anthropic.com>" in line:
                    continue
                # 添加非Claude Code相关的行
                cleaned_lines.append(line)
            
            # 重新组合，清理末尾的空行
            result = '\n'.join(cleaned_lines).rstrip()
            return result
            
        except Exception as e:
            # 如果清理失败，返回原始消息
            return message

def main():
    """主函数 - 演示用法"""
    # 演示从完整cookies字符串中提取login_ticket
    full_cookies = """bs_n_lang=zh_CN; cna=Ob23HYAavGMCAXVEujqQyIKJ; account_info_switch=close; cnaui=237175890734336340; aui=237175890734336340; yunpk=1306757022114677; aliyun_site=CN; aliyun_country=CN; partitioned_cookie_flag=doubleRemove; aliyun_lang=zh; login_aliyunid_pk=1306757022114677; login_current_pk=237175890734336340; login_aliyunid_csrf=_csrf_tk_1909856806744608; login_aliyunid="yuanhonghu @ hetun"; login_aliyunid_ticket=3RctYK12wchSG5MTNmpZhQ3r.1118LAazv7na8qekPAeBrv2iiHacFRbKGgXDXzANt7QN6N8pyY84EQDTNZGaDVLhBFLZ5XgoeFDGREq9PrCu4CnqBm6JJZj9iCfseHqV8WEH64gGQWxXmNHpFvR3PwhTMxpnuaEYgmafon78ZfBMyaoTrJsyAFkQtW9k4tDytrFJcughVYz.2mWNaj2meJqzns1bZmuQNPXNXDq2nB1m7yRG3c87UXgsLJ1T62nu5Qzr84prtBFd3y; login_aliyunid_sc=3R5H3e3HY2c8q5WiJ2aXp2hw.1113gzDJHKLg4SACK7NautNMZowHVRz3XRAUnb1wndHWix18xziqGkgg8BaUVTXmE3fsU9.1QDta7oaFub1t2erHSp7rq27edmBikxpDTtRwom5xvgYbcHjCG6obhEVwG9DubUu3; LOGIN_ALIYUN_PK_FOR_TB=237175890734336340"""
    
    print("=== 从完整cookies字符串中提取login_ticket ===")
    login_ticket = CodeupClient.extract_login_ticket(full_cookies)
    
    if not login_ticket:
        print("无法提取login_ticket，使用默认值")
        login_ticket = '3RctYK12wchSG5MTNmpZhQ3r.1118LAazv7na8qekPAeBrv2iiHacFRbKGgXDXzANt7QN6N8pyY84EQDTNZGaDVLhBFLZ5XgoeFDGREq9PrCu4CnqBm6JJZj9iCfseHqV8WEH64gGQWxXmNHpFvR3PwhTMxpnuaEYgmafon78ZfBMyaoTrJsyAFkQtW9k4tDytrFJcughVYz.2mWNaj2meJqzns1bZmuQNPXNXDq2nB1m7yRG3c87UXgsLJ1T62nu5Qzr84prtBFd3y'
    
    # 初始化客户端
    client = CodeupClient(login_ticket)
    
    # 获取用户信息
    print("\n获取系统事件（用户信息）...")
    print("-" * 50)
    user_info = client.get_user_info()
    if user_info:
        self.logger.debug(f"当前用户: {user_info.name}")
        print(f"邮箱: {user_info.email}")
    
    # 项目 ID
    project_id = 5318863  # snookerAlgo 项目的 ID
    
    # 获取本周所有的项目活动
    print("\n" + "=" * 50)
    print("获取本周所有项目活动...")
    print("=" * 50)
    all_result = client.get_week_activities(project_id, filter_by_user=False)
    
    # 获取本周只属于当前用户的项目活动
    print("\n" + "=" * 50)
    print("获取本周当前用户的项目活动...")
    print("=" * 50)
    my_result = client.get_week_activities(project_id, filter_by_user=True)
    
    # 输出统计对比
    if all_result and my_result:
        all_activities = all_result.get('activities', [])
        my_activities = my_result.get('activities', [])
        print(f"\n" + "=" * 50)
        print("📊 统计对比")
        print("=" * 50)
        print(f"本周项目总活动数: {len(all_activities)} 条")
        print(f"本周我的活动数: {len(my_activities)} 条")
        if all_activities:
            print(f"我的活动占比: {len(my_activities)/len(all_activities)*100:.1f}%")
        else:
            print("我的活动占比: 0%")
        
        if all_result.get('date_range'):
            date_range = all_result['date_range']
            print(f"日期范围: {date_range['start_date']} 至 {date_range['end_date']}")
    
    def _clean_claude_code_content(self, activities: List[Dict]) -> List[Dict]:
        """
        清理活动数据中的Claude Code相关内容
        
        Args:
            activities: 原始活动数据列表
            
        Returns:
            清理后的活动数据列表
        """
        import copy
        
        def clean_commit_message(message: str) -> str:
            """清理提交消息中的Claude Code相关内容"""
            if not message or not isinstance(message, str):
                return message
                
            # 使用简单的字符串替换，避免复杂的正则表达式
            cleaned_message = message
            
            # 移除Claude Code相关的标记
            claude_markers = [
                "🤖 Generated with [Claude Code](https://claude.ai/code)",
                "Co-Authored-By: Claude <noreply@anthropic.com>"
            ]
            
            for marker in claude_markers:
                cleaned_message = cleaned_message.replace(marker, "")
            
            # 清理多余的空行和空白字符
            lines = cleaned_message.split('\n')
            cleaned_lines = []
            
            for line in lines:
                stripped_line = line.strip()
                if stripped_line:  # 保留非空行
                    cleaned_lines.append(line)
            
            # 重新组合，去掉末尾多余的空行
            result = '\n'.join(cleaned_lines).strip()
            return result
        
        try:
            # 深拷贝活动列表以避免修改原数据
            cleaned_activities = copy.deepcopy(activities)
            
            for activity in cleaned_activities:
                try:
                    # 清理dataMap中的提交消息
                    if 'dataMap' in activity and ':commits' in activity['dataMap']:
                        commits = activity['dataMap'][':commits']
                        if isinstance(commits, list):
                            for commit in commits:
                                if isinstance(commit, dict) and ':message' in commit:
                                    commit[':message'] = clean_commit_message(commit[':message'])
                    
                    # 也清理data字段中的内容（如果存在）
                    if 'data' in activity and isinstance(activity['data'], str):
                        activity['data'] = clean_commit_message(activity['data'])
                        
                except Exception as e:
                    print(f"Error cleaning activity: {e}")
                    continue
            
            return cleaned_activities
            
        except Exception as e:
            print(f"Error in _clean_claude_code_content: {e}")
            # 如果清理失败，返回原始数据
            return activities


if __name__ == "__main__":
    main()