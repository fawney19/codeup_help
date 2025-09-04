<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
    <!-- Header -->
    <header class="border-b-4 border-black bg-brutal-cyan">
      <div class="max-w-7xl mx-auto px-6 py-8">
        <div class="flex justify-between items-center">
          <div>
            <h1 
              class="text-4xl font-black text-gray-800 uppercase cursor-pointer hover:bg-brutal-yellow hover:px-2 transition-all"
              @click="goToProjectList"
            >
              {{ projectName }}
            </h1>
            <div class="bg-blue-600 text-white px-3 py-1 inline-block mt-2 font-bold text-sm">
              {{ currentProject?.overview?.description || '项目活动时间线' }}
            </div>
          </div>
          <div class="flex items-center">
            <UserAvatar />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-6">
      <!-- Time Filter Section -->
      <div class="bg-brutal-yellow border-4 border-blue-600 shadow-brutal p-6 mb-8">
        <h2 class="text-2xl font-black text-gray-800 uppercase mb-4 flex items-center">
          <Clock class="w-6 h-6 mr-3 text-blue-600" />
          时间筛选器
        </h2>
        <div class="flex flex-wrap gap-4">
          <button 
            v-for="filter in timeFilters" 
            :key="filter.value"
            @click="setTimeFilter(filter.value)"
            class="border-4 border-blue-600 px-4 py-2 font-black text-gray-800 uppercase transition-all hover:transform hover:scale-105"
            :class="activeTimeFilter === filter.value 
              ? 'bg-blue-600 text-brutal-yellow shadow-brutal-sm' 
              : 'bg-white hover:bg-brutal-pink'"
          >
            {{ filter.label }}
          </button>
        </div>
        
        <!-- Custom Date Range -->
        <div class="mt-6 flex flex-wrap gap-4">
          <div>
            <label class="block text-lg font-black text-gray-800 uppercase mb-2 flex items-center">
              <Calendar class="w-5 h-5 mr-2 text-blue-600" />
              开始日期
            </label>
            <input 
              type="date" 
              v-model="startDate" 
              @change="loadActivities"
              class="border-4 border-blue-600 px-3 py-2 font-bold focus:outline-none focus:bg-brutal-cyan"
            />
          </div>
          <div>
            <label class="block text-lg font-black text-gray-800 uppercase mb-2 flex items-center">
              <Calendar class="w-5 h-5 mr-2 text-blue-600" />
              结束日期
            </label>
            <input 
              type="date" 
              v-model="endDate" 
              @change="loadActivities"
              class="border-4 border-blue-600 px-3 py-2 font-bold focus:outline-none focus:bg-brutal-cyan"
            />
          </div>
          <div class="flex items-end">
            <button 
              @click="loadActivities" 
              class="bg-brutal-green border-4 border-blue-600 shadow-brutal px-6 py-2 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
            >
              <Search class="w-5 h-5 mr-2" />
              查询
            </button>
          </div>
        </div>
      </div>

      <!-- Activity Summary -->
      <div v-if="activitySummary" class="bg-brutal-pink border-4 border-blue-600 shadow-brutal p-6 mb-8">
        <div class="flex justify-between items-start mb-6">
          <h2 class="text-2xl font-black text-gray-800 uppercase flex items-center">
            <BarChart3 class="w-6 h-6 mr-3 text-blue-600" />
            活动概览
          </h2>
          <button 
            @click="openAIReportModal"
            :disabled="!activities.length"
            class="bg-brutal-orange border-4 border-blue-600 shadow-brutal px-4 py-2 font-black text-gray-800 uppercase hover:transform hover:scale-105 transition-all disabled:opacity-50"
          >
            <Sparkles class="w-5 h-5 mr-2" />
            生成AI报告
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-brutal-cyan border-4 border-blue-600 text-center p-4">
            <div class="text-3xl font-black text-gray-800">{{ activitySummary.pushCount }}</div>
            <div class="text-sm font-bold text-gray-800 uppercase">推送次数</div>
          </div>
          <div class="bg-brutal-green border-4 border-blue-600 text-center p-4">
            <div class="text-3xl font-black text-gray-800">{{ activitySummary.commitCount }}</div>
            <div class="text-sm font-bold text-gray-800 uppercase">提交数量</div>
          </div>
          <div class="bg-brutal-yellow border-4 border-blue-600 text-center p-4">
            <div class="text-3xl font-black text-gray-800">{{ activitySummary.fileChanges }}</div>
            <div class="text-sm font-bold text-gray-800 uppercase">文件变更</div>
          </div>
          <div class="bg-brutal-orange border-4 border-blue-600 text-center p-4">
            <div class="text-3xl font-black text-gray-800">{{ activitySummary.activeDays }}</div>
            <div class="text-sm font-bold text-gray-800 uppercase">活跃天数</div>
          </div>
        </div>
      </div>

      <!-- Activity Timeline -->
      <div class="bg-white border-4 border-blue-600 shadow-brutal-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-black text-gray-800 uppercase flex items-center">
            <TrendingUp class="w-6 h-6 mr-3 text-blue-600" />
            活动时间线
          </h2>
          <div v-if="Object.keys(groupedActivities).length > 0" class="flex items-center space-x-4">
            <button 
              @click="collapseAllDates"
              v-if="collapsedDates.size < Object.keys(groupedActivities).length"
              class="bg-brutal-cyan border-4 border-blue-600 px-3 py-1 font-black text-gray-800 text-sm uppercase hover:bg-brutal-pink transition-colors"
            >
              <FolderMinus class="w-4 h-4 mr-2" />
              全部收缩
            </button>
            <button 
              @click="expandAllDates"
              v-if="collapsedDates.size > 0"
              class="bg-brutal-green border-4 border-blue-600 px-3 py-1 font-black text-gray-800 text-sm uppercase hover:bg-brutal-yellow transition-colors"
            >
              <FolderOpen class="w-4 h-4 mr-2" />
              全部展开
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="text-center py-12">
          <div class="bg-brutal-yellow border-4 border-blue-600 shadow-brutal p-6 inline-block">
            <div class="text-xl font-black text-gray-800 uppercase mb-2 flex items-center justify-center">
              <Loader2 class="w-6 h-6 mr-3 animate-spin text-blue-600" />
              加载中
            </div>
            <div class="text-sm font-bold text-gray-800">正在获取活动记录...</div>
          </div>
        </div>

        <div v-else-if="activities.length === 0" class="text-center py-12">
          <div class="bg-brutal-orange border-4 border-blue-600 shadow-brutal-lg p-8 max-w-md mx-auto transform -rotate-1">
            <h3 class="text-xl font-black text-gray-800 uppercase mb-4">📭 没有活动记录</h3>
            <p class="text-sm font-bold text-gray-800">
              在所选时间范围内没有找到任何推送活动
            </p>
          </div>
        </div>

        <div v-else class="space-y-6">
          <!-- Group activities by date -->
          <div v-for="(dayActivities, date) in groupedActivities" :key="date" class="relative">
            <!-- Date Header -->
            <div 
              class="flex items-center mb-4 cursor-pointer hover:bg-brutal-yellow hover:px-2 p-2 -mx-2 transition-all border-2 border-blue-600"
              @click="toggleDateCollapse(date)"
            >
              <div class="flex items-center">
                <span class="w-6 h-6 bg-blue-600 text-white flex items-center justify-center font-black mr-3">
                  {{ isDateCollapsed(date) ? '►' : '▼' }}
                </span>
                <div class="bg-brutal-pink border-2 border-blue-600 px-4 py-2 font-black text-gray-800 text-sm uppercase">
                  {{ formatDate(date) }}
                </div>
              </div>
              <div class="flex-1 h-1 bg-blue-600 ml-4"></div>
              <div class="ml-4 bg-blue-600 text-white px-2 py-1 font-bold text-xs uppercase">
                {{ dayActivities.length }} 个活动
              </div>
            </div>

            <!-- Activities for this date -->
            <div 
              v-if="!isDateCollapsed(date)" 
              class="pl-4 border-l-4 border-black space-y-4 transition-all duration-200"
            >
              <div 
                v-for="activity in dayActivities" 
                :key="activity.id || activity.created_at"
                class="relative border-4 border-blue-600 shadow-brutal bg-white p-4 hover:shadow-brutal-lg hover:transform hover:-translate-y-1 transition-all"
              >
                <!-- Activity Icon -->
                <div class="absolute -left-8 w-8 h-8 bg-brutal-green border-2 border-blue-600 flex items-center justify-center font-black text-gray-800 text-xs">
                  <FileText class="w-4 h-4" />
                </div>

                <!-- Activity Content -->
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center space-x-2">
                      <h3 class="text-sm font-medium text-gray-900">
                        {{ activity.action || 'pushed to' }}
                      </h3>
                      <span class="text-sm text-gray-500">
                        {{ activity.target_title || activity.ref_name || 'master' }}
                      </span>
                    </div>
                    
                    <p v-if="activity.note" class="mt-1 text-sm text-gray-600">
                      {{ activity.note }}
                    </p>
                    
                    <!-- Commit details if available -->
                    <div v-if="activity.commits && activity.commits.length" class="mt-2 space-y-1">
                      <div 
                        v-for="commit in activity.commits.slice(0, 3)" 
                        :key="commit.id"
                        class="text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded"
                      >
                        <div class="font-bold mb-1">{{ commit.id?.substring(0, 7) }}</div>
                        <div class="whitespace-pre-wrap">{{ commit.message }}</div>
                      </div>
                      <div v-if="activity.commits.length > 3" class="text-xs text-gray-400">
                        还有 {{ activity.commits.length - 3 }} 个提交...
                      </div>
                    </div>
                  </div>
                  
                  <div class="ml-4 text-right flex-shrink-0">
                    <div class="text-xs text-gray-500">
                      {{ formatTime(activity.created_at) }}
                    </div>
                    <div v-if="activity.author_name" class="text-xs text-gray-400 mt-1">
                      {{ activity.author_name }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- AI Report Modal -->
    <div 
      v-if="showAIReportModal" 
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click="closeAIReportModal"
    >
      <div 
        class="bg-white border-4 border-blue-600 shadow-brutal-lg max-w-4xl w-full max-h-[90vh] flex flex-col transform rotate-1 hover:rotate-0 transition-transform duration-300"
        @click.stop
      >
        <!-- Modal Header -->
        <div class="bg-brutal-yellow border-b-4 border-blue-600 p-6 flex items-center justify-between">
          <h2 class="text-2xl font-black text-gray-800 uppercase flex items-center">
            <Sparkles class="w-6 h-6 mr-3 text-blue-600" />
            AI智能报告
          </h2>
          <div class="flex items-center space-x-3">
            <button 
              @click="handleAIReportButtonClick"
              :disabled="aiGenerating"
              class="bg-brutal-green border-4 border-blue-600 shadow-brutal px-4 py-2 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              data-ai-generate-btn
            >
              <Sparkles class="w-4 h-4 mr-2 inline" />
              {{ aiGenerating ? '生成中...' : (aiReport ? '重新生成' : '生成报告') }}
            </button>
            <button 
              @click="closeAIReportModal"
              class="bg-brutal-red border-4 border-blue-600 shadow-brutal px-3 py-2 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Modal Content -->
        <div class="flex-1 overflow-auto p-6 bg-white">
          <!-- Loading State -->
          <div v-if="aiGenerating && !aiReport" class="text-center py-12">
            <div class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal p-8 inline-block transform -rotate-1">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
              <p class="mt-4 text-gray-800 font-black uppercase flex items-center justify-center">
                <Activity class="w-4 h-4 mr-2" />
                正在生成AI报告...
              </p>
              <p v-if="generateDuration" class="mt-2 text-sm text-gray-600 font-bold flex items-center justify-center">
                <Clock class="w-3 h-3 mr-1" />
                已耗时: {{ generateDuration }}
              </p>
            </div>
          </div>
          
          <!-- AI Report Content -->
          <div v-else-if="aiReport" class="space-y-6">
            <div class="bg-brutal-pink border-4 border-blue-600 shadow-brutal p-4 flex items-center justify-between transform rotate-1">
              <div>
                <h3 class="text-xl font-black text-gray-800 uppercase flex items-center">
                  <FileText class="w-5 h-5 mr-2" />
                  报告内容
                </h3>
                <div class="flex items-center space-x-4 mt-2 text-sm font-bold text-gray-600">
                  <span v-if="aiGenerateEndTime" class="bg-blue-600 text-white px-2 py-1 rounded flex items-center">
                    <Calendar class="w-3 h-3 mr-1" />
                    {{ aiGenerateEndTime.toLocaleString('zh-CN') }}
                  </span>
                  <span v-if="generateDuration" class="bg-blue-600 text-white px-2 py-1 rounded flex items-center">
                    <Clock class="w-3 h-3 mr-1" />
                    {{ generateDuration }}
                  </span>
                </div>
              </div>
              <div class="flex space-x-2">
                <button 
                  @click="copyReport"
                  class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal-sm px-3 py-2 font-bold text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all text-xs"
                >
                  <Copy class="w-3 h-3 mr-1 inline" />
                  复制
                </button>
                <button 
                  @click="copyReportAsText"
                  class="bg-brutal-green border-4 border-blue-600 shadow-brutal-sm px-3 py-2 font-bold text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all text-xs"
                >
                  <FileText class="w-3 h-3 mr-1 inline" />
                  文本
                </button>
                <button 
                  @click="downloadReport"
                  class="bg-brutal-orange border-4 border-blue-600 shadow-brutal-sm px-3 py-2 font-bold text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all text-xs"
                >
                  <Download class="w-3 h-3 mr-1 inline" />
                  下载
                </button>
              </div>
            </div>
            <div 
              ref="reportContainer"
              class="border-4 border-blue-600 shadow-brutal-sm p-6 overflow-auto max-h-96 scroll-smooth bg-white transform -rotate-1"
            >
              <!-- 加载中显示 -->
              <div v-if="aiGenerating" class="flex flex-col items-center justify-center py-12">
                <div class="bg-brutal-orange border-4 border-blue-600 shadow-brutal p-4 inline-block">
                  <div class="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
                </div>
                <p class="text-gray-800 font-bold text-sm mt-4 flex items-center justify-center">
                  <Activity class="w-4 h-4 mr-2" />
                  正在生成AI报告...
                </p>
                <p v-if="generateDuration" class="text-gray-600 font-bold text-xs mt-2 flex items-center justify-center">
                  <Clock class="w-3 h-3 mr-1" />
                  {{ generateDuration }}
                </p>
              </div>
              <!-- 生成完成后显示报告内容 -->
              <div 
                v-else 
                class="whitespace-pre-wrap font-mono text-sm text-gray-800 leading-relaxed"
              >
                {{ aiReport }}
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <div class="bg-brutal-yellow border-4 border-blue-600 shadow-brutal p-8 inline-block transform rotate-1 hover:-rotate-1 transition-transform duration-300">
              <Sparkles class="w-16 h-16 text-blue-600 mb-4 mx-auto" />
              <h3 class="text-2xl font-black text-gray-800 uppercase mb-4 flex items-center justify-center">
                <Sparkles class="w-8 h-8 mr-3" />
                AI智能报告
              </h3>
              <p class="text-sm font-bold text-gray-800 mb-4">点击上方按钮生成智能分析报告</p>
              <div class="text-xs text-gray-600 font-bold flex items-center justify-center">
                <Activity class="w-4 h-4 mr-2" />
                AI将分析您的项目活动并生成详细报告
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast通知系统 -->
    <Teleport to="body">
      <div class="fixed top-4 right-4 z-[99999] space-y-2">
        <TransitionGroup name="toast" tag="div">
          <div 
            v-for="(toast, index) in toasts"
            :key="toast.id"
            class="bg-brutal-green border-4 border-blue-600 shadow-brutal overflow-hidden animate-fade-in toast-container min-w-[300px] max-w-[400px] transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
            :style="{ 
              'z-index': 99999 - index,
              'margin-top': index > 0 ? '0.5rem' : '0',
              'transform': `rotate(${index % 2 === 0 ? '1deg' : '-1deg'})`
            }"
          >
            <div class="countdown-bar bg-blue-600" :key="'bar-' + toast.id"></div>
            <div class="flex items-center px-4 py-3">
              <div class="flex-shrink-0">
                <CheckCircle class="w-5 h-5 text-blue-600" />
              </div>
              <div class="ml-3 flex-1">
                <p class="text-sm font-black text-gray-800 uppercase">
                  {{ toast.message }}
                </p>
              </div>
              <div class="ml-2">
                <button 
                  @click="removeToast(toast.id)"
                  class="bg-brutal-red border-2 border-blue-600 shadow-brutal-sm px-2 py-1 font-bold text-gray-800 hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                >
                  <X class="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, Teleport, TransitionGroup } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { useAuthStore } from '@/stores/auth'
