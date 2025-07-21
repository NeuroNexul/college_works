<script setup lang="ts">
import { type ParkingLot, type ParkingSpot } from '@/types'
import axios from 'axios'
import { computed } from 'vue'
import { ref, watch } from 'vue'

const props = defineProps({
  lot: {
    type: Object as () => ParkingLot,
    required: true,
  },
  spot: {
    type: Object as () => ParkingSpot,
    required: true,
  },
  showSpotView: {
    type: Boolean,
    default: false,
  },
  can_delete: {
    type: Boolean,
    default: true,
  },
})

defineEmits<{
  (e: 'cancel'): void
  (e: 'delete', id: number): void
}>()

type BookingDetails = {
  id: number
  user_id: number
  booking_time: string
  parking_time: string | null
  release_time: string | null
  total_cost: number
  vehicle_number: string
  user: {
    id: number
    full_name: string
    email: string
    address: string
  }
  spot: {
    id: number
    status: string
    lot: {
      id: number
      name: string
      address: string
      price_per_hour: number
    }
  }
}

const showSpotDetails = ref(false)
const bookingDetails = ref<BookingDetails | null>(null)
const isLoading = ref(false)

const getBookingDetails = async () => {
  if (!props.spot || bookingDetails.value !== null) return
  isLoading.value = true

  if (props.spot?.status === 'Occupied') {
    const res = await axios.get<BookingDetails>(`/api/booking/${props.spot.id}`)

    console.log('Booking Details:', res.data)

    bookingDetails.value = res.data
  } else {
    bookingDetails.value = null
  }

  isLoading.value = false
}

const estimatedCost = computed(() => {
  const details = bookingDetails.value
  if (!details?.parking_time) return '0.00'

  const startTime = new Date(details.parking_time).getTime()
  const now = Date.now()
  const durationSeconds = (now - startTime) / 1000

  const durationHours = durationSeconds / 3600
  const cost = durationHours * details.spot.lot.price_per_hour

  return cost.toFixed(2)
})

watch(
  () => props.spot,
  () => {
    showSpotDetails.value = false // Reset details view when spot changes
    if (props.spot) {
      getBookingDetails()
    } else {
      bookingDetails.value = null
    }
  },
  { immediate: true },
)

watch(
  () => props.showSpotView,
  (newVal) => {
    if (!newVal) {
      showSpotDetails.value = false
      // bookingDetails.value = null // Reset details when view is closed
    }
  },
)

const formatDateTime = (isoString: string) => {
  if (!isoString) return 'N/A'
  return new Date(isoString).toLocaleString()
}
</script>

<template>
  <div>
    <div class="spot-details-content">
      <div class="info-grid">
        <div class="info-label">Spot ID</div>
        <div class="info-value">{{ spot?.id }}</div>

        <div class="info-label">Parking Lot</div>
        <div class="info-value">{{ lot?.name }}</div>

        <div class="info-label">Address</div>
        <div class="info-value">{{ lot?.address }}</div>

        <div class="info-label">Status</div>
        <div class="info-value">
          <BBadge
            :variant="spot?.status === 'Occupied' ? 'danger' : 'success'"
            pill
            class="py-2 px-4 fw-medium"
            :role="spot?.status === 'Occupied' ? 'button' : ''"
            @click="spot?.status === 'Occupied' && (showSpotDetails = !showSpotDetails)"
          >
            {{ spot?.status }}
          </BBadge>
        </div>
      </div>
    </div>

    <Transition name="expand">
      <div v-if="showSpotDetails && bookingDetails">
        <hr class="my-4" />
        <h5 class="details-subtitle">Occupied Spot Details</h5>
        <div class="info-grid mt-3">
          <div class="info-label">Customer ID</div>
          <div class="info-value">{{ bookingDetails.user.id }}</div>

          <div class="info-label">Customer Name</div>
          <div class="info-value">{{ bookingDetails.user.full_name }}</div>

          <div class="info-label">Vehicle Number</div>
          <div class="info-value mono-font">{{ bookingDetails.vehicle_number }}</div>

          <div class="info-label">Parking Time</div>
          <div class="info-value">{{ formatDateTime(bookingDetails.parking_time!) }}</div>

          <div class="info-label">Est. Parking Cost</div>
          <div class="info-value fw-bold" style="color: var(--highlight-color)">
            ${{ estimatedCost }}
          </div>
        </div>
      </div>
    </Transition>

    <div class="d-flex justify-content-end mt-4">
      <BButton type="button" variant="secondary" @click="$emit('cancel')" class="me-2">
        Cancel
      </BButton>
      <BButton
        type="submit"
        class="btn-primary-gradient"
        @click.prevent="$emit('delete', spot?.id || -1)"
        >Delete Lot</BButton
      >
    </div>
  </div>
</template>

<style scoped>
.info-grid {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 1rem;
  align-items: center;
}

.info-label {
  font-weight: 500;
  color: var(--text-color-muted);
}

.info-value {
  font-weight: 500;
  color: var(--text-color);
  word-break: break-all;
}

.btn-primary-gradient {
  background: linear-gradient(90deg, var(--button-bg-start), var(--button-bg-end));
  color: var(--text-color) !important;
  border: none;
  font-weight: 600;
  padding: 0.6rem 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.2);
}
.btn-primary-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(32, 201, 151, 0.3);
}

.btn-secondary {
  background-color: var(--input-bg);
  border-color: var(--input-border);
  color: var(--text-color-muted);
}
.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: var(--highlight-color);
  color: var(--text-color);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.4s ease-out;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0 !important; /* Override Bootstrap margins */
  margin-bottom: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
.expand-enter-to,
.expand-leave-from {
  max-height: 500px; /* Needs to be larger than the content will ever be */
  opacity: 1;
}
</style>
