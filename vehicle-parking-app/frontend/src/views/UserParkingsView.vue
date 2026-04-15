<script lang="ts" setup>
import { ref, onMounted, computed, watch, reactive } from 'vue'
import type { Booking } from '@/types'
import { BCard, BCardBody, BButton, BSpinner, BAlert } from 'bootstrap-vue-next'
import axios from 'axios'

// State
const allBookings = ref<Booking[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)
const elapsedTimers = reactive<Record<number, string>>({})
const timerInterval = ref<number | null>(null)

// Computed Properties for Data Separation
const reservedBookings = computed(() =>
  allBookings.value.filter((b) => b.release_time === null && b.parking_time === null),
)
const occupiedBookings = computed(() =>
  allBookings.value.filter((b) => b.release_time === null && b.parking_time !== null),
)
const pastBookings = computed(() =>
  allBookings.value
    .filter((b) => b.release_time !== null)
    .sort((a, b) => new Date(b.release_time!).getTime() - new Date(a.release_time!).getTime()),
)

// Timer Management
const stopTimer = () => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

const startTimerForOccupied = () => {
  stopTimer()

  timerInterval.value = window.setInterval(() => {
    occupiedBookings.value.forEach((booking) => {
      if (booking.parking_time) {
        const startTime = new Date(booking.parking_time).getTime()
        const now = Date.now()
        const diff = now - startTime
        const h = String(Math.floor(diff / 3600000)).padStart(2, '0')
        const m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0')
        const s = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0')
        elapsedTimers[booking.id] = `${h}:${m}:${s}`
      }
    })
  }, 1000)
}

// Watch for changes in the list of occupied bookings to manage timers
watch(
  occupiedBookings,
  () => {
    startTimerForOccupied()
  },
  { deep: true },
)

// Mock Data & Lifecycle
const fetchBookings = async () => {
  isLoading.value = true
  error.value = null
  try {
    const res = await axios.get<Booking[]>('/api/bookings')
    allBookings.value = res.data
    startTimerForOccupied() // Start timer after fetching bookings
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load your parking data.'
  } finally {
    isLoading.value = false
  }
}
onMounted(fetchBookings)

// Helper Functions
const formatDateTime = (isoString: string) => {
  if (!isoString) return 'N/A'
  return new Date(isoString).toLocaleString()
}

const calculateDuration = (start: string, end: string): string => {
  const diffMs = new Date(end).getTime() - new Date(start).getTime()
  const hours = Math.floor(diffMs / 3600000)
  const minutes = Math.floor((diffMs % 3600000) / 60000)
  let duration = ''
  if (hours > 0) duration += `${hours}h `
  duration += `${minutes}m`
  return duration
}

// Handlers
const handleParkCar = async (bookingId: number) => {
  try {
    const res = await axios.post(`/api/park/${bookingId}`)

    if (res.status === 200) {
      fetchBookings() // Refetch to update UI state
    } else {
      error.value = 'Failed to park the car.' + res.data.message
    }
  } catch (err) {
    console.error(err)
    error.value = 'Failed to park the car.'
    return
  }
}
const handleRelease = async (bookingId: number) => {
  try {
    const res = await axios.post(`/api/release/${bookingId}`)

    if (res.status === 200) {
      fetchBookings() // Refetch to update UI state
    } else {
      error.value = 'Failed to release the parking lot.' + res.data.message
    }
  } catch (err) {
    console.error(err)
    error.value = 'Failed to release the parking spot.'
  }
}

const handleExport = async () => {
  try {
    const res = await axios.post('/api/export-bookings')

    if (res.status === 202) {
      alert(
        'Your parking history is being exported. You will receive an email with the file shortly.',
      )
    }
  } catch (err) {
    console.error(err)
    error.value = 'Failed to export parking history.'
  }
}
</script>

