<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import type { AdminSummaryData } from '@/types'
import axios from 'axios'
import { BRow, BCol, BCard, BAlert, BListGroup, BListGroupItem, BBadge } from 'bootstrap-vue-next'
import StatCard from '@/components/StatCard.vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
)

const summaryData = ref<AdminSummaryData | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const response = await axios.get('/api/admin/summary')
    summaryData.value = response.data
  } catch (err) {
    error.value = 'Failed to load summary data.'
  } finally {
    isLoading.value = false
  }
})

const chartOptions = {
  line: {
    responsive: false,
    maintainAspectRatio: true,
    aspectRatio: 4,
    plugins: { legend: { display: false } } /* ... scales ... */,
  },
  bar: {
    responsive: false,
    maintainAspectRatio: true,
    aspectRatio: 4,
    plugins: { legend: { labels: { color: 'rgba(224, 224, 224, 0.7)' } } },
    scales: { x: { stacked: true }, y: { stacked: true } },
  },
}

const dailyRevenueChartData = computed(() => {
  if (!summaryData.value) return null
  const labels = summaryData.value.dailyRevenue.map((d) =>
    new Date(d.day).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
  )
  const data = summaryData.value.dailyRevenue.map((d) => d.total)
  return {
    labels,
    datasets: [
      {
        label: 'Revenue',
        backgroundColor: 'rgba(32, 201, 151, 0.2)',
        borderColor: 'rgba(32, 201, 151, 1)',
        pointBackgroundColor: 'rgba(32, 201, 151, 1)',
        fill: true,
        data,
      },
    ],
  }
})

const occupancyByLotChartData = computed(() => {
  if (!summaryData.value) return null
  const labels = summaryData.value.occupancyByLot.map((d) => d.name)
  return {
    labels,
    datasets: [
      {
        label: 'Occupied',
        data: summaryData.value.occupancyByLot.map((d) => d.occupied),
        backgroundColor: 'rgba(220, 53, 69, 0.7)',
      },
      {
        label: 'Available',
        data: summaryData.value.occupancyByLot.map((d) => d.available),
        backgroundColor: 'rgba(40, 167, 69, 0.6)',
      },
    ],
  }
})
</script>

<template>
  <div class="summary-view">
    <h1 class="page-title mb-4">Admin Dashboard Summary</h1>

    <div v-if="isLoading" class="text-center py-5">...</div>
    <BAlert v-else-if="error" show variant="danger">{{ error }}</BAlert>
    <div v-else-if="summaryData">
      <!-- KPI Cards -->
      <BRow class="g-4 mb-4">
        <BCol
          ><StatCard icon="bi-p-circle-fill" :value="summaryData.kpis.totalLots" label="Total Lots"
        /></BCol>
        <BCol
          ><StatCard
            icon="bi-people-fill"
            :value="summaryData.kpis.totalUsers"
            label="Registered Users"
        /></BCol>
        <BCol
          ><StatCard
            icon="bi-bar-chart-steps"
            :value="`${summaryData.kpis.liveOccupancyPercent.toFixed(1)}%`"
            label="Live Occupancy"
        /></BCol>
        <BCol
          ><StatCard
            icon="bi-cash-coin"
            :value="`$${summaryData.kpis.totalRevenue.toFixed(2)}`"
            label="Total Revenue"
        /></BCol>
        <BCol
          ><StatCard
            icon="bi-grid-1x2-fill"
            :value="summaryData.kpis.totalSpots"
            label="Total Spots"
        /></BCol>
      </BRow>

      <!-- Charts & Lists -->
      <BRow class="g-4">
        <BCol xl="8">
          <BCard class="chart-card">
            <h5 class="chart-title">Daily Revenue (Last 30 Days)</h5>
            <Line
              v-if="dailyRevenueChartData"
              class="w-100"
              :data="dailyRevenueChartData"
              :options="chartOptions.line"
            />
          </BCard>
        </BCol>
        <BCol xl="4">
          <BCard class="list-card">
            <h5 class="chart-title">Top 5 Active Lots</h5>
            <BListGroup flush>
              <BListGroupItem
                v-for="lot in summaryData.topLots"
                :key="lot.id"
                class="d-flex justify-content-between align-items-center"
              >
                <span>{{ lot.name }}</span>
                <BBadge pill>{{ lot.booking_count }} bookings</BBadge>
              </BListGroupItem>
            </BListGroup>
          </BCard>
        </BCol>
        <BCol xl="12">
          <BCard class="chart-card">
            <h5 class="chart-title">Live Occupancy by Lot</h5>
            <Bar
              v-if="occupancyByLotChartData"
              class="w-100"
              :data="occupancyByLotChartData"
              :options="chartOptions.bar"
            />
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
.chart-card,
.list-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  padding: 1.5rem;
  /* height: 450px; */
}
.chart-title {
  color: var(--text-color-muted);
  margin-bottom: 1.5rem;
}

.list-card .list-group-item {
  background-color: transparent;
  border-color: var(--input-border);
  color: var(--text-color);
}
.list-card .list-group-item:first-child {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
