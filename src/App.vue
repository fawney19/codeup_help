<template>
  <router-view />
</template>

<script setup>
import { onBeforeUnmount } from 'vue'
import { useProjectsStore } from '@/stores/projects'

// 页面卸载时清理缓存
onBeforeUnmount(() => {
  const projectsStore = useProjectsStore()
  projectsStore.clearData()
})

// 页面刷新前清理缓存
window.addEventListener('beforeunload', () => {
  const projectsStore = useProjectsStore()
  projectsStore.clearData()
})
</script>