import { projectsApi } from '@/services/api'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import {
  ArrowLeft,
  RefreshCw,
  Calendar,
  Clock,
  CalendarDays,
  Search,
  Activity,
  GitCommit,
  FileText,
  Sparkles,
  Copy,
  Download,
  ChevronDown,
  ChevronRight,
  X,
  CheckCircle,
  BarChart3,
  TrendingUp,
  Loader2,
  FolderMinus,
  FolderOpen
} from 'lucide-vue-next'

const props = defineProps({
  id: {
    type: [String, Number],
    required: true
  },
  name: {
    type: String,
    required: false
  }
})

const route = useRoute()
const router = useRouter()
const projectsStore = useProjectsStore()
const authStore = useAuthStore()

const activeTimeFilter = ref('week')
const startDate = ref('')
const endDate = ref('')
const summaryText = ref('') // 内部变量，不显示
const aiReport = ref('') // 完整的报告内容
const aiGenerating = ref(false)
const aiGenerateStartTime = ref(null) // 开始生成时间
const aiGenerateEndTime = ref(null) // 完成生成时间
const generateTimer = ref(null) // 用于更新实时耗时的定时器
const showAIReportModal = ref(false)
const collapsedDates = ref(new Set())

// DOM refs
const reportContainer = ref(null)

