<template>
  <div v-if="reportData" ref="reportContainer" class="space-y-6">
    <!-- 开发者信息卡片 -->
    <div class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal p-6 transform rotate-1 hover:-rotate-1 transition-transform duration-300">
      <div class="mb-4">
        <h3 class="text-xl font-black text-gray-800 uppercase flex items-center">
          <User class="w-5 h-5 mr-2 text-blue-600" />
          开发者信息
        </h3>
      </div>
      <div class="space-y-2">
        <div class="flex items-center">
          <span class="bg-blue-600 text-white px-2 py-1 text-sm font-bold rounded mr-3">姓名</span>
          <span class="text-lg font-bold text-gray-800">{{ reportData.developer }}</span>
        </div>
        <div class="flex items-center">
          <span class="bg-blue-600 text-white px-2 py-1 text-sm font-bold rounded mr-3">岗位</span>
          <span class="text-lg font-bold text-gray-800">{{ reportData.position }}</span>
        </div>
      </div>
    </div>

    <!-- 工作完成情况卡片 -->
    <div class="bg-brutal-yellow border-4 border-blue-600 shadow-brutal p-6 transform -rotate-1 hover:rotate-1 transition-transform duration-300">
      <div class="flex justify-between items-start mb-4">
        <h3 class="text-xl font-black text-gray-800 uppercase flex items-center">
          <CheckCircle2 class="w-5 h-5 mr-2 text-blue-600" />
          本周工作完成情况
        </h3>
        <button 
          @click="copySection('workSummary')"
          class="bg-brutal-green border-2 border-blue-600 shadow-brutal-sm px-3 py-1 font-bold text-gray-800 text-xs uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <Copy class="w-3 h-3 mr-1 inline" />
          复制
        </button>
      </div>
      <div class="bg-white border-2 border-blue-600 p-4 rounded">
        <div 
          class="whitespace-pre-wrap text-gray-800 text-sm leading-relaxed"
          v-html="formatWorkSummary(reportData.work_summary)"
        ></div>
      </div>
    </div>

    <!-- 下周工作计划卡片 -->
    <div class="bg-brutal-pink border-4 border-blue-600 shadow-brutal p-6 transform rotate-1 hover:-rotate-1 transition-transform duration-300">
      <div class="flex justify-between items-start mb-4">
        <h3 class="text-xl font-black text-gray-800 uppercase flex items-center">
          <Calendar class="w-5 h-5 mr-2 text-blue-600" />
          下周工作计划
        </h3>
        <button 
          @click="copySection('nextPlan')"
          class="bg-brutal-green border-2 border-blue-600 shadow-brutal-sm px-3 py-1 font-bold text-gray-800 text-xs uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <Copy class="w-3 h-3 mr-1 inline" />
          复制
        </button>
      </div>
      <div class="bg-white border-2 border-blue-600 p-4 rounded">
        <ul class="space-y-2">
          <li 
            v-for="(plan, index) in reportData.next_plan" 
            :key="index"
            class="flex items-start"
          >
            <span class="bg-blue-600 text-white w-6 h-6 flex items-center justify-center text-xs font-bold rounded-full mr-3 mt-0.5 flex-shrink-0">
              {{ index + 1 }}
            </span>
            <span class="text-gray-800 text-sm leading-relaxed">{{ plan }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- 完整报告复制 -->
    <div class="bg-brutal-orange border-4 border-blue-600 shadow-brutal p-6 text-center transform -rotate-1 hover:rotate-0 transition-transform duration-300">
      <h3 class="text-xl font-black text-gray-800 uppercase mb-4 flex items-center justify-center">
        <FileText class="w-5 h-5 mr-2 text-blue-600" />
        完整报告操作
      </h3>
      <div class="flex justify-center space-x-4">
        <button 
          @click="copyFullReport()"
          class="bg-brutal-green border-4 border-blue-600 shadow-brutal px-4 py-2 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <Copy class="w-4 h-4 mr-2 inline" />
          复制完整报告
        </button>
        <button 
          @click="downloadReport()"
          class="bg-brutal-cyan border-4 border-blue-600 shadow-brutal px-4 py-2 font-black text-gray-800 uppercase hover:transform hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <Download class="w-4 h-4 mr-2 inline" />
          下载报告(MD)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  User, 
  CheckCircle2, 
  Calendar, 
  FileText, 
  Copy, 
  Download
} from 'lucide-vue-next'
import { ref } from 'vue'

