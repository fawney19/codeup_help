<template>
  <div class="relative">
    <div
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      class="cursor-pointer"
    >
      <img 
        :src="authStore.user?.avatar_url || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'"
        :alt="authStore.user?.name"
        class="h-10 w-10 rounded-full border border-gray-200 transition-all hover:ring-2 hover:ring-blue-300 hover:ring-offset-2"
        @error="$event.target.src = 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'"
      />
    </div>

    <!-- 悬停提示框 -->
    <div 
      v-show="showTooltip"
      @mouseenter="handleTooltipEnter"
      @mouseleave="handleTooltipLeave"
      class="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-lg bg-white py-1 shadow-xl ring-1 ring-black ring-opacity-5 border border-gray-100 transform transition-all duration-200"
      :class="showTooltip ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'"
    >
      <!-- 用户信息 -->
      <div class="px-3 py-2 border-b border-gray-100">
        <p class="text-sm font-medium text-gray-900 truncate">
          {{ authStore.user?.name || '未知用户' }}
        </p>
        <p class="text-xs text-gray-500 truncate">
          {{ authStore.user?.email || '未设置邮箱' }}
        </p>
      </div>

      <!-- 菜单项 -->
      <div class="py-1">
        <button 
          @click="logout" 
          class="group flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
        >
          <svg class="w-4 h-4 mr-2 text-gray-400 group-hover:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showTooltip = ref(false)
let hideTimer = null

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
  await authStore.logout()
}
</script>