// Toast系统
const toasts = ref([])
let toastId = 0

// 时间筛选器选项
const timeFilters = [
  { value: 'today', label: '今天', icon: Clock },
  { value: 'week', label: '本周', icon: Calendar },
  { value: 'month', label: '本月', icon: CalendarDays },
  { value: 'year', label: '今年', icon: CalendarDays }
]

// 使用 computed 保持响应性
const currentProject = computed(() => projectsStore.currentProject)
const activities = computed(() => projectsStore.activities)
const loading = computed(() => projectsStore.loading)

// 获取项目名称，优先使用URL参数中的名称
const projectName = computed(() => {
  if (props.name) {
    return decodeURIComponent(props.name)
  }
  return currentProject.value?.overview?.name || '加载中...'
})

// 实时更新的毫秒计时器
const currentTime = ref(new Date())

// 计算生成耗时（毫秒精度）
const generateDuration = computed(() => {
  if (!aiGenerateStartTime.value) return null
  
  if (aiGenerating.value) {
    // 正在生成中，显示实时耗时（毫秒精度）
    const now = currentTime.value
    const durationMs = now - aiGenerateStartTime.value
    const seconds = Math.floor(durationMs / 1000)
    const milliseconds = Math.floor((durationMs % 1000) / 10) // 显示两位毫秒
    return `${seconds}.${milliseconds.toString().padStart(2, '0')}秒`
  } else if (aiGenerateEndTime.value) {
    // 已完成，显示总耗时
    const durationMs = aiGenerateEndTime.value - aiGenerateStartTime.value
    const seconds = Math.floor(durationMs / 1000)
    const milliseconds = Math.floor((durationMs % 1000) / 10) // 显示两位毫秒
    return `${seconds}.${milliseconds.toString().padStart(2, '0')}秒`
  }
  
  return null
})