<template>
  <div class="parking-view">
    <!-- Error State -->
    <BAlert v-if="error" show variant="danger" class="text-center">{{ error }}</BAlert>

    <Transition name="fade" mode="out-in">
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-5">
        <BSpinner style="width: 3rem; height: 3rem"></BSpinner>
        <p class="mt-3">Loading Your Parking Data...</p>
      </div>

      <!-- Content: Two-Column Layout -->
      <BRow v-else class="g-4">
        <!-- Left Column: Active Session -->
        <BCol lg="5" xl="4">
          <!-- Section for Occupied Sessions -->
          <div class="session-section">
            <h2 class="section-title">Active Parking Sessions ({{ occupiedBookings.length }})</h2>

            <TransitionGroup name="session-list" tag="div">
              <BCard
                v-for="booking in occupiedBookings"
                :key="booking.id"
                no-body
                class="active-session-card session-card occupied"
              >
                <BCardBody v-if="booking">
                  <h4 class="lot-name mb-1">{{ booking.lot.name }}</h4>
                  <p class="lot-address mb-4">
                    <i class="bi bi-geo-alt-fill me-2"></i>{{ booking.lot.address }}
                  </p>

                  <div class="session-timer">
                    <div class="timer-label">Elapsed Time</div>
                    <div class="timer-value">{{ elapsedTimers[booking.id] || '00:00:00' }}</div>
                  </div>

                  <dl class="details-list">
                    <dt>Vehicle Number</dt>
                    <dd class="mono-font">{{ booking.vehicle_number }}</dd>
                    <dt>Spot ID</dt>
                    <dd>{{ booking.spot.id }}</dd>
                    <dt>Booked At</dt>
                    <dd>{{ formatDateTime(booking.booking_time!) }}</dd>
                    <dt>Parked At</dt>
                    <dd>{{ formatDateTime(booking.parking_time!) }}</dd>
                  </dl>

                  <BButton class="w-100 mt-2" variant="success" @click="handleRelease(booking.id)">
                    <i class="bi bi-box-arrow-left me-2"></i> Release Parking
                  </BButton>
                </BCardBody>
                <div v-else class="empty-state-card text-center">
                  <i class="bi bi-moon-stars display-4"></i>
                  <p class="mt-3 mb-0 text-color-muted">No active parking sessions.</p>
                </div>
              </BCard>
            </TransitionGroup>
          </div>
        </BCol>

        <!-- Right Column: Parking History -->
        <BCol lg="7" xl="8">
          <!-- Section for Reserved Sessions -->
          <div class="session-section reserved">
            <h2 class="section-title">Reserved Sessions ({{ reservedBookings.length }})</h2>
            <TransitionGroup
              name="session-list"
              tag="div"
              class="d-flex flex-row flex -wrap gap-3 overflow-auto pb-2"
            >
              <BCard
                v-for="booking in reservedBookings"
                :key="booking.id"
                no-body
                class="session-card reserved mb-0 flex-shrink-0"
              >
                <BCardBody>
                  <div class="status-indicator">
                    <BSpinner small variant="info"></BSpinner><span class="ms-2">RESERVED</span>
                  </div>
                  <h5 class="lot-name mb-1">{{ booking.lot.name }}</h5>
                  <p class="lot-address mb-3">
                    <i class="bi bi-geo-alt-fill me-2"></i>{{ booking.lot.address }}
                  </p>
                  <dl class="details-list">
                    <dt>Vehicle</dt>
                    <dd class="mono-font">{{ booking.vehicle_number }}</dd>
                    <dt>Reserved At</dt>
                    <dd>{{ formatDateTime(booking.booking_time) }}</dd>
                  </dl>
                  <BButton @click="handleParkCar(booking.id)" variant="success" class="w-100 mt-2"
                    >I Have Arrived / Park Car</BButton
                  >
                </BCardBody>
              </BCard>
            </TransitionGroup>
          </div>

          <div class="session-section past-history mt-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h2 class="section-title">Parking History</h2>

              <BButton
                v-if="pastBookings.length > 0"
                variant="outline-success"
                @click="handleExport"
              >
                <i class="bi bi-save me-2"></i> Expport
              </BButton>
            </div>
            <div class="history-list">
              <div v-if="pastBookings.length === 0" class="empty-state-card text-center">
                <i class="bi bi-clock-history display-4"></i>
                <p class="mt-3 mb-0 text-color-muted">Your parking history will appear here.</p>
              </div>

              <TransitionGroup v-else name="history-list-anim" tag="div">
                <BListGroupItem
                  v-for="booking in pastBookings"
                  :key="booking.id"
                  class="d-flex justify-content-between align-items-center flex-wrap"
                >
                  <div class="flex-grow-1 me-3 mb-2 mb-md-0">
                    <h6 class="history-lot-name mb-1">{{ booking.lot.name }}</h6>
                    <span class="history-vehicle mono-font">{{ booking.vehicle_number }}</span>
                  </div>

                  <div class="me-4 history-timestamps">
                    <div class="timestamp-item" title="Booking Time">
                      <i class="bi bi-box-arrow-in-right"></i>
                      <span>{{ formatDateTime(booking.booking_time) }}</span>
                    </div>
                    <div class="timestamp-item" title="Release Time">
                      <i class="bi bi-box-arrow-left"></i>
                      <span>{{ formatDateTime(booking.release_time!) }}</span>
                    </div>
                  </div>

                  <div class="history-meta">
                    <span class="me-4" title="Duration"
                      ><i class="bi bi-hourglass-split me-1"></i>
                      {{ calculateDuration(booking.booking_time, booking.release_time!) }}</span
                    >
                    <span class="history-cost" title="Total Cost"
                      ><i class="bi bi-wallet2 me-1"></i> ${{
                        booking.total_cost?.toFixed(2)
                      }}</span
                    >
                  </div>
                </BListGroupItem>
              </TransitionGroup>
            </div>
          </div>
        </BCol>
      </BRow>
    </Transition>
  </div>
