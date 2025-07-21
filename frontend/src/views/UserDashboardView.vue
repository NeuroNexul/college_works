<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue'
import type { ParkingLot } from '@/types'
import LotSearchResultCard from '@/components/LotSearchResultCard.vue'
import { BInputGroup, BFormInput, BSpinner, BAlert, BInputGroupText } from 'bootstrap-vue-next'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// State
const allLots = ref<ParkingLot[]>([])
const searchQuery = ref('')
const isLoading = ref(true)
const showBookingModal = ref(false)
const bookingLot = ref<ParkingLot | null>(null)
const error = ref<string | null>(null)
const vehicleNumber = ref('')
const validated = ref(false)

// Computed Property for Filtering
const filteredLots = computed(() => {
  if (!searchQuery.value) {
    return allLots.value
  }
  const query = searchQuery.value.toLowerCase()
  return allLots.value.filter(
    (lot) =>
      lot.name.toLowerCase().includes(query) ||
      lot.address.toLowerCase().includes(query) ||
      lot.pin_code.toLowerCase().includes(query),
  )
})

// API & Lifecycle
const fetchLots = async () => {
  isLoading.value = true
  error.value = null
  try {
    const res = await axios.get<ParkingLot[]>('/api/lots')
    allLots.value = res.data
  } catch (err) {
    console.error(err)
    error.value = 'Failed to fetch parking lots.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchLots)

const showBookingModalFn = (lot: ParkingLot) => {
  bookingLot.value = lot
  showBookingModal.value = true
}

// Handlers
const handleBookLot = async () => {
  if (!vehicleNumber.value.trim()) {
    error.value = 'Vehicle number is required.'
    return
  }

  if (!bookingLot.value) {
    error.value = 'No parking lot selected.'
    return
  }

  console.log('Booking lot:', bookingLot.value.name)
  error.value = null
  try {
    const res = await axios.post('/api/reserve', {
      lot_id: bookingLot.value.id,
      vehicle_number: vehicleNumber.value,
    })
    console.log('Booking successful:', res.data)
    router.push({ name: 'UserParkings' })
  } catch (err) {
    console.error(err)
    error.value = 'Failed to book the parking lot. Please try again.'
  }
}
</script>

<template>
  <div class="user-dashboard">
    <h1 class="page-title text-center mb-3">Find Your Parking Spot</h1>
    <p class="page-subtitle text-center mb-4">Search for a lot by name, address, or pin code.</p>

    <!-- Search Bar -->
    <div class="search-container mx-auto mb-5">
      <BInputGroup>
        <BInputGroupText is-text>
          <i class="bi bi-search"></i>
        </BInputGroupText>
        <BFormInput
          v-model="searchQuery"
          class="search-input"
          placeholder="e.g., Downtown, 123 Main St, 90210..."
        />
      </BInputGroup>
    </div>

    <!-- Results Section -->
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <BSpinner style="width: 3rem; height: 3rem"></BSpinner>
      <p class="mt-3">Finding Available Lots...</p>
    </div>

    <!-- Error State -->
    <BAlert v-else-if="error" show variant="danger" class="text-center">{{ error }}</BAlert>

    <!-- Content -->
    <div v-else>
      <!-- Empty Search Result State -->
      <div v-if="filteredLots.length === 0" class="text-center py-5 empty-state">
        <i class="bi bi-compass display-1"></i>
        <h3 class="mt-3">No Parking Lots Match Your Search</h3>
        <p class="text-color-muted">
          Try a different search term or clear the search field to see all lots.
        </p>
      </div>

      <!-- Lots Grid with Animation -->
      <TransitionGroup name="lot-list" tag="div" class="row g-4">
        <div v-for="lot in filteredLots" :key="lot.id" class="col-12 col-md-6 col-lg-4 d-flex">
          <LotSearchResultCard :lot="lot" @book="showBookingModalFn" class="w-100" />
        </div>
      </TransitionGroup>

      <BModal v-model="showBookingModal" title="Confirm Booking" no-footer centered>
        <div v-if="bookingLot" class="booking-details">
          <!-- Lot Information Section -->
          <h4 class="lot-name mb-2">{{ bookingLot.name }}</h4>
          <div class="lot-details-grid">
            <div class="detail-item">
              <i class="bi bi-geo-alt-fill"></i>
              <span>{{ bookingLot.address }}, {{ bookingLot.pin_code }}</span>
            </div>
            <div class="detail-item">
              <i class="bi bi-currency-dollar"></i>
              <span>{{ bookingLot.price_per_hour.toFixed(2) }} / hour (charged upon exit)</span>
            </div>
            <div class="detail-item">
              <i class="bi bi-p-circle-fill"></i>
              <span
                >{{ bookingLot.total_spots - bookingLot.occupied_spots_count }} spots
                available</span
              >
            </div>
          </div>

          <hr class="my-4" />

          <!-- Form Section -->
          <BForm @submit.prevent="handleBookLot" novalidate :validated="validated">
            <BFormGroup
              label="Enter Your Vehicle Number"
              label-for="vehicle-number-input"
              description="This will be used to identify your vehicle in the lot."
            >
              <BFormInput
                id="vehicle-number-input"
                v-model="vehicleNumber"
                required
                placeholder="e.g., STATE-1234"
                size="lg"
                class="mono-font text-uppercase"
              />
              <BFormInvalidFeedback>Vehicle number is required.</BFormInvalidFeedback>
            </BFormGroup>

            <!-- Action Buttons -->
            <div class="d-flex justify-content-end mt-4">
              <BButton
                type="button"
                variant="secondary"
                @click="showBookingModal = false"
                class="me-2"
              >
                Cancel
              </BButton>
              <BButton
                type="submit"
                class="btn-primary-gradient"
                variant="success"
                :disabled="isLoading"
              >
                <BSpinner v-if="isLoading" small class="me-2"></BSpinner>
                Reserve My Spot
              </BButton>
            </div>
          </BForm>
        </div>
      </BModal>
    </div>
  </div>
</template>

<style scoped>
.user-dashboard {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.page-title {
  color: var(--text-color);
  font-weight: 600;
}
.page-subtitle {
  color: var(--text-color-muted);
  font-weight: 300;
  font-size: 1.1rem;
}
.search-container {
  max-width: 600px;
}
.search-input,
.input-group-text {
  background-color: var(--input-bg) !important;
  color: var(--text-color) !important;
  border: 1px solid var(--input-border) !important;
  padding: 0.75rem 1rem;
}
.search-input:focus,
.search-input:focus + .input-group-text {
  box-shadow: 0 0 0 0.25rem rgba(32, 201, 151, 0.25);
  border-color: var(--highlight-color) !important;
}
.input-group-text {
  border-right: none !important;
  color: var(--text-color-muted) !important;
}
.search-input {
  border-left: none !important;
}

.empty-state i {
  color: var(--input-border);
}
.d-flex {
  display: flex !important;
}

.lot-name {
  color: var(--highlight-color);
  font-weight: 700;
}
.lot-details-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.detail-item {
  display: flex;
  align-items: center;
  color: var(--text-color-muted);
  font-size: 0.95rem;
}
.detail-item i {
  color: var(--highlight-color);
  margin-right: 0.75rem;
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}
hr {
  border-color: var(--input-border);
  opacity: 0.5;
}
.form-group label {
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}
.form-group small {
  color: var(--text-color-muted) !important;
  opacity: 0.7;
}
.form-control.mono-font {
  font-family: 'Courier New', Courier, monospace;
  font-weight: 700;
  letter-spacing: 1px;
}
.btn-primary-gradient {
  background: linear-gradient(90deg, var(--button-bg-start), var(--button-bg-end));
  border: none;
  font-weight: 600;
  padding: 0.6rem 1.5rem;
}
.btn-secondary {
  background-color: var(--input-bg);
  border-color: var(--input-border);
  color: var(--text-color-muted);
}

/* Lot List Transition */
.lot-list-enter-active,
.lot-list-leave-active {
  transition: all 0.5s ease;
}
.lot-list-move {
  transition: transform 0.5s ease;
}
.lot-list-enter-from,
.lot-list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
.lot-list-leave-active {
  position: absolute;
}
</style>
