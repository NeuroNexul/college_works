<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import {
  BForm,
  BInputGroup,
  BFormSelect,
  BFormInput,
  BButton,
  BSpinner,
  BAlert,
  BCard,
  BTable,
} from 'bootstrap-vue-next'
import ParkingLotCard from '@/components/ParkingLotCard.vue' // Reuse the existing component
import type { ParkingLot, ParkingSpot } from '@/types'

const searchType = ref('lot')
const searchQuery = ref('')
const results = ref<any[]>([])
const hasSearched = ref(false)
const isLoading = ref(false)
const error = ref<string | null>(null)
const lastQuery = ref('')

const selectedLot = ref<ParkingLot | null>(null)
const selectedSpot = ref<ParkingSpot | null>(null)
const showSpotView = ref(false)

let debounceTimer: number | null = null
let abortController: AbortController | null = null

const searchOptions = [
  { value: 'lot', text: 'by Lot' },
  { value: 'user', text: 'by User' },
  { value: 'vehicle', text: 'by Vehicle No.' },
]

const userTableFields = [
  { key: 'fullName', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'address', label: 'Address' },
]

const searchPlaceholder = computed(() => {
  switch (searchType.value) {
    case 'user':
      return 'Enter user name or email...'
    case 'vehicle':
      return 'Enter vehicle number...'
    default:
      return 'Enter lot name, address, or pin code...'
  }
})

const executeSearch = async () => {
  if (!searchQuery.value.trim()) {
    results.value = []
    hasSearched.value = false // Go back to initial prompt if search is cleared
    return
  }

  isLoading.value = true
  hasSearched.value = true
  error.value = null
  lastQuery.value = searchQuery.value

  // 1. Abort any previous, ongoing request
  if (abortController) {
    abortController.abort()
  }
  // Create a new controller for the new request
  abortController = new AbortController()

  try {
    const response = await axios.get('/api/admin/search', {
      params: { type: searchType.value, q: searchQuery.value },
      signal: abortController.signal,
    })
    results.value = response.data
  } catch (err) {
    if (axios.isCancel(err)) {
      // This is not a real error, just a cancelled request. We can ignore it.
      console.log('Request canceled:', (err as Error).message)
    } else {
      // This is a real network or server error
      error.value = 'An error occurred during search.'
      results.value = []
    }
  } finally {
    isLoading.value = false
  }
}

watch([searchQuery, searchType], () => {
  // Clear the previous debounce timer
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  isLoading.value = true
  hasSearched.value = true

  // 3. Set a new timer. The search will only run after 400ms of inactivity.
  debounceTimer = window.setTimeout(() => {
    executeSearch()
  }, 400) // 400ms is a good debounce delay
})

const viewSpotModal = (lot: ParkingLot, spot: ParkingSpot) => {
  selectedLot.value = lot
  selectedSpot.value = spot // Reset selected spot
  showSpotView.value = true
}

const clearSearch = () => {
  searchQuery.value = ''
}
</script>

<template>
  <div class="search-view">
    <h1 class="page-title mb-4">Universal Search</h1>

    <!-- Search Input Form -->
    <div class="search-form mx-auto mb-5">
      <BInputGroup>
        <BFormSelect v-model="searchType" :options="searchOptions" class="search-type-select" />
        <BFormInput
          v-model="searchQuery"
          :placeholder="searchPlaceholder"
          class="search-input"
          autofocus
        />
        <!-- We can add a clear button for better UX -->
        <BButton v-if="searchQuery" @click="clearSearch" variant="link" class="clear-btn">
          <i class="bi bi-x-lg"></i>
        </BButton>
      </BInputGroup>
    </div>

    <!-- Results Section -->
    <div v-if="hasSearched">
      <h2 class="results-title">Search Results for "{{ lastQuery }}"</h2>

      <!-- Loading & Error States -->
      <div v-if="isLoading" class="text-center py-5">
        <BSpinner style="width: 3rem; height: 3rem"></BSpinner>
        <p class="mt-3">Searching...</p>
      </div>
      <BAlert v-else-if="error" show variant="danger">{{ error }}</BAlert>

      <!-- No Results State -->
      <div v-else-if="results.length === 0" class="empty-state text-center py-5">
        <i class="bi bi-binoculars-fill display-1"></i>
        <h3 class="mt-3">No Results Found</h3>
        <p class="text-color-muted">Your search did not match any records.</p>
      </div>

      <!-- Results Display -->
      <div v-else>
        <!-- For Lot or Vehicle Search -->
        <TransitionGroup
          v-if="searchType === 'lot' || searchType === 'vehicle'"
          name="lot-list"
          tag="div"
          class="row g-4"
        >
          <div v-for="lot in results" :key="lot.id" class="col-12 col-md-6 col-lg-4">
            <ParkingLotCard
              :lot="lot"
              class="searched-card"
              :highlighted-spot="lot.searched_vehicle?.spot_id"
              :is-editable="false"
              @view-spots="viewSpotModal"
            />
          </div>
        </TransitionGroup>

        <!-- For User Search -->
        <BCard v-if="searchType === 'user'" no-body class="table-card">
          <BTable :items="results" :fields="userTableFields" responsive borderless hover />
        </BCard>
      </div>
    </div>

    <!-- Initial Prompt -->
    <div v-else class="initial-prompt text-center py-5">
      <i class="bi bi-zoom-in display-1"></i>
      <h3 class="mt-3">Search the System</h3>
      <p class="text-color-muted">Select a category and enter a query to begin.</p>
    </div>
  </div>

  <BModal v-model="showSpotView" title="Parking Lot Spots" centered no-footer>
    <KeepAlive>
      <ParkingLotSpotView
        :key="selectedLot?.id"
        :lot="selectedLot"
        :spot="selectedSpot"
        :show-spot-view="showSpotView"
        @cancel="showSpotView = false"
    /></KeepAlive>
  </BModal>
</template>

<style scoped>
.search-view {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.page-title {
  color: var(--text-color);
  font-weight: 600;
}
.search-form {
  max-width: 800px;
}
.search-type-select {
  flex: 0 0 150px;
}
/* Input group styling from UserDashboard */
.search-input,
.input-group-text,
.form-select {
  background-color: var(--input-bg) !important;
  color: var(--text-color) !important;
  border: 1px solid var(--input-border) !important;
  padding: 0.75rem 1rem;
}
.search-input:focus,
.form-select:focus {
  box-shadow: 0 0 0 0.25rem rgba(32, 201, 151, 0.25);
  border-color: var(--highlight-color) !important;
}

.results-title {
  color: var(--text-color-muted);
  font-weight: 300;
  border-bottom: 1px solid var(--input-border);
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
.initial-prompt i,
.empty-state i {
  color: var(--input-border);
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

/* Card highlight for vehicle search */
.searched-card.highlighted {
  box-shadow: 0 0 25px rgba(32, 201, 151, 0.4);
  border-color: var(--highlight-color);
}
</style>
