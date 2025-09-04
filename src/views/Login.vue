<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Codeup 活动助手
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          请输入您的 Codeup Cookies 登录
        </p>
      </div>
      
      <div class="rounded-lg border bg-white shadow-sm p-8">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="cookies" class="block text-sm font-medium text-gray-700 mb-2">
              Codeup Cookies
            </label>
            <textarea
              id="cookies"
              v-model="cookies"
              required
              rows="4"
              placeholder="请粘贴完整的 Codeup 网站 Cookies 字符串..."
              :disabled="loading"
              class="flex w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-vertical min-h-20"
            />
            <p class="mt-1 text-xs text-gray-500">
              从浏览器开发者工具中复制完整的 Cookies 字符串
            </p>
          </div>

          <div v-if="error" class="rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">
                  登录失败
                </h3>
                <div class="mt-2 text-sm text-red-700">
                  {{ error }}
                </div>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading || !cookies.trim()"
              class="inline-flex w-full items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2"
            >
              <span v-if="loading">登录中...</span>
              <span v-else>登录</span>
            </button>
          </div>
        </form>

        <div class="mt-6 border-t pt-6">
          <h3 class="text-sm font-medium text-gray-900 mb-3">如何获取 Codeup Cookies:</h3>
          <ol class="text-xs text-gray-600 space-y-1 list-decimal list-inside">
            <li>在浏览器中登录 Codeup 网站</li>
            <li>按 F12 打开开发者工具</li>
            <li>转到 Network/网络 标签页</li>
            <li>刷新页面，选择任一请求</li>
            <li>在Request Headers中找到 "Cookie" 字段</li>
            <li>复制完整的 Cookie 值并粘贴到上方文本框</li>
          </ol>
          <div class="mt-3 p-2 bg-yellow-50 rounded text-xs text-yellow-700">
            <strong>提示：</strong>Cookie 格式类似：key1=value1; key2=value2; login_ticket=xxxxx; ...
          </div>
        </div>
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

const cookies = ref('')
const loading = ref(false)
const error = ref('')

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
      router.push('/projects')
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
</script>