// 按日期分组的活动
const groupedActivities = computed(() => {
  const groups = {}
  activities.value.forEach(activity => {
    const date = new Date(activity.created_at).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(activity)
  })
  
  // 按时间排序每一天的活动
  Object.keys(groups).forEach(date => {
    groups[date].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  })
  
  return groups
})

// 活动统计摘要
const activitySummary = computed(() => {
  if (!activities.value.length) return null
  
  const pushCount = activities.value.filter(a => a.action?.includes('push')).length
  const commitCount = activities.value.reduce((sum, a) => sum + (a.commits?.length || 0), 0)
  const activeDays = Object.keys(groupedActivities.value).length
  const fileChanges = activities.value.reduce((sum, a) => {
    return sum + (a.commits?.reduce((cSum, c) => cSum + (c.added || 0) + (c.modified || 0) + (c.removed || 0), 0) || 0)
  }, 0)
  
  return {
    pushCount,
    commitCount,
    fileChanges,
    activeDays
  }
})

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      weekday: 'long'
    })
  }
}

// 格式化时间
const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 根据筛选器设置日期范围
const setDatesByFilter = (filterValue) => {
  const today = new Date()
  // 使用本地时间格式化日期，避免时区问题
  const formatDateForInput = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  switch (filterValue) {
    case 'today':
      // 只查询今天
      startDate.value = formatDateForInput(today)
      endDate.value = formatDateForInput(today)
      break
      
    case 'week':
      // 本周开始到今天（周一开始）
      const startOfWeek = new Date(today)
      const dayOfWeek = today.getDay()
      // 将周日(0)转换为7，然后计算到周一的天数
      const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1
      startOfWeek.setDate(today.getDate() - daysToMonday)
      startDate.value = formatDateForInput(startOfWeek)
      endDate.value = formatDateForInput(today)
      break
      
    case 'month':
      // 本月1号到今天
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      startDate.value = formatDateForInput(startOfMonth)
      endDate.value = formatDateForInput(today)
      break
      
    case 'year':
      // 今年1月1号到今天
      const startOfYear = new Date(today.getFullYear(), 0, 1)
      startDate.value = formatDateForInput(startOfYear)
      endDate.value = formatDateForInput(today)
      break
  }
}

