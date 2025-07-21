<script lang="ts" setup>
import type { ParkingLot, ParkingSpot } from '@/types' // We will create this type file
import { BCard, BCardHeader, BCardBody } from 'bootstrap-vue-next'

defineProps({
  lot: {
    type: Object as () => ParkingLot,
    required: true,
  },
  highlightedSpot: {
    type: Number,
    default: undefined,
  },
  isEditable: {
    type: Boolean,
    default: true,
  },
})

defineEmits<{
  (e: 'delete', id: number): void
  (e: 'edit', lot: ParkingLot): void
  (e: 'view-spots', lot: ParkingLot, spot: ParkingSpot): void
}>()
</script>

<template>
  <BCard no-body class="parking-lot-card h-100">
    <BCardHeader class="d-flex justify-content-between align-items-center">
      <h5 class="mb-0" style="color: var(--text-color)">{{ lot.name }}</h5>
      <div v-if="isEditable" class="action-links">
        <a href="#" class="action-link me-3" @click.prevent="$emit('edit', lot)">Edit</a>
        <a href="#" class="action-link text-danger" @click.prevent="$emit('delete', lot.id)"
          >Delete</a
        >
      </div>
    </BCardHeader>
    <BCardBody>
      <div class="occupancy-info">
        <span class="occupied-count">{{ lot.occupied_spots_count }}</span>
        <span class="total-count">/ {{ lot.total_spots }} Occupied</span>
      </div>
      <div class="spot-grid">
        <div
          v-for="spot in lot.spots"
          :key="spot.id"
          :class="[
            'spot-box',
            { occupied: spot.status === 'Occupied' },
            { highlight: spot.id === highlightedSpot },
          ]"
          :title="`Spot ${spot.id} - ${spot.status}`"
          role="button"
          @click="$emit('view-spots', lot, spot)"
        >
          <span v-if="spot.status === 'Occupied'">O</span>
          <span v-else>A</span>
        </div>
      </div>
    </BCardBody>
  </BCard>
</template>

<style scoped>
.parking-lot-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}
.parking-lot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
  border-color: var(--highlight-color);
}

.card-header {
  background-color: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid var(--input-border);
  font-weight: 600;
}

.action-link {
  color: var(--text-color-muted);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}
.action-link:hover {
  color: var(--highlight-color);
}
.action-link.text-danger:hover {
  color: #ff5c5c !important;
}

.occupancy-info {
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: 300;
}
.occupied-count {
  font-size: 2rem;
  font-weight: 600;
  color: var(--highlight-color);
}
.total-count {
  color: var(--text-color-muted);
}

.spot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(30px, 1fr));
  gap: 8px;
}

.spot-box {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 700;
  font-size: 0.9rem;
  background-color: rgba(40, 167, 69, 0.2);
  border: 1px solid rgba(40, 167, 69, 0.5);
  color: var(--highlight-color);
  transition: all 0.2s ease;
}

.spot-box.occupied {
  background-color: rgba(220, 53, 69, 0.2);
  border-color: rgba(220, 53, 69, 0.5);
  color: #ff7878;
}

.spot-box.highlight {
  border: 2px solid #ffc107; /* Bootstrap 'warning' color for attention */
  box-shadow: 0 0 15px rgba(255, 193, 7, 0.5);
  transform: scale(1.1);
}
</style>
