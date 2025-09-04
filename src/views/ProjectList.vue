<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
    <!-- Header -->
    <header class="border-b-4 border-blue-600 bg-brutal-yellow">
      <div class="max-w-6xl mx-auto px-6 py-8">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-6xl font-black text-gray-800 uppercase tracking-tight">
              CODEUP
            </h1>
            <div class="text-xl font-bold text-gray-800 mt-2">
              PROJECT MANAGER
            </div>
          </div>
          <div class="flex items-center">
            <UserAvatar />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-6 py-8">
      <!-- Hero Section -->
      <div class="text-center py-8 mb-8">
        <div class="bg-brutal-pink border-4 border-blue-600 shadow-brutal p-8 mb-6 transform rotate-1">
          <h2 class="text-4xl font-black text-gray-800 uppercase mb-4">
            管理您的代码项目
          </h2>
          <p class="text-xl font-bold text-gray-800">
            强大的项目管理工具 / 简单粗暴的界面设计
          </p>
        </div>
      </div>

      <!-- Stats Section -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal p-6 transform -rotate-1">
          <div class="text-3xl font-black text-gray-800">{{ stats.total }}</div>
          <div class="text-lg font-bold text-gray-800 uppercase">总项目数</div>
        </div>
        <div class="bg-brutal-green border-4 border-blue-600 shadow-brutal p-6">
          <div class="text-3xl font-black text-gray-800">{{ stats.authorized }}</div>
          <div class="text-lg font-bold text-gray-800 uppercase">可访问项目</div>
        </div>
        <div class="bg-brutal-orange border-4 border-blue-600 shadow-brutal p-6 transform rotate-1">
          <div class="text-3xl font-black text-gray-800">{{ activeProjects }}</div>
          <div class="text-lg font-bold text-gray-800 uppercase">活跃项目</div>
        </div>
      </div>

      <!-- Search Card -->
      <div class="mb-8">
        <div class="bg-white border-4 border-blue-600 shadow-brutal-lg p-8">
          <!-- Search Section -->
          <div class="mb-8">
            <h3 class="text-2xl font-black text-gray-800 uppercase mb-4">搜索项目</h3>
            <div class="flex flex-col sm:flex-row gap-4">
              <div class="flex-1">
                <input
                  v-model="searchQuery"
                  @input="debouncedSearch"
                  placeholder="输入项目名称..."
                  class="w-full h-14 px-4 border-4 border-blue-600 font-bold text-lg focus:outline-none focus:bg-brutal-yellow transition-colors"
                />
              </div>
              <button 
                @click="refreshProjects" 
                :disabled="loading"
                class="bg-brutal-green border-4 border-blue-600 shadow-brutal px-8 py-3 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:opacity-50"
              >
                <span v-if="loading">刷新中...</span>
                <span v-else>刷新</span>
              </button>
            </div>
          </div>

          <!-- Quick Access Tags -->
          <div class="mb-6" v-if="sortedProjects.length > 0">
            <h3 class="text-xl font-black text-gray-800 uppercase mb-4">快速访问:</h3>
            <div class="flex flex-wrap gap-3">
              <button 
                v-for="project in sortedProjects.slice(0, 6)" 
                :key="project.id"
                @click="goToProject(project.id)"
                class="bg-brutal-pink border-4 border-blue-600 px-4 py-2 font-bold text-gray-800 hover:bg-brutal-cyan hover:transform hover:scale-105 transition-all"
              >
                {{ project.name || project.path }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Projects List -->
      <div v-if="loading" class="text-center py-12">
        <div class="bg-brutal-yellow border-4 border-blue-600 shadow-brutal p-8 inline-block">
          <div class="text-2xl font-black text-gray-800 uppercase">加载中...</div>
          <div class="mt-2 text-lg font-bold text-gray-800">正在获取项目列表</div>
        </div>
      </div>

      <div v-else-if="sortedProjects.length === 0" class="text-center py-12">
        <div class="bg-brutal-orange border-4 border-blue-600 shadow-brutal-lg p-8 max-w-md mx-auto transform -rotate-1">
          <h3 class="text-2xl font-black text-gray-800 uppercase mb-4">没有找到项目</h3>
          <p class="text-lg font-bold text-gray-800">
            {{ searchQuery ? '尝试调整搜索关键词' : '您暂时没有可访问的项目' }}
          </p>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div 
          v-for="(project, index) in sortedProjects" 
          :key="project.id"
          class="border-4 border-blue-600 shadow-brutal hover:shadow-brutal-lg transition-all duration-200 cursor-pointer group hover:transform hover:-translate-y-1"
          :class="[
            index % 4 === 0 ? 'bg-brutal-cyan' : 
            index % 4 === 1 ? 'bg-brutal-yellow' : 
            index % 4 === 2 ? 'bg-brutal-pink' : 
            'bg-brutal-green'
          ]"
          @click="goToProject(project.id)"
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-xl font-black text-gray-800 uppercase mb-2 flex-1">
                {{ project.name || project.path }}
              </h3>
              <div class="flex flex-col items-end space-y-2 ml-4">
                <span v-if="project.visibility" 
                      class="bg-blue-600 text-white px-2 py-1 font-bold text-xs uppercase border-2 border-blue-600"
                      :class="project.visibility === 'public' ? 'text-brutal-green' : 'text-brutal-yellow'">
                  {{ project.visibility === 'public' ? '公开' : '私有' }}
                </span>
                <span class="bg-white border-2 border-blue-600 px-2 py-1 text-xs font-bold">ID: {{ project.id }}</span>
              </div>
            </div>
            
            <p class="text-gray-800 font-bold mb-4 text-sm">
              {{ project.description || '暂无项目描述' }}
            </p>
            
            <div class="flex flex-wrap gap-2 text-xs font-bold text-gray-800">
              <div class="bg-blue-600 text-white px-2 py-1 border-2 border-blue-600 flex items-center">
                <Clock class="w-3 h-3 mr-1" />
                {{ formatLastActivity(project.last_activity_at) }}
              </div>
              <div class="bg-blue-600 text-white px-2 py-1 border-2 border-blue-600 flex items-center">
                <GitCommit class="w-3 h-3 mr-1" />
                {{ project.default_branch || 'master' }}
              </div>
              <div class="bg-blue-600 text-white px-2 py-1 border-2 border-blue-600 flex items-center" v-if="project.star_count">
                <Activity class="w-3 h-3 mr-1" />
                {{ project.star_count }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="pagination && pagination.total_pages > 1" class="mt-8 flex justify-center">
        <div class="flex items-center gap-4">
          <button 
            :disabled="pagination.page <= 1"
            @click="changePage(pagination.page - 1)"
            class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal px-6 py-3 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← 上一页
          </button>
          
          <div class="bg-white border-4 border-blue-600 px-6 py-3 font-black text-gray-800">
            {{ pagination.page }} / {{ pagination.total_pages }}
          </div>
          
          <button 
            :disabled="pagination.page >= pagination.total_pages"
            @click="changePage(pagination.page + 1)"
            class="bg-brutal-pink border-4 border-blue-600 shadow-brutal px-6 py-3 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页 →
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
import { Clock, GitCommit, Activity } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const projectsStore = useProjectsStore()

const searchQuery = ref('')
const searchTimeout = ref(null)

// 计算属性 - 保持响应性
const projects = computed(() => projectsStore.projects)
const sortedProjects = computed(() => projectsStore.projects) // 直接使用项目列表，后端已处理分页和搜索
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

// 防抖搜索 - 重新加载项目列表和统计
const debouncedSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    // 搜索时重置到第一页
    projectsStore.pagination.page = 1
    // 重新加载项目列表和统计数据
    loadProjects(true)
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
  // 获取项目列表，包含分页和搜索参数
  await projectsStore.fetchProjects({ 
    search: searchQuery.value,
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
const changePage = async (page) => {
  // 更新分页信息
  projectsStore.pagination.page = page
  // 重新加载项目数据
  await loadProjects()
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