// 设置时间筛选器
const setTimeFilter = (filterValue) => {
  activeTimeFilter.value = filterValue
  setDatesByFilter(filterValue)
  loadActivities()
}

// 加载活动数据
const loadActivities = async () => {
  const projectId = props.id
  
  if (!startDate.value || !endDate.value) {
    console.warn('开始日期或结束日期为空，跳过加载')
    return
  }
  
  try {
    // 统一使用日期范围API
    const result = await projectsStore.fetchActivities(projectId, {
      start_date: startDate.value,
      end_date: endDate.value
    })
    
    // Clear previous summaries when loading new data
    summaryText.value = ''
    aiReport.value = ''
    
  } catch (error) {
    console.error('Failed to load activities:', error)
  }
}

// 生成活动小结
const generateSummary = () => {
  if (!activities.value.length) return
  
  const { pushCount, commitCount, fileChanges, activeDays } = activitySummary.value
  const timeRange = getTimeRangeText()
  
  let summary = `${timeRange}活动小结：\n\n`
  summary += `统计概览：\n`
  summary += `• 推送次数：${pushCount} 次\n`
  summary += `• 提交数量：${commitCount} 个\n`
  summary += `• 文件变更：${fileChanges} 处\n`
  summary += `• 活跃天数：${activeDays} 天\n\n`
  
  // 按日期统计推送和提交次数
  const dailyStats = {}
  Object.entries(groupedActivities.value).forEach(([date, dayActivities]) => {
    const pushes = dayActivities.filter(a => a.action?.includes('Push')).length
    const commits = dayActivities.reduce((sum, a) => sum + (a.commits?.length || 0), 0)
    dailyStats[date] = { pushes, commits, activities: dayActivities }
  })
  
  summary += `每日统计：\n`
  Object.entries(dailyStats)
    .sort(([a], [b]) => new Date(b) - new Date(a))
    .forEach(([date, stats]) => {
      const formattedDate = new Date(date).toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
      })
      summary += `• ${formattedDate}：推送 ${stats.pushes} 次，提交 ${stats.commits} 个\n`
    })
  summary += `\n`
  
  // 详细的提交内容
  summary += `详细提交记录：\n`
  Object.entries(dailyStats)
    .sort(([a], [b]) => new Date(b) - new Date(a))
    .forEach(([date, stats]) => {
      const formattedDate = new Date(date).toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
      })
      summary += `\n=== ${formattedDate} ===\n`
      
      stats.activities.forEach((activity, index) => {
        const time = formatTime(activity.created_at)
        summary += `\n${index + 1}. [${time}] ${activity.action || 'Push'} to ${activity.target_title || activity.ref_name || 'master'}\n`
        
        if (activity.note) {
          summary += `   备注: ${activity.note}\n`
        }
        
        if (activity.commits && activity.commits.length > 0) {
          summary += `   提交内容:\n`
          activity.commits.forEach((commit, commitIndex) => {
            summary += `   ${commitIndex + 1}) ${commit.id?.substring(0, 7)} - ${commit.message || '无提交信息'}\n`
            if (commit.author && typeof commit.author === 'string') {
              summary += `      作者: ${commit.author}\n`
            } else if (commit.author && commit.author.name) {
              summary += `      作者: ${commit.author.name}\n`
            }
          })
        }
      })
    })
  
  summaryText.value = summary
}

