<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import type { UserSummaryData } from '@/types'
import axios from 'axios'
import { BRow, BCol, BCard, BAlert } from 'bootstrap-vue-next'
import StatCard from '@/components/StatCard.vue' // A new reusable component
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const summaryData = ref<UserSummaryData | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const response = await axios.get('/api/summary')
    summaryData.value = response.data
  } catch (err) {
    error.value = 'Failed to load summary data.'
  } finally {
    isLoading.value = false
  }
})

const chartOptions = {
  responsive: !false,
  maintainAspectRatio: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: 'rgba(224, 224, 224, 0.7)' } },
    y: { ticks: { color: 'rgba(224, 224, 224, 0.7)' } },
  },
}

const monthlyChartData = computed(() => {
  if (!summaryData.value) return null
  const labels = summaryData.value.monthlySpending.map((d) =>
    new Date(d.month + '-02').toLocaleString('default', { month: 'short', year: '2-digit' }),
  )
  const data = summaryData.value.monthlySpending.map((d) => d.total)
  return {
    labels,
    datasets: [
      {
        label: 'Total Spent',
        backgroundColor: 'rgba(32, 201, 151, 0.6)',
        borderColor: 'rgba(32, 201, 151, 1)',
        borderWidth: 1,
        borderRadius: 4,
        data,
      },
    ],
  }
})

const dayOfWeekChartData = computed(() => {
  if (!summaryData.value) return null
  const labels = Object.keys(summaryData.value.dayOfWeekParking)
  const data = Object.values(summaryData.value.dayOfWeekParking)
  return {
    labels,
    datasets: [
      {
        backgroundColor: [
          '#20c997',
          '#28a745',
          '#17a2b8',
          '#fd7e14',
          '#ffc107',
          '#6f42c1',
          '#dc3545',
        ],
        data,
      },
    ],
  }
})
</script>

<template>
  <div class="summary-view">
    <h1 class="page-title mb-4">My Parking Summary</h1>

    <div v-if="isLoading" class="text-center py-5">...</div>
    <BAlert v-else-if="error" show variant="danger">{{ error }}</BAlert>
    <div v-else-if="summaryData">
      <!-- KPI Cards -->
      <BRow class="g-4 mb-4">
        <BCol md="6" lg="3"
          ><StatCard icon="bi-stack" :value="summaryData.kpis.totalSessions" label="Total Sessions"
        /></BCol>
        <BCol md="6" lg="3"
          ><StatCard
            icon="bi-wallet2"
            :value="`$${summaryData.kpis.totalSpent.toFixed(2)}`"
            label="Total Spent"
        /></BCol>
        <BCol md="6" lg="3"
          ><StatCard
            icon="bi-pie-chart-fill"
            :value="`$${summaryData.kpis.avgCost.toFixed(2)}`"
            label="Avg. Cost / Session"
        /></BCol>
        <BCol md="6" lg="3"
          ><StatCard
            icon="bi-heart-fill"
            :value="summaryData.favoriteLot.name"
            :label="`Favorite Lot (${summaryData.favoriteLot.visits} visits)`"
        /></BCol>
      </BRow>

      <!-- Charts -->
      <BRow class="g-4">
        <BCol lg="8">
          <BCard class="chart-card">
            <h5 class="chart-title">Spending per Month (Last 6 Months)</h5>
            <Bar
              class="w-100"
              v-if="monthlyChartData"
              :data="monthlyChartData"
              :options="chartOptions"
            />
          </BCard>
        </BCol>
        <BCol lg="4">
          <BCard class="chart-card">
            <h5 class="chart-title">Parking by Day of Week</h5>
            <Doughnut class="w-100" v-if="dayOfWeekChartData" :data="dayOfWeekChartData" />
          </BCard>
        </BCol>
      </BRow>
    </div>
  </div>
</template>

<style scoped>
.summary-view {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.page-title {
  color: var(--text-color);
  font-weight: 600;
}
.chart-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  padding: 1.5rem;
  /* height: 500px; */
}
.chart-title {
  color: var(--text-color-muted);
  margin-bottom: 1.5rem;
}
</style>