const reportContainer = ref(null)

const props = defineProps({
  reportData: {
    type: Object,
    required: true
  },
  projectName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['showToast'])

// 格式化工作总结，支持多种格式
const formatWorkSummary = (workSummary) => {
  if (!workSummary) return ''
  
  // 将工作总结按行分割，然后格式化
  return workSummary
    .split('\n')
    .map(line => {
      const trimmedLine = line.trim()
      
      // 跳过空行
      if (!trimmedLine) return ''
      
      // 识别日期标题行（多种格式）
      // 支持: ## 2025年9月1日 星期一 或者 2025年9月1日 星期一
      if (trimmedLine.match(/^(##\s+)?\d{4}年\d{1,2}月\d{1,2}日.*星期[一二三四五六日]/)) {
        const dateText = trimmedLine.replace(/^##\s*/, '').trim()
        return `<div class="bg-blue-600 text-white px-3 py-1 rounded font-bold text-sm mb-3 mt-4 first:mt-0 inline-block">${dateText}</div>`
      }
      
      // 识别数字列表项 (1. 内容)
      if (trimmedLine.match(/^\d+\.\s+/)) {
        const number = trimmedLine.match(/^(\d+)/)[1]
        const content = trimmedLine.replace(/^\d+\.\s+/, '')
        return `<div class="ml-4 mb-2 flex items-start">
          <span class="bg-brutal-green text-gray-800 w-6 h-6 flex items-center justify-center text-xs font-bold rounded-full mr-3 mt-0.5 flex-shrink-0">${number}</span>
          <span class="text-gray-800 leading-relaxed">${content}</span>
        </div>`
      }
      
      // 识别无序列表项 (- 内容 或 • 内容)
      if (trimmedLine.match(/^[-•]\s+/)) {
        const content = trimmedLine.replace(/^[-•]\s+/, '')
        return `<div class="ml-4 mb-2 flex items-start">
          <span class="bg-brutal-cyan text-gray-800 w-4 h-4 flex items-center justify-center text-xs font-bold rounded-full mr-3 mt-1 flex-shrink-0">•</span>
          <span class="text-gray-800 leading-relaxed">${content}</span>
        </div>`
      }
      
      // 识别标题行（以 # 开始）
      if (trimmedLine.match(/^#+\s+/)) {
        const level = (trimmedLine.match(/^#+/)[0]).length
        const content = trimmedLine.replace(/^#+\s+/, '')
        const fontSize = level === 1 ? 'text-lg' : level === 2 ? 'text-base' : 'text-sm'
        return `<div class="font-bold ${fontSize} text-gray-900 mt-3 mb-2">${content}</div>`
      }
      
      // 普通文本行
      return `<div class="mb-2 text-gray-800 leading-relaxed">${trimmedLine}</div>`
    })
    .filter(html => html) // 过滤掉空字符串
    .join('')
}

// 将工作总结转换为纯文本
const convertToPlainText = (text) => {
  if (!text) return ''
  
  return text
    .split('\n')
    .map(line => {
      const trimmedLine = line.trim()
      if (!trimmedLine) return ''
      
      // 移除markdown标记，保留内容
      return trimmedLine
        .replace(/^##\s*/, '') // 移除二级标题标记
        .replace(/^#+\s*/, '') // 移除其他标题标记
        .replace(/^\d+\.\s*/, (match) => match) // 保留数字列表
        .replace(/^[-•]\s*/, '• ') // 统一无序列表标记
    })
    .filter(line => line) // 移除空行
    .join('\n')
}

// 复制指定部分
const copySection = async (section) => {
  let content = ''
  
  switch (section) {
    case 'developer':
      content = `姓名：${props.reportData.developer}\n岗位：${props.reportData.position}`
      break
    case 'workSummary':
      const plainWorkSummary = convertToPlainText(props.reportData.work_summary)
      content = `本周工作完成情况：\n\n${plainWorkSummary}`
      break
    case 'nextPlan':
      content = `下周工作计划：\n\n${props.reportData.next_plan.map((plan, index) => `${index + 1}. ${plan}`).join('\n')}`
      break
  }
  
  try {
    // 检查clipboard API是否可用
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(content)
      emit('showToast', '内容已复制到剪贴板')
    } else {
      // 降级方案：使用旧的execCommand方法
      const textArea = document.createElement('textarea')
      textArea.value = content
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        const successful = document.execCommand('copy')
        document.body.removeChild(textArea)
        if (successful) {
          emit('showToast', '内容已复制到剪贴板')
        } else {
          throw new Error('execCommand failed')
        }
      } catch (fallbackError) {
        document.body.removeChild(textArea)
        console.error('降级复制方法也失败:', fallbackError)
        emit('showToast', '复制失败，请手动选择并复制内容')
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    // 提供更详细的错误信息
    if (error.name === 'NotAllowedError') {
      emit('showToast', '复制权限被拒绝，请允许网站访问剪贴板')
    } else {
      emit('showToast', `复制失败: ${error.message}`)
    }
  }
}

// 复制完整报告（纯文本格式）
const copyFullReport = async () => {
  // 将工作总结转换为纯文本
  const plainWorkSummary = convertToPlainText(props.reportData.work_summary)
  
  const fullReport = `项目活动报告${props.projectName ? ` - ${props.projectName}` : ''}
生成时间：${new Date().toLocaleString('zh-CN')}

================================

开发者信息：
姓名：${props.reportData.developer}
岗位：${props.reportData.position}

本周工作完成情况：
${plainWorkSummary}

下周工作计划：
${props.reportData.next_plan.map((plan, index) => `${index + 1}. ${plan}`).join('\n')}

================================
报告生成时间：${new Date().toLocaleString('zh-CN')}`

  try {
    // 检查clipboard API是否可用
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(fullReport)
      emit('showToast', '完整报告已复制到剪贴板')
    } else {
      // 降级方案：使用旧的execCommand方法
      const textArea = document.createElement('textarea')
      textArea.value = fullReport
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        const successful = document.execCommand('copy')
        document.body.removeChild(textArea)
        if (successful) {
          emit('showToast', '完整报告已复制到剪贴板')
        } else {
          throw new Error('execCommand failed')
        }
      } catch (fallbackError) {
        document.body.removeChild(textArea)
        console.error('降级复制方法也失败:', fallbackError)
        emit('showToast', '复制失败，请手动选择并复制内容')
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    if (error.name === 'NotAllowedError') {
      emit('showToast', '复制权限被拒绝，请允许网站访问剪贴板')
    } else {
      emit('showToast', `复制失败: ${error.message}`)
    }
  }
}

// 下载报告
const downloadReport = () => {
  const fullReport = `项目活动报告${props.projectName ? ` - ${props.projectName}` : ''}
生成时间：${new Date().toLocaleString('zh-CN')}

================================

开发者信息：
姓名：${props.reportData.developer}
岗位：${props.reportData.position}

本周工作完成情况：
${props.reportData.work_summary}

下周工作计划：
${props.reportData.next_plan.map((plan, index) => `${index + 1}. ${plan}`).join('\n')}

================================
报告生成时间：${new Date().toLocaleString('zh-CN')}`

  const blob = new Blob([fullReport], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `工作报告_${props.reportData.developer}_${new Date().toISOString().split('T')[0]}.txt`
  link.click()
  URL.revokeObjectURL(url)
  
  emit('showToast', '报告已下载')
}
</script>