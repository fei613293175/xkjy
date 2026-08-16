<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type Readiness = { status: 'ready' | 'not_ready'; release: string; dependencies: Record<string, 'ready' | 'unavailable'> }
const loading = ref(false)
const checkedAt = ref('尚未检查')
const error = ref('')
const liveness = ref<'ok' | 'unavailable'>('unavailable')
const readiness = ref<Readiness | null>(null)
const overallStatus = computed(() => readiness.value?.status === 'ready' && liveness.value === 'ok' ? '正常' : '待处理')
const dependencyRows = computed(() => [['API 进程', liveness.value === 'ok' ? 'ready' : 'unavailable'], ['PostgreSQL', readiness.value?.dependencies.postgres ?? 'unavailable'], ['Redis', readiness.value?.dependencies.redis ?? 'unavailable']])

async function refresh(): Promise<void> {
  loading.value = true; error.value = ''
  try {
    const [healthResponse, readyResponse] = await Promise.all([fetch('/api/healthz'), fetch('/api/readyz')])
    liveness.value = healthResponse.ok ? 'ok' : 'unavailable'; readiness.value = await readyResponse.json() as Readiness
    if (!healthResponse.ok || !readyResponse.ok) error.value = '服务已响应，但至少一项依赖尚未就绪。'
  } catch {
    liveness.value = 'unavailable'; readiness.value = null; error.value = '无法连接基线 API，请检查 Docker 服务和反向代理。'
  } finally {
    checkedAt.value = new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'medium', hour12: false }).format(new Date()); loading.value = false
  }
}
onMounted(refresh)
</script>

<template>
  <main class="shell">
    <aside class="sidebar" aria-label="后台导航"><div class="brand"><span class="brand-mark" aria-hidden="true"></span><span>星矿纪元</span></div><p class="release">P00 / 项目基线</p><nav><a class="nav-item active" href="#overview">运行概览</a><a class="nav-item" href="#boundaries">交付边界</a><a class="nav-item" href="#dependencies">服务依赖</a></nav><p class="sidebar-note">仅显示不含秘密值的运行状态。</p></aside>
    <section class="content">
      <header class="topbar"><div><p class="eyebrow">运维控制台</p><h1>项目基线</h1></div><button class="refresh" type="button" :disabled="loading" @click="refresh">{{ loading ? '刷新中' : '刷新状态' }}</button></header>
      <section id="overview" class="overview" aria-label="运行概览"><div class="metric"><p>整体状态</p><strong :class="overallStatus === '正常' ? 'healthy' : 'warning'">{{ overallStatus }}</strong></div><div class="metric"><p>当前发布</p><strong>{{ readiness?.release ?? 'P00' }}</strong></div><div class="metric"><p>最后检查</p><strong class="checked-at">{{ checkedAt }}</strong></div></section>
      <p v-if="error" class="alert" role="alert">{{ error }}</p>
      <section id="dependencies" class="section-block"><div class="section-heading"><div><p class="eyebrow">基础设施</p><h2>服务依赖</h2></div><span class="caption">来自 readyz</span></div><div class="table" role="table" aria-label="服务依赖状态"><div class="table-head" role="row"><span>组件</span><span>状态</span><span>说明</span></div><div v-for="row in dependencyRows" :key="row[0]" class="table-row" role="row"><span>{{ row[0] }}</span><span class="status" :class="row[1] === 'ready' ? 'status-ready' : 'status-unavailable'"><i aria-hidden="true"></i>{{ row[1] === 'ready' ? '就绪' : '不可用' }}</span><span>{{ row[1] === 'ready' ? '健康检查通过' : '等待服务恢复或检查配置' }}</span></div></div></section>
      <section id="boundaries" class="section-block boundaries"><div class="section-heading"><div><p class="eyebrow">P00 范围</p><h2>已建立的工程能力</h2></div></div><ul><li>Docker Compose、PostgreSQL 迁移、Redis、健康检查和结构化日志</li><li>Android Compose 诊断壳、V1.3.0 资源登记与截图差异门禁</li><li>Vue 运维壳与不含秘密值的基线状态接口</li></ul><p class="boundary-note">账号、游戏棋盘、项目、商城、支付、钱包、实名和提现均不属于 P00，未在此控制台中标记为已实现。</p></section>
    </section>
  </main>
</template>
