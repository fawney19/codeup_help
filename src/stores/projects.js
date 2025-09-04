import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectsApi } from '@/services/api'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([])
  const currentProject = ref(null)
  const activities = ref([])
  const stats = ref({ total: 0, authorized: 0 })
  const loading = ref(false)
  const pagination = ref({ page: 1, per_page: 20, total: 0, total_pages: 0 })
  
  // 缓存相关状态 - 仅在同一会话中有效，页面刷新时自动清空
  const lastSearchQuery = ref('')
  const lastPage = ref(1)
  const isStatsCached = ref(false)
  const isProjectsCached = ref(false)

  // 排序后的项目列表 - 按最后活动时间排序
  const sortedProjects = computed(() => {
    if (!projects.value || !Array.isArray(projects.value)) {
      return []
    }
    return [...projects.value].sort((a, b) => {
      // 假设项目有 last_activity_at 字段
      const aTime = new Date(a.last_activity_at || 0)
      const bTime = new Date(b.last_activity_at || 0)
      return bTime - aTime
    })
  })

  // 根据搜索关键词过滤的项目列表
  const getFilteredProjects = (searchQuery = '') => {
    const sorted = sortedProjects.value
    if (!searchQuery.trim()) {
      return sorted
    }
    
    return sorted.filter(project => {
      const name = (project.name || project.path || '').toLowerCase()
      const description = (project.description || '').toLowerCase()
      const query = searchQuery.toLowerCase()
      
      return name.includes(query) || description.includes(query)
    })
  }

  // 检查统计缓存是否有效
  const isStatsCacheValid = (searchQuery = '') => {
    if (!isStatsCached.value) return false
    return lastSearchQuery.value === searchQuery
  }

  // 检查项目列表缓存是否有效
  const isProjectsCacheValid = (searchQuery = '', page = 1) => {
    if (!isProjectsCached.value) return false
    return lastSearchQuery.value === searchQuery && lastPage.value === page
  }

  // 获取项目统计
  const fetchStats = async (params = {}, forceRefresh = false) => {
    const searchQuery = params.search || ''
    
    // 检查缓存是否有效，除非强制刷新
    if (!forceRefresh && isStatsCacheValid(searchQuery)) {
      return { success: true, data: stats.value }
    }
    
    try {
      loading.value = true
      const response = await projectsApi.getStats(params)
      if (response.status === 'success') {
        stats.value = response.data
        // 更新统计缓存状态和搜索查询
        isStatsCached.value = true
        lastSearchQuery.value = searchQuery
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch stats failed:', error)
      return { success: false, error: error.response?.data?.message || '获取统计失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取项目列表
  const fetchProjects = async (params = {}, forceRefresh = false) => {
    const searchQuery = params.search || ''
    const page = params.page || 1
    
    // 检查缓存是否有效，除非强制刷新
    if (!forceRefresh && isProjectsCacheValid(searchQuery, page)) {
      return { success: true, data: { projects: projects.value, pagination: pagination.value } }
    }
    
    try {
      loading.value = true
      const response = await projectsApi.getProjects(params)
      if (response.status === 'success') {
        projects.value = response.data.projects || []
        pagination.value = response.data.pagination || pagination.value
        // 更新项目缓存状态和搜索查询
        isProjectsCached.value = true
        lastSearchQuery.value = searchQuery
        lastPage.value = page
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch projects failed:', error)
      return { success: false, error: error.response?.data?.message || '获取项目列表失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取项目详情
  const fetchProjectOverview = async (projectId, params = {}) => {
    try {
      loading.value = true
      const response = await projectsApi.getProjectOverview(projectId, params)
      if (response.status === 'success') {
        currentProject.value = response.data
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch project overview failed:', error)
      return { success: false, error: error.response?.data?.message || '获取项目详情失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取项目活动
  const fetchActivities = async (projectId, params = {}) => {
    try {
      loading.value = true
      const response = await projectsApi.getProjectActivities(projectId, params)
      if (response.status === 'success') {
        const transformedActivities = (response.data.activities || []).map(transformActivity)
        activities.value = transformedActivities
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch activities failed:', error)
      return { success: false, error: error.response?.data?.message || '获取活动记录失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取今日活动
  const fetchTodayActivities = async (projectId, params = {}) => {
    try {
      loading.value = true
      const response = await projectsApi.getTodayActivities(projectId, params)
      if (response.status === 'success') {
        const transformedActivities = (response.data.activities || []).map(transformActivity)
        activities.value = transformedActivities
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch today activities failed:', error)
      return { success: false, error: error.response?.data?.message || '获取今日活动失败' }
    } finally {
      loading.value = false
    }
  }

  // 转换活动数据格式以匹配前端期望的字段名
  const transformActivity = (activity) => {
    // 解析action类型
    const getActionText = (actionCode) => {
      switch (actionCode) {
        case 5: return 'Push'
        case 1: return 'Created'
        case 2: return 'Updated'
        default: return 'Activity'
      }
    }

    // 从dataMap中提取提交信息
    const extractCommits = (dataMap) => {
      if (!dataMap || !dataMap[':commits']) return []
      
      return dataMap[':commits'].map(commit => ({
        id: commit[':id'],
        message: commit[':message'],
        author: commit[':author']
      }))
    }

    // 提取分支名
    const extractRefName = (dataMap) => {
      if (!dataMap || !dataMap[':ref']) return 'master'
      return dataMap[':ref'].replace('refs/heads/', '')
    }

    return {
      ...activity,
      // 映射时间字段 - 从 createdAt 到 created_at
      created_at: activity.createdAt,
      // 映射action字段 - 从数值转为文本
      action: getActionText(activity.action),
      // 映射分支名
      ref_name: extractRefName(activity.dataMap),
      target_title: extractRefName(activity.dataMap),
      // 映射提交信息
      commits: extractCommits(activity.dataMap),
      // 映射作者名
      author_name: activity.user?.name || activity.user?.memberName
    }
  }

  // 获取本周活动
  const fetchWeekActivities = async (projectId, params = {}) => {
    try {
      loading.value = true
      const response = await projectsApi.getWeekActivities(projectId, params)
      if (response.status === 'success') {
        // 转换数据格式以匹配前端期望
        const transformedActivities = (response.data.activities || []).map(transformActivity)
        
        activities.value = transformedActivities
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch week activities failed:', error)
      return { success: false, error: error.response?.data?.message || '获取本周活动失败' }
    } finally {
      loading.value = false
    }
  }

  // 获取本月活动
  const fetchMonthActivities = async (projectId, params = {}) => {
    try {
      loading.value = true
      const response = await projectsApi.getMonthActivities(projectId, params)
      if (response.status === 'success') {
        const transformedActivities = (response.data.activities || []).map(transformActivity)
        activities.value = transformedActivities
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch month activities failed:', error)
      return { success: false, error: error.response?.data?.message || '获取本月活动失败' }
    } finally {
      loading.value = false
    }
  }

  // 设置当前项目
  const setCurrentProject = (project) => {
    currentProject.value = project
  }

  // 清空数据
  const clearData = () => {
    projects.value = []
    currentProject.value = null
    activities.value = []
    stats.value = { total: 0, authorized: 0 }
    pagination.value = { page: 1, per_page: 20, total: 0, total_pages: 0 }
    isStatsCached.value = false
    isProjectsCached.value = false
    lastSearchQuery.value = ''
    lastPage.value = 1
  }

  return {
    projects,
    sortedProjects,
    getFilteredProjects,
    currentProject,
    activities,
    stats,
    loading,
    pagination,
    fetchStats,
    fetchProjects,
    fetchProjectOverview,
    fetchActivities,
    fetchTodayActivities,
    fetchWeekActivities,
    fetchMonthActivities,
    setCurrentProject,
    clearData
  }
})