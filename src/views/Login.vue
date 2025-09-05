<template>
  <div class="min-h-screen relative overflow-hidden bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
    <!-- 背景动画层 -->
    <div class="absolute inset-0 overflow-hidden">
      <!-- 漂浮圆形 -->
      <div 
        v-for="(circle, index) in floatingCircles" 
        :key="`circle-${index}`"
        class="absolute rounded-full opacity-10 animate-bounce"
        :class="circle.color"
        :style="{
          left: circle.x + '%',
          top: circle.y + '%',
          width: circle.size + 'px',
          height: circle.size + 'px',
          animationDelay: circle.delay + 's',
          animationDuration: circle.duration + 's'
        }"
      ></div>
      
      <!-- 漂浮方形 -->
      <div 
        v-for="(square, index) in floatingSquares" 
        :key="`square-${index}`"
        class="absolute opacity-8 animate-pulse transform"
        :class="[square.color, square.rotation]"
        :style="{
          left: square.x + '%',
          top: square.y + '%',
          width: square.size + 'px',
          height: square.size + 'px',
          animationDelay: square.delay + 's',
          animationDuration: square.duration + 's'
        }"
      ></div>
      
      <!-- 粒子效果 -->
      <div class="absolute inset-0">
        <div 
          v-for="(particle, index) in particles" 
          :key="`particle-${index}`"
          class="absolute rounded-full animate-float"
          :class="particle.color"
          :style="{
            left: particle.x + '%',
            top: particle.y + '%',
            width: particle.size + 'px',
            height: particle.size + 'px',
            animationDelay: particle.delay + 's',
            animationDuration: particle.duration + 's'
          }"
        ></div>
      </div>
    </div>
    
    <!-- 主内容 -->
    <div class="relative z-10 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-lg w-full space-y-8">
        <!-- Logo/Header -->
        <div class="text-center mb-8 animate-fade-in-up">
          <div class="bg-brutal-yellow border-4 border-blue-600 shadow-brutal p-8 transform -rotate-1 mb-6 hover:rotate-0 transition-transform duration-300">
            <h1 class="text-5xl font-black text-gray-800 uppercase tracking-tight">
              CODEUP
            </h1>
            <div class="text-xl font-bold text-gray-800 mt-2">
              活动助手
            </div>
          </div>
          <div class="bg-brutal-pink border-4 border-blue-600 shadow-brutal-sm p-4 transform rotate-1 hover:-rotate-1 transition-transform duration-300">
            <p class="text-lg font-bold text-gray-800 uppercase">
              请输入您的 Cookies 登录
            </p>
          </div>
        </div>
        
        <div class="bg-white/90 backdrop-blur-sm border-4 border-blue-600 shadow-brutal-lg p-8 animate-fade-in-up animate-delay-200">
          <form class="space-y-8" @submit.prevent="handleLogin">
            <div>
              <label for="cookies" class="block text-xl font-black text-gray-800 uppercase mb-4">
                CODEUP COOKIES
              </label>
              <textarea
                id="cookies"
                v-model="cookies"
                required
                rows="5"
                placeholder="请粘贴完整的 Codeup 网站 Cookies 字符串..."
                :disabled="loading"
                class="w-full border-4 border-blue-600 p-4 font-bold text-sm focus:outline-none focus:bg-brutal-yellow transition-colors disabled:cursor-not-allowed disabled:opacity-50 resize-vertical min-h-24"
              />
              <div class="mt-3 bg-brutal-cyan border-2 border-blue-600 p-3 flex items-center justify-between">
                <p class="text-sm font-bold text-gray-800 flex-1">
                  从浏览器开发者工具中复制完整的 Cookies 字符串
                </p>
                <button 
                  @click="showHelp = !showHelp"
                  class="ml-3 w-8 h-8 bg-blue-600 text-white rounded-full font-bold hover:bg-blue-700 transition-colors flex items-center justify-center"
                  type="button"
                >
                  ?
                </button>
              </div>
            </div>

            <div v-if="error" class="bg-brutal-red border-4 border-blue-600 shadow-brutal p-4">
              <div class="text-center">
                <h3 class="text-lg font-black text-gray-800 uppercase mb-2">
                  登录失败
                </h3>
                <div class="text-sm font-bold text-gray-800">
                  {{ error }}
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                :disabled="loading || !cookies.trim()"
                class="w-full bg-brutal-green border-4 border-blue-600 shadow-brutal px-8 py-4 font-black text-gray-800 text-lg uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:bg-gray-200 disabled:cursor-not-allowed"
              >
                <span v-if="loading">登录中...</span>
                <span v-else>LOGIN</span>
              </button>
            </div>
          </form>
        </div>

        <!-- 帮助提示模态框 -->
        <div 
          v-if="showHelp" 
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
          @click.self="showHelp = false"
        >
          <div class="bg-white border-4 border-blue-600 shadow-brutal-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto animate-scale-in">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-2xl font-black text-gray-800 uppercase">📚 获取 Cookies 步骤</h3>
              <button 
                @click="showHelp = false"
                class="w-8 h-8 bg-red-500 text-white rounded-full font-bold hover:bg-red-600 transition-colors flex items-center justify-center"
              >
                ×
              </button>
            </div>
            
            <div class="space-y-4">
              <div 
                v-for="(step, index) in helpSteps" 
                :key="index"
                class="bg-brutal-orange border-2 border-blue-600 p-4 transform hover:scale-105 transition-transform cursor-pointer"
                :class="{
                  'rotate-1': index % 2 === 0,
                  '-rotate-1': index % 2 === 1
                }"
              >
                <div class="flex items-start">
                  <span class="bg-blue-600 text-white px-3 py-1 text-sm font-black mr-4 flex-shrink-0 rounded">{{ index + 1 }}</span>
                  <div>
                    <h4 class="font-bold text-gray-800 mb-1">{{ step.title }}</h4>
                    <p class="text-sm text-gray-700">{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-6 bg-brutal-yellow border-2 border-blue-600 p-4 transform rotate-1">
              <div class="font-black text-gray-800 text-sm">
                <span class="text-base">提示：</span> Cookie 格式类似：<br>
                <code class="bg-blue-600 text-brutal-cyan px-2 py-1 mt-2 inline-block rounded">key1=value1; key2=value2; login_ticket=xxxxx;</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const cookies = ref('')
const loading = ref(false)
const error = ref('')
const showHelp = ref(false)

// 动画元素数据
const floatingCircles = ref([])
const floatingSquares = ref([])
const particles = ref([])

// 帮助步骤数据
const helpSteps = ref([
  {
    title: '登录 Codeup 网站',
    description: '在浏览器中打开并登录 Codeup 网站，确保已经成功登录'
  },
  {
    title: '打开开发者工具',
    description: '按 F12 键或右键选择"检查元素"打开浏览器开发者工具'
  },
  {
    title: '切换到网络标签',
    description: '在开发者工具中点击"Network"（网络）标签页'
  },
  {
    title: '刷新页面并选择请求',
    description: '刷新当前页面，然后在网络请求列表中选择任意一个请求'
  },
  {
    title: '查找 Cookie 字段',
    description: '在请求详情的"Request Headers"部分找到"Cookie"字段'
  },
  {
    title: '复制 Cookie 值',
    description: '复制完整的 Cookie 值并粘贴到上方的输入框中'
  }
])

// 初始化动画元素
const initAnimationElements = () => {
  // 生成漂浮圆形
  floatingCircles.value = Array.from({ length: 10 }, (_, i) => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 60 + 30,
    color: ['bg-blue-200', 'bg-indigo-200', 'bg-gray-200', 'bg-slate-200'][Math.floor(Math.random() * 4)],
    delay: Math.random() * 5,
    duration: Math.random() * 3 + 4
  }))

  // 生成漂浮方形
  floatingSquares.value = Array.from({ length: 6 }, (_, i) => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 40 + 20,
    color: ['bg-blue-100', 'bg-indigo-100', 'bg-gray-100', 'bg-slate-100'][Math.floor(Math.random() * 4)],
    rotation: ['rotate-12', 'rotate-45', '-rotate-12', '-rotate-45'][Math.floor(Math.random() * 4)],
    delay: Math.random() * 3,
    duration: Math.random() * 4 + 3
  }))

  // 生成小粒子
  particles.value = Array.from({ length: 15 }, (_, i) => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 6 + 3,
    color: ['bg-blue-300', 'bg-indigo-300', 'bg-slate-300', 'bg-gray-300'][Math.floor(Math.random() * 4)],
    delay: Math.random() * 5,
    duration: Math.random() * 6 + 4
  }))
}

const handleLogin = async () => {
  if (!cookies.value.trim()) {
    error.value = '请输入 Codeup Cookies'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await authStore.loginWithCookies(cookies.value.trim())
    
    if (result.success) {
      await router.push('/projects')
    } else {
      error.value = result.error || '登录失败，请检查 Cookies 是否正确或包含有效的 login_ticket'
    }
  } catch (err) {
    error.value = '登录过程中发生错误，请稍后重试'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initAnimationElements()
})
</script>