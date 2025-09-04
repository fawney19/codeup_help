import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import { authApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  const cookies = ref(Cookies.get('codeup_cookies') || null)

  // 设置 cookies
  const setCookies = (cookieString) => {
    cookies.value = cookieString
    Cookies.set('codeup_cookies', cookieString, { expires: 30 }) // 30天过期
  }


  // 使用Cookies登录
  const loginWithCookies = async (cookieString) => {
    try {
      const response = await authApi.loginWithCookies(cookieString)
      if (response.status === 'success') {
        user.value = response.data.user
        setCookies(response.data.cookies) // 保存完整的cookies
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Cookie login failed:', error)
      return { success: false, error: error.response?.data?.message || 'Cookie登录失败' }
    }
  }

  // 获取用户信息
  const fetchUser = async () => {
    try {
      const response = await authApi.getCurrentUser()
      if (response.status === 'success') {
        user.value = response.data
        return { success: true, data: response.data }
      }
      return { success: false, error: response.message }
    } catch (error) {
      console.error('Fetch user failed:', error)
      logout() // 清除无效状态
      return { success: false, error: error.response?.data?.message || '获取用户信息失败' }
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    cookies.value = null
    Cookies.remove('codeup_cookies')
  }

  // 初始化时检查登录状态
  const checkAuth = async () => {
    if (cookies.value && !user.value) {
      await fetchUser()
    }
  }

  return {
    user,
    isAuthenticated,
    cookies,
    loginWithCookies,
    logout,
    fetchUser,
    checkAuth
  }
})