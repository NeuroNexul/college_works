<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import type { ParkingLot, ParkingSpot } from '@/types'
import ParkingLotCard from '@/components/ParkingLotCard.vue'
import { BButton, BSpinner, BAlert, BModal } from 'bootstrap-vue-next'
import ParkingLotForm, { type LotFormData } from '@/components/ParkingLotForm.vue'
import ParkingLotSpotView from '@/components/ParkingLotSpotView.vue'

// State
const lots = ref<ParkingLot[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)
const showModal = ref(false)
const isEditing = ref(false)
const showSpotView = ref(false)
const showSpotDetails = ref(false)
const selectedLot = ref<ParkingLot | null>(null)
const selectedSpot = ref<ParkingSpot | null>(null)

// API Functions
const fetchLots = async () => {
  // isLoading.value = true
  error.value = null
  try {
    const response = await axios.get('/api/admin/lots')
    lots.value = response.data as ParkingLot[]
  } catch (err) {
    console.error(err)
    error.value = 'Failed to fetch parking lots. Please try again later.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchLots)

// Modal and Action Handlers
const openAddModal = () => {
  isEditing.value = false
  selectedLot.value = null
  showModal.value = true
}

const openEditModal = (lot: ParkingLot) => {
  isEditing.value = true
  selectedLot.value = { ...lot } // Create a copy to avoid mutating the original
  showModal.value = true
}

const viewSpotModal = (lot: ParkingLot, spot: ParkingSpot) => {
  selectedLot.value = lot
  selectedSpot.value = spot // Reset selected spot
  showSpotView.value = true
}

const confirmDelete = async (id: number) => {
  if (
    window.confirm(
      'Are you sure you want to delete this parking lot? This action cannot be undone.',
    )
  ) {
    // Call API to delete, then refresh
    console.log(`Deleting lot ${id}`)
    try {
      const res = await axios.delete(`/api/admin/lots/${id}`)

      if (res.status === 200) {
        lots.value = lots.value.filter((lot) => lot.id !== id) // Optimistic UI update
        fetchLots()
      } else {
        console.error('Failed to delete lot:', res.data)
        error.value = 'Failed to delete the parking lot. Please try again later.'
      }
    } catch (err) {
      console.error(err)
      error.value = 'Failed to delete the parking lot. Please try again later.'
    }
  }
}

// Handle form submission
const handleFormSubmit = async (formData: LotFormData, id: number | null): Promise<any> => {
  if (isEditing.value) {
    // Update existing lot
    console.log(`Updating lot ${id}`, formData)
    const response = await axios.put(`/api/admin/lots/${id}`, formData)
    if (response.status === 200) {
      // Update the local state with the updated lot
      const index = lots.value.findIndex((lot) => lot.id === id)
      if (index !== -1) {
        lots.value[index] = { ...lots.value[index], ...response.data }
      }
    } else {
      console.error('Failed to update lot:', response.data)
      error.value = 'Failed to update the parking lot. Please try again later.'
    }
  } else {
    // Add new lot
    console.log('Adding new lot', formData)
    const res = await axios.post('/api/admin/lots', formData)
    if (res.status !== 201) {
      console.error('Failed to add lot:', res.data)
      error.value = 'Failed to add the parking lot. Please try again later.'
    }
  }
  showModal.value = false
  fetchLots() // Refresh the list after adding/updating
}

const confirmSpotDelete = async (spotId: number) => {
  if (
    window.confirm(
      'Are you sure you want to delete this parking spot? This action cannot be undone.',
    )
  ) {
    try {
      const response = await axios.delete(`/api/admin/spots/${spotId}`)
      if (response.status === 200) {
        // Remove the spot from the local state
        fetchLots() // Refresh the list of lots
        showSpotView.value = false // Close the modal after deletion
      } else {
        console.error('Failed to delete spot:', response.data)
        error.value = 'Failed to delete the parking spot. Please try again later.'
      }
    } catch (err) {
      console.error(err)
      error.value = 'Failed to delete the parking spot. Please try again later.'
    }
  }
}
</script>

<template>
  <div class="admin-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="page-title">Parking Lots</h2>

      <BButton @click="openAddModal" class="btn-primary-gradient">
        <i class="bi bi-plus-lg me-2"></i> Add Lot
      </BButton>
    </div>

    <!-- Error State -->
    <BAlert v-if="error" show variant="danger" class="text-center">{{ error }}</BAlert>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <BSpinner style="width: 3rem; height: 3rem"></BSpinner>
      <p class="mt-3">Loading Parking Lots...</p>
    </div>

    <!-- Content -->
    <div v-else class="main-content">
      <!-- Empty State -->
      <div v-if="lots.length === 0" class="text-center py-5 empty-state">
        <i class="bi bi-box2-heart display-1"></i>
        <h3 class="mt-3">No Parking Lots Found</h3>
        <p class="text-color-muted">Get started by adding your first parking lot!</p>
        <BButton @click="openAddModal" variant="outline-success" class="mt-3"
          >Create a New Lot</BButton
        >
      </div>

      <!-- Lots Grid with Animation -->
      <TransitionGroup name="lot-list" tag="div" class="row g-4">
        <div v-for="lot in lots" :key="lot.id" class="col-12 col-md-6 col-lg-4">
          <ParkingLotCard
            :lot="lot"
            @delete="confirmDelete"
            @edit="openEditModal"
            @view-spots="viewSpotModal"
          />
        </div>
      </TransitionGroup>
    </div>

    <!-- Add/Edit Modal -->
    <BModal
      v-model="showModal"
      :title="isEditing ? 'Edit Parking Lot' : 'Add New Parking Lot'"
      no-footer
      centered
    >
      <parking-lot-form
        :lot-data="selectedLot"
        :is-loading="isLoading"
        @submit="handleFormSubmit"
        @cancel="showModal = false"
      />
    </BModal>

    <!-- Spot View Modal -->
    <BModal v-model="showSpotView" title="Parking Lot Spots" centered no-footer>
      <KeepAlive>
        <ParkingLotSpotView
          :key="selectedLot?.id"
          :lot="selectedLot!"
          :spot="selectedSpot!"
          :show-spot-view="showSpotView"
          @cancel="showSpotView = false"
          @delete="confirmSpotDelete"
      /></KeepAlive>
    </BModal>
  </div>
</template>

<style scoped>
.admin-dashboard {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.page-title {
  color: var(--text-color);
  font-weight: 600;
}

.btn-primary-gradient {
  background: linear-gradient(90deg, var(--button-bg-start), var(--button-bg-end));
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.2);
}
.btn-primary-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(32, 201, 151, 0.3);
}

.main-content {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-state i {
  color: var(--input-border);
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
