<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import type { RegisteredUser } from '@/types'
import axios from 'axios'
import { BCard, BTable, BSpinner, BAlert, BBadge } from 'bootstrap-vue-next'

const users = ref<RegisteredUser[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)

const fetchUsers = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await axios.get('/api/admin/users')
    users.value = response.data
  } catch (err) {
    console.error('Failed to fetch users:', err)
    error.value = 'Could not load registered users. Please try again later.'
  } finally {
    isLoading.value = false
  }
}
onMounted(fetchUsers)

const fields = [
  { key: 'id', label: 'ID', class: 'text-center' },
  { key: 'userInfo', label: 'User' },
  { key: 'locationInfo', label: 'Location' },
  { key: 'activeBookings', label: 'Bookings', class: 'text-center' },
  { key: 'totalSpent', label: 'Total Spent', class: 'text-end' },
]
</script>

<template>
  <div class="users-view">
    <h1 class="page-title mb-4">Registered User Overview</h1>

    <!-- Loading, Error, Empty states are unchanged -->
    <div v-if="isLoading" class="text-center py-5">...</div>
    <BAlert v-else-if="error" show variant="danger" class="text-center">{{ error }}</BAlert>
    <BCard v-else-if="users.length === 0" class="table-card empty-state text-center">...</BCard>

    <!-- Updated Table -->
    <BCard v-else no-body class="table-card">
      <BTable
        :items="users"
        :fields="fields"
        responsive
        borderless
        hover
        tbody-tr-class="table-row-transition"
      >
        <!-- Custom Cell for User Info -->
        <template #cell(userInfo)="data">
          <div class="user-info-cell">
            <div class="user-name">{{ data.item.fullName || 'N/A' }}</div>
            <div class="user-email">{{ data.item.email }}</div>
          </div>
        </template>

        <!-- Custom Cell for Location Info -->
        <template #cell(locationInfo)="data">
          <div>{{ data.item.address || 'N/A' }}</div>
          <div class="pin-code">{{ data.item.pinCode || 'N/A' }}</div>
        </template>

        <!-- Custom Cell for Active Bookings -->
        <template #cell(activeBookings)="data">
          <BBadge :variant="data.item.activeBookings > 0 ? 'success' : 'secondary'" pill>
            {{ data.item.activeBookings }} Active
          </BBadge>
          <div class="total-bookings-text">{{ data.item.totalBookings }} Total</div>
        </template>

        <!-- Custom Cell for Total Spent -->
        <template #cell(totalSpent)="data">
          <span class="amount-spent">${{ data.item.totalSpent.toFixed(2) }}</span>
        </template>
      </BTable>
    </BCard>
  </div>
</template>

<style scoped>
.users-view {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.page-title {
  color: var(--text-color);
  font-weight: 600;
}

.table-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  overflow: hidden;
}

:deep(.table) {
  color: var(--text-color-muted) !important;
  background-color: transparent !important;
  margin-bottom: 0;
}

:deep(thead) {
  border-bottom: 2px solid var(--highlight-color);
}

:deep(th) {
  color: var(--text-color) !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  padding: 1rem 1.5rem !important;
  background-color: transparent !important;
  border-bottom: none !important;
}

:deep(td) {
  padding: 1rem 1.5rem !important;
  vertical-align: middle;
  border-color: var(--input-border) !important;
  background-color: transparent !important;
  color: var(--text-color) !important;
}

:deep(tbody tr),
:deep(.table-striped > tbody > tr:nth-of-type(odd) > *),
:deep(.table-striped > tbody > tr:nth-of-type(even) > *) {
  background-color: transparent !important;
  color: var(--text-color-muted) !important;
  border-color: var(--input-border) !important;
  transition: background-color 0.2s ease-in-out;
}

:deep(tbody tr:hover),
:deep(.table-hover > tbody > tr:hover > *) {
  background-color: rgba(32, 201, 151, 0.08) !important;
  color: var(--text-color) !important;
}

.user-name {
  color: var(--text-color);
  font-weight: 600;
}
.user-email {
  font-size: 0.85rem;
  color: inherit;
}
.pin-code {
  font-size: 0.85rem;
  font-family: monospace;
  color: inherit;
}
.total-bookings-text {
  font-size: 0.8rem;
  margin-top: 0.25rem;
  color: inherit;
}
.amount-spent {
  font-weight: 600;
  color: var(--highlight-color);
  font-size: 1.05rem;
}

:deep(.badge) {
  --bs-badge-font-size: 0.8em;
  --bs-badge-font-weight: 600;
  --bs-badge-padding-x: 0.8em;
  --bs-badge-padding-y: 0.4em;
}
:deep(.badge.bg-success) {
  background-color: rgba(40, 167, 69, 0.3) !important;
  color: var(--highlight-color) !important;
}
:deep(.badge.bg-secondary) {
  background-color: var(--input-bg) !important;
  color: var(--text-color-muted) !important;
}

.empty-state {
  padding: 3rem;
}
.empty-state i {
  color: var(--input-border);
}

:deep(.text-center) {
  text-align: center;
}
:deep(.text-end) {
  text-align: end;
}
</style>
