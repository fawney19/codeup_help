import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/projects',
      name: 'Projects',
      component: () => import('@/views/ProjectList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects/:id/:name?',
      name: 'ProjectDetail',
      component: () => import('@/views/ProjectDetail.vue'),
      meta: { requiresAuth: true },
      props: true
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 检查登录状态
  if (authStore.cookies && !authStore.user) {
    await authStore.checkAuth()
  }
  
  // 需要认证的路由
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
  }
  
  // 已登录用户访问登录页面时重定向到项目页面
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next('/projects')
    return
  }
  
  next()
})

export default router