// 打开AI报告模态框
const openAIReportModal = () => {
  showAIReportModal.value = true
  currentTime.value = new Date()
  // 只有在没有正在生成且没有现有报告时才开始新的生成
  if (activities.value.length > 0 && !aiGenerating.value && !aiReport.value) {
    generateAIReport()
  }
}

// 关闭AI报告模态框
const closeAIReportModal = () => {
  showAIReportModal.value = false
}



// 将markdown转换为纯文本
const markdownToText = (markdown) => {
  if (!markdown) return ''
  
  // 简单的markdown到文本转换
  return markdown
    .replace(/#{1,6}\s+/g, '') // 移除标题标记
    .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗体标记
    .replace(/\*(.*?)\*/g, '$1') // 移除斜体标记
    .replace(/`(.*?)`/g, '$1') // 移除代码标记
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1') // 移除链接，保留文本
    .replace(/^\s*[-*+]\s+/gm, '• ') // 转换列表标记
    // .replace(/^\s*\d+\.\s+/gm, '') // 保留有序列表的序号
    .replace(/\n\s*\n/g, '\n\n') // 规范化换行
    .trim()
}

// 获取时间范围文本
const getTimeRangeText = () => {
  if (startDate.value && endDate.value) {
    // 如果是预设的时间范围，使用中文标签
    switch (activeTimeFilter.value) {
      case 'today': return '今日'
      case 'week': return '本周'
      case 'month': return '本月'
      case 'year': return '今年'
      default: return `${startDate.value} 至 ${endDate.value}`
    }
  }
  return '时间范围未设置'
}

// 处理AI报告按钮点击（强制重新生成）
const handleAIReportButtonClick = () => {
  if (aiGenerating.value) return // 如果正在生成中，不处理
  
  // 重置状态，强制重新生成
  aiReport.value = ''
  aiGenerateStartTime.value = null
  aiGenerateEndTime.value = null
  currentTime.value = new Date()
  if (generateTimer.value) {
    clearInterval(generateTimer.value)
    generateTimer.value = null
  }
  generateAIReport()
}

// AI生成报告
const generateAIReport = async () => {
  if (!activities.value.length) return
  
  // 如果已经在生成中，不重复生成
  if (aiGenerating.value) return
  
  try {
    aiGenerating.value = true
    aiReport.value = ''
    aiGenerateStartTime.value = new Date()
    aiGenerateEndTime.value = null
    
    // 启动高精度定时器用于更新实时耗时显示（100毫秒间隔）
    generateTimer.value = setInterval(() => {
      currentTime.value = new Date()
    }, 100)
    
    // 先生成内部小结（不显示给用户）
    generateSummary()
    
    // 准备AI报告请求数据
    const reportData = {
      project_id: parseInt(props.id),
      report_type: 'activity_summary',
      time_range: 'custom',
      start_date: startDate.value,
      end_date: endDate.value,
      additional_context: `项目：${projectName.value}
时间范围：${getTimeRangeText()}
活动总结：${summaryText.value}`,
      response_mode: 'blocking',
      user: 'frontend_user'
    }
    
    // 调用阻塞式AI报告生成API
    const response = await projectsApi.generateAIReportBlocking(props.id, reportData)
    
    if (response && response.data && response.data.answer) {
      aiReport.value = response.data.answer
      aiGenerateEndTime.value = new Date()
      // 清除定时器
      if (generateTimer.value) {
        clearInterval(generateTimer.value)
        generateTimer.value = null
      }
    }
    
  } catch (error) {
    console.error('AI报告生成失败:', error)
    aiReport.value = `## 报告生成失败

很抱歉，AI报告生成过程中出现了错误：${error.message}

请稍后重试，或联系系统管理员。

---
*错误时间：${new Date().toLocaleString('zh-CN')}*`
    aiGenerateEndTime.value = new Date()
  } finally {
    aiGenerating.value = false
    // 清除定时器
    if (generateTimer.value) {
      clearInterval(generateTimer.value)
      generateTimer.value = null
    }
  }
}

// Toast管理函数
const addToast = (message, type = 'success') => {
  const toast = {
    id: ++toastId,
    message,
    type,
    timestamp: Date.now()
  }
  
  toasts.value.push(toast)
  console.log('Toast添加:', message)
  
  // 自动移除Toast
  setTimeout(() => {
    removeToast(toast.id)
  }, 4000)
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
    console.log('Toast移除:', id)
  }
}

// 显示复制成功提示
const showCopyToast = (message) => {
  addToast(message, 'success')
}

// 复制报告（markdown格式）
const copyReport = async () => {
  try {
    if (!aiReport.value) {
      showCopyToast('暂无报告内容可复制')
      return
    }
    
    await navigator.clipboard.writeText(aiReport.value)
    showCopyToast('报告已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    showCopyToast('复制失败，请重试')
  }
}

// 复制报告为纯文本格式
const copyReportAsText = async () => {
  try {
    if (!aiReport.value) {
      showCopyToast('暂无报告内容可复制')
      return
    }
    
    const plainText = markdownToText(aiReport.value)
    await navigator.clipboard.writeText(plainText)
    showCopyToast('文本已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    showCopyToast('复制失败，请重试')
  }
}

// 下载报告
const downloadReport = () => {
  const blob = new Blob([aiReport.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `项目活动报告_${props.id}_${new Date().toISOString().split('T')[0]}.md`
  link.click()
  URL.revokeObjectURL(url)
}

// 切换日期折叠状态
const toggleDateCollapse = (date) => {
  if (collapsedDates.value.has(date)) {
    collapsedDates.value.delete(date)
  } else {
    collapsedDates.value.add(date)
  }
}

// 检查日期是否已折叠
const isDateCollapsed = (date) => {
  return collapsedDates.value.has(date)
}

// 收缩所有日期
const collapseAllDates = () => {
  collapsedDates.value = new Set(Object.keys(groupedActivities.value))
}

// 展开所有日期
const expandAllDates = () => {
  collapsedDates.value.clear()
}

// 导航到项目列表
const goToProjectList = () => {
  router.push('/')
}

// 刷新数据
const refreshData = () => {
  loadActivities()
  if (props.id) {
    projectsStore.fetchProjectOverview(props.id)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  if (props.id) {
    // 初始化默认时间范围
    setDatesByFilter(activeTimeFilter.value)
    
    // 只有当前项目信息不存在时才获取项目概览
    if (!currentProject.value?.overview) {
      projectsStore.fetchProjectOverview(props.id)
    }
    loadActivities()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  // 清理工作
})

// 监听路由参数变化
watch(() => props.id, (newId) => {
  if (newId) {
    // 设置默认时间范围
    setDatesByFilter(activeTimeFilter.value)
    projectsStore.fetchProjectOverview(newId)
    loadActivities()
  }
})
</script>

<style scoped>
.markdown-content {
  line-height: 1.6;
  color: #1f2937;
}

.markdown-content h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.25rem;
  color: #111827;
}

.markdown-content h2 {
  font-size: 1.25rem;
  font-weight: bold;
  margin: 1rem 0 0.5rem 0;
  color: #374151;
}

.markdown-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0.75rem 0 0.25rem 0;
  color: #4b5563;
}

.markdown-content ul, .markdown-content ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.markdown-content li {
  margin: 0.25rem 0;
  color: #374151;
}

.markdown-content p {
  margin: 0.5rem 0;
  color: #374151;
}

.markdown-content pre {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 0.75rem;
  border-radius: 0.375rem;
  margin: 0.75rem 0;
  overflow-x: auto;
  border: 1px solid #374151;
}

.markdown-content code {
  background-color: #f3f4f6;
  color: #1f2937;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-size: 0.875rem;
}

.markdown-content pre code {
  background: none;
  color: #f9fafb;
  padding: 0;
}

.markdown-content blockquote {
  border-left: 4px solid #3b82f6;
  background-color: #f8fafc;
  padding: 0.75rem 1rem;
  margin: 0.75rem 0;
  color: #475569;
  font-style: italic;
  border-radius: 0.25rem;
}

/* Toast提示样式 */
.toast-container {
  position: relative;
  max-width: 320px;
  backdrop-filter: blur(10px);
  pointer-events: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(16, 185, 129, 0.1);
  background: rgba(240, 253, 244, 0.95);
}

.countdown-bar {
  position: absolute;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 4px 4px 0 0;
  animation: countdown 4s linear forwards;
  width: 100%;
}

@keyframes countdown {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* Toast动画 */
.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Toast进入离开动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-move {
  transition: transform 0.4s ease;
}

.markdown-content strong {
  font-weight: bold;
  color: #111827;
}

.markdown-content em {
  font-style: italic;
  color: #4b5563;
}

/* 表格样式 */
.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #d1d5db;
  padding: 0.5rem;
  text-align: left;
}

.markdown-content th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #111827;
}

/* 链接样式 */
.markdown-content a {
  color: #3b82f6;
  text-decoration: underline;
}

.markdown-content a:hover {
  color: #1d4ed8;
}
</style>