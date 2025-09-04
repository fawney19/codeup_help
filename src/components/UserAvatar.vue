<template>
  <div class="relative">
    <div
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      class="cursor-pointer"
    >
      <div class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal p-2 hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all">
        <!-- 如果有头像就显示图片，否则显示首字母 -->
        <div v-if="authStore.user?.avatar_url" class="h-8 w-8 overflow-hidden">
          <img 
            :src="authStore.user.avatar_url"
            :alt="getUserDisplayName()"
            class="h-8 w-8 object-cover"
            @error="showFallback = true"
          />
        </div>
        <div v-else class="h-8 w-8 flex items-center justify-center">
          <span class="text-blue-600 font-black text-lg uppercase">
            {{ getUserInitials() }}
          </span>
        </div>
      </div>
    </div>

    <!-- Neo-Brutalism 风格提示框 -->
    <div 
      v-show="showTooltip"
      @mouseenter="handleTooltipEnter"
      @mouseleave="handleTooltipLeave"
      class="absolute right-0 z-10 mt-2 w-64 bg-white border-4 border-blue-600 shadow-brutal-lg transform transition-all duration-200"
      :class="showTooltip ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'"
    >
      <!-- 用户信息区域 -->
      <div class="bg-brutal-yellow p-4 border-b-4 border-blue-600">
        <div class="font-black text-gray-800 text-lg uppercase truncate">
          {{ getUserDisplayName() }}
        </div>
        <div class="font-bold text-gray-600 text-sm truncate">
          {{ authStore.user?.email || '未设置邮箱' }}
        </div>
      </div>

      <!-- 菜单项 -->
      <div class="p-2">
        <button 
          @click="logout" 
          class="w-full bg-brutal-red border-4 border-blue-600 shadow-brutal-sm p-3 font-black text-gray-800 uppercase text-sm hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all flex items-center justify-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const showTooltip = ref(false)
const showFallback = ref(false)
let hideTimer = null

// 获取用户显示名称
const getUserDisplayName = () => {
  if (!authStore.user) return '未知用户'
  
  // 如果有名字就使用名字，否则从邮箱提取用户名
  if (authStore.user.name && authStore.user.name !== authStore.user.email) {
    return authStore.user.name
  }
  
  // 从邮箱提取用户名部分
  if (authStore.user.email) {
    return authStore.user.email.split('@')[0]
  }
  
  return '未知用户'
}

// 获取用户首字母
const getUserInitials = () => {
  const displayName = getUserDisplayName()
  
  if (displayName === '未知用户') {
    return '?'
  }
  
  // 提取首字母，最多2个
  const words = displayName.trim().split(/\s+/)
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  } else {
    return displayName[0].toUpperCase()
  }
}

// 处理头像鼠标进入
const handleMouseEnter = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  showTooltip.value = true
}

// 处理头像鼠标离开
const handleMouseLeave = () => {
  hideTimer = setTimeout(() => {
    showTooltip.value = false
  }, 100) // 100ms延迟，给用户时间移动到提示框
}

// 处理提示框鼠标进入
const handleTooltipEnter = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

// 处理提示框鼠标离开
const handleTooltipLeave = () => {
  showTooltip.value = false
}

// 退出登录
const logout = async () => {
  showTooltip.value = false
  authStore.logout()
  await router.push('/login')
}
</script>