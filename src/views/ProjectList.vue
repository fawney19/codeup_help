<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Codeup 项目管理</h1>
            <p class="mt-1 text-sm text-gray-500">
              欢迎回来，{{ authStore.user?.name }}
            </p>
          </div>
          <div class="flex items-center">
            <!-- 用户头像 -->
            <UserAvatar />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">总项目数</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.total }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-green-100">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">可访问项目</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.authorized }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg border shadow-sm p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-purple-100">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">活跃项目</p>
              <p class="text-2xl font-semibold text-gray-900">{{ activeProjects }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filters -->
      <div class="mb-6 flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            placeholder="搜索项目..."
            class="flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
          />
        </div>
        <button 
          @click="refreshProjects" 
          :disabled="loading"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          刷新
        </button>
      </div>

      <!-- Projects Grid -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-500">加载项目中...</p>
      </div>

      <div v-else-if="sortedProjects.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">没有找到项目</h3>
        <p class="mt-1 text-sm text-gray-500">
          {{ searchQuery ? '尝试调整搜索关键词' : '您暂时没有可访问的项目' }}
        </p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="project in sortedProjects" 
          :key="project.id"
          class="bg-white rounded-lg border shadow-sm p-6 hover:shadow-lg transition-shadow cursor-pointer"
          @click="goToProject(project.id)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-medium text-gray-900 truncate">
                {{ project.name || project.path }}
              </h3>
              <p class="mt-1 text-sm text-gray-500 truncate">
                {{ project.description || '暂无描述' }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0">
              <span v-if="project.visibility" 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="project.visibility === 'public' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                {{ project.visibility === 'public' ? '公开' : '私有' }}
              </span>
            </div>
          </div>
          
          <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>{{ formatLastActivity(project.last_activity_at) }}</span>
            </div>
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path>
              </svg>
              <span>{{ project.default_branch || 'master' }}</span>
            </div>
          </div>
          
          <div class="mt-4 flex items-center justify-between">
            <div class="flex items-center text-sm text-gray-500">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
              </svg>
              <span>{{ project.star_count || 0 }}</span>
            </div>
            <div class="text-sm text-gray-500">
              ID: {{ project.id }}
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination && pagination.total_pages > 1" class="mt-8 flex justify-center">
        <div class="flex items-center space-x-2">
          <button 
            :disabled="pagination.page <= 1"
            @click="changePage(pagination.page - 1)"
            class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            上一页
          </button>
          
          <span class="text-sm text-gray-500 px-4">
            第 {{ pagination.page }} / {{ pagination.total_pages }} 页
          </span>
          
          <button 
            :disabled="pagination.page >= pagination.total_pages"
            @click="changePage(pagination.page + 1)"
            class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import UserAvatar from '@/components/UserAvatar.vue'

const router = useRouter()
const authStore = useAuthStore()
const projectsStore = useProjectsStore()

const searchQuery = ref('')
const searchTimeout = ref(null)

// 计算属性 - 保持响应性
const projects = computed(() => projectsStore.projects)
const sortedProjects = computed(() => projectsStore.getFilteredProjects(searchQuery.value))
const stats = computed(() => projectsStore.stats)
const loading = computed(() => projectsStore.loading)
const pagination = computed(() => projectsStore.pagination)
const activeProjects = computed(() => {
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  if (!sortedProjects.value || !Array.isArray(sortedProjects.value)) {
    return 0
  }
  return sortedProjects.value.filter(project => {
    const lastActivity = new Date(project.last_activity_at)
    return lastActivity > oneWeekAgo
  }).length
})

// 防抖搜索 - 只更新统计，项目列表使用前端过滤
const debouncedSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    // 只更新统计数据，项目列表通过计算属性自动过滤
    projectsStore.fetchStats({ search: searchQuery.value }, true)
  }, 500)
}

// 格式化最后活动时间
const formatLastActivity = (dateString) => {
  if (!dateString) return '暂无活动'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return '1天前'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}月前`
  return `${Math.floor(diffDays / 365)}年前`
}

// 加载项目数据
const loadProjects = async (forceRefresh = false) => {
  await projectsStore.fetchStats({ search: searchQuery.value }, forceRefresh)
  // 总是获取所有项目，前端进行过滤
  await projectsStore.fetchProjects({ 
    search: '', // 不在后端过滤，获取所有项目
    page: pagination.value?.page || 1,
    per_page: pagination.value?.per_page || 20
  }, forceRefresh)
}

// 刷新项目
const refreshProjects = () => {
  projectsStore.clearData() // 清除缓存
  loadProjects(true) // 强制刷新缓存
}

// 切换页面
const changePage = (page) => {
  projectsStore.pagination.page = page
  loadProjects()
}

// 跳转到项目详情
const goToProject = (projectId) => {
  const project = projects.value.find(p => p.id === projectId)
  if (project) {
    // 将项目信息存储到store，方便详情页直接使用
    projectsStore.setCurrentProject({ overview: project })
    // URL编码项目名称，避免特殊字符问题
    const encodedName = encodeURIComponent(project.name || project.path || 'project')
    router.push(`/projects/${projectId}/${encodedName}`)
  } else {
    router.push(`/projects/${projectId}`)
  }
}


// 组件挂载时加载数据
onMounted(() => {
  loadProjects()
})
</script>