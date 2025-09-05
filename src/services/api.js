import axios from 'axios'
import Cookies from 'js-cookie'

// 动态获取API地址
const getAPIBaseURL = () => {
  // Docker部署环境：通过nginx反向代理，直接使用相对路径
  if (window.location.port === '5111' || process.env.NODE_ENV === 'production') {
    return '' // 使用相对路径，通过nginx代理到后端
  }
  // 如果是通过内网IP访问前端，后端也使用内网IP
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return `http://${window.location.hostname}:8000`
  }
  // 本地开发环境
  return 'http://localhost:8000'
}

const API_BASE_URL = getAPIBaseURL()

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器 - 添加 cookies
api.interceptors.request.use(
  (config) => {
    const cookies = Cookies.get('codeup_cookies')
    if (cookies) {
      config.headers['X-Codeup-Cookies'] = cookies
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除无效的 cookies
      Cookies.remove('codeup_cookies')
      
      // 触发认证状态清理
      try {
        // 动态导入避免循环依赖
        import('@/stores/auth').then(({ useAuthStore }) => {
          const authStore = useAuthStore()
          authStore.logout() // 这会清理用户状态和项目缓存
        })
      } catch (e) {
        console.warn('Failed to clear auth state:', e)
      }
      
      // 重定向到登录页面
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API方法
export const authApi = {
  // 使用Cookies登录
  loginWithCookies: (cookies) => api.post('/api/v1/auth/login-with-cookies', { cookies }),
  
  // 获取当前用户信息
  getCurrentUser: () => api.get('/api/v1/users/me')
}

export const projectsApi = {
  // 获取项目统计
  getStats: (params = {}) => api.get('/api/v1/projects/stats', { params }),
  
  // 获取项目列表
  getProjects: (params = {}) => api.get('/api/v1/projects', { params }),
  
  // 获取项目概览
  getProjectOverview: (projectId, params = {}) => 
    api.get(`/api/v1/projects/${projectId}`, { params }),
  
  // 获取项目活动记录
  getProjectActivities: (projectId, params = {}) => 
    api.get(`/api/v1/projects/${projectId}/activities`, { params }),
  
  // 获取今日活动
  getTodayActivities: (projectId, params = {}) => 
    api.get(`/api/v1/projects/${projectId}/activities/today`, { params }),
  
  // 获取本周活动  
  getWeekActivities: (projectId, params = {}) => 
    api.get(`/api/v1/projects/${projectId}/activities/week`, { params }),
  
  // 获取本月活动
  getMonthActivities: (projectId, params = {}) => 
    api.get(`/api/v1/projects/${projectId}/activities/month`, { params }),
  
  // AI报告生成 - 流式响应
  generateAIReport: (projectId, data, onProgress) => {
    return new Promise((resolve, reject) => {
      const params = new URLSearchParams({
        report_type: data.report_type || 'activity_summary',
        time_range: data.time_range || 'week',
        additional_context: data.additional_context || '',
        user: data.user || 'frontend_user'
      });
      
      const cookies = Cookies.get('codeup_cookies');
      const baseUrl = API_BASE_URL || window.location.origin; // 生产环境使用当前域名
      const url = `${baseUrl}/api/v1/projects/${projectId}/reports/ai-generate-stream?${params}&X-Codeup-Cookies=${encodeURIComponent(cookies || '')}`;
      
      const eventSource = new EventSource(url);
      
      let fullResponse = '';
      
      eventSource.onmessage = function(event) {
        try {
          const eventData = JSON.parse(event.data);
          if (eventData.type === 'content') {
            fullResponse += eventData.content;
            // 通过回调函数实时返回内容
            if (onProgress) {
              onProgress(fullResponse);
            }
          } else if (eventData.type === 'done') {
            eventSource.close();
            resolve({ answer: fullResponse, status: 'completed' });
          } else if (eventData.type === 'error') {
            console.error('AI报告生成错误:', eventData.message);
            eventSource.close();
            reject(new Error(eventData.message || '生成报告时发生错误'));
          }
        } catch (e) {
          console.error('解析SSE数据失败:', e);
        }
      };
      
      eventSource.onerror = function(error) {
        eventSource.close();
        reject(new Error('连接AI服务失败'));
      };
    });
  },
  
  // AI报告生成 - 阻塞式响应
  generateAIReportBlocking: (projectId, data) => 
    api.post(`/api/v1/projects/${projectId}/reports/ai-generate`, {
      report_type: data.report_type || 'activity_summary',
      time_range: data.time_range || 'week',
      additional_context: data.additional_context || '',
      response_mode: 'blocking',
      user: data.user || 'frontend_user'
    })
}

// AI聊天API
export const aiApi = {
  // AI聊天 - 流式响应
  chatStream: (query, onProgress) => {
    return new Promise((resolve, reject) => {
      const baseUrl = API_BASE_URL || window.location.origin; // 生产环境使用当前域名
      const eventSource = new EventSource(`${baseUrl}/api/v1/ai/chat-stream?${new URLSearchParams({
        query: query,
        user: 'frontend_user'
      })}`);
      
      let fullResponse = '';
      
      eventSource.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'content') {
            fullResponse += data.content;
            if (onProgress) {
              onProgress(fullResponse);
            }
          } else if (data.type === 'done') {
            eventSource.close();
            resolve({ answer: fullResponse, status: 'completed' });
          } else if (data.type === 'error') {
            eventSource.close();
            reject(new Error(data.message || '聊天时发生错误'));
          }
        } catch (e) {
          console.error('解析SSE数据失败:', e);
        }
      };
      
      eventSource.onerror = function(error) {
        eventSource.close();
        reject(new Error('连接AI服务失败'));
      };
    });
  },
  
  // AI聊天 - 阻塞式响应
  chatBlocking: (query) => 
    api.post('/api/v1/ai/chat', {
      query: query,
      response_mode: 'blocking',
      user: 'frontend_user'
    })
}

export default api