</template>

<style scoped>
.parking-view {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.section-title {
  color: var(--text-color-muted);
  font-weight: 300;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.session-section {
  width: 100%;
}
.session-card {
  margin-bottom: 1.5rem;
  background: var(--form-bg);
  border-radius: 12px;
  padding: 1.25rem;
}
.session-card.occupied {
  border: 1px solid var(--highlight-color);
  box-shadow: 0 0 25px rgba(32, 201, 151, 0.2);
}
.session-card.reserved {
  border: 1px solid #0dcaf0;
  padding: 0.25rem;
  /* box-shadow: 0 0 25px rgba(13, 202, 240, 0.2); */
}
.session-card .lot-name {
  font-weight: 700;
}
.session-card .lot-address {
  color: var(--text-color-muted);
  font-size: 0.9rem;
}
.session-card.occupied .lot-name {
  color: var(--highlight-color);
}
.session-card.reserved .lot-name {
  color: #0dcaf0;
  padding-right: 9rem;
}

.session-timer {
  background: rgba(32, 201, 151, 0.1);
  border-radius: 8px;
  text-align: center;
  padding: 1rem;
  margin-bottom: 1.5rem;
}
.timer-label {
  color: var(--text-color-muted);
  font-size: 0.9rem;
}
.timer-value {
  color: var(--highlight-color);
  font-size: 2.25rem;
  font-weight: 700;
  font-family: 'Courier New', Courier, monospace;
  letter-spacing: 2px;
}

.status-indicator {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  font-weight: 700;
  color: #0dcaf0;
  background-color: rgba(13, 202, 240, 0.1);
  padding: 0.3rem 0.8rem;
  border-radius: 50px;
  font-size: 0.8rem;
}

.details-list {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 0.75rem;
}
.details-list dt {
  color: var(--text-color-muted);
  font-weight: 500;
}
.details-list dd {
  color: var(--text-color);
  font-weight: 500;
  margin: 0;
}

/* History List */
.history-list {
  background-color: var(--form-bg);
  border-radius: 12px;
  border: 1px solid var(--input-border);
  overflow: hidden;
}
.list-group-item {
  background-color: transparent;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--input-border) !important;
  transition: background-color 0.2s ease-in-out;
}
.list-group-item:last-child {
  border-bottom: none !important;
}
.list-group-item:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.history-lot-name {
  color: var(--text-color);
  font-weight: 600;
  margin-bottom: 0.1rem;
}
.history-vehicle {
  color: var(--text-color-muted);
  font-size: 0.9rem;
}

.history-timestamps {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-color-muted);
}
.timestamp-item {
  display: flex;
  align-items: center;
}
.timestamp-item i {
  color: var(--highlight-color);
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.history-meta {
  color: var(--text-color-muted);
  font-size: 0.9rem;
}
.history-cost {
  color: var(--text-color);
  font-weight: 600;
}
.history-meta i {
  color: var(--highlight-color);
}

.mono-font {
  font-family: 'Courier New', Courier, monospace;
  font-weight: 700;
}

.empty-state-card {
  background-color: var(--form-bg);
  border: 2px dashed var(--input-border);
  border-radius: 12px;
  padding: 2rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}
.empty-state-card i {
  color: var(--input-border);
}

/* Animation */
.history-list-anim-enter-active,
.history-list-anim-leave-active {
  transition: all 0.5s ease;
}
.history-list-anim-enter-from,
.history-list-anim-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.session-list-enter-active,
.session-list-leave-active {
  transition: all 0.5s ease;
}
.session-list-enter-from,
.session-list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
