<script lang="ts" setup>
import { computed } from 'vue'
import type { ParkingLot } from '@/types'
import {
  BCard,
  BCardHeader,
  BCardBody,
  BCardFooter,
  BBadge,
  BListGroup,
  BListGroupItem,
  BButton,
  type BaseColorVariant,
} from 'bootstrap-vue-next'

const props = defineProps<{
  lot: ParkingLot
}>()

defineEmits<{
  (e: 'book', lot: ParkingLot): void
}>()

const availableSpots = computed(() => {
  return props.lot.total_spots - props.lot.occupied_spots_count
})

const availability = computed<{
  variant: keyof BaseColorVariant
  text: string
}>(() => {
  const percentage = (availableSpots.value / props.lot.total_spots) * 100
  if (percentage === 0) return { variant: 'danger', text: 'Full' }
  if (percentage <= 25) return { variant: 'warning', text: 'Filling Fast' }
  return { variant: 'success', text: 'Available' }
})
</script>

<template>
  <BCard no-body class="lot-card h-100">
    <BCardHeader class="d-flex justify-content-between align-items-center">
      <h5 class="mb-0">{{ lot.name }}</h5>
      <BBadge :variant="availability.variant" pill class="availability-badge">
        {{ availability.text }}
      </BBadge>
    </BCardHeader>

    <BCardBody class="d-flex flex-column">
      <BListGroup flush class="flex-grow-1">
        <BListGroupItem>
          <i class="bi bi-geo-alt-fill me-2 text-color-muted"></i>
          {{ lot.address }}, {{ lot.pin_code }}
        </BListGroupItem>
        <BListGroupItem>
          <i class="bi bi-currency-dollar me-2 text-color-muted"></i>
          {{ lot.price_per_hour.toFixed(2) }} / hour
        </BListGroupItem>
        <BListGroupItem>
          <i class="bi bi-p-circle-fill me-2 text-color-muted"></i>
          {{ availableSpots }} / {{ lot.total_spots }} spots available
        </BListGroupItem>
      </BListGroup>
    </BCardBody>

    <BCardFooter>
      <BButton
        @click="$emit('book', lot)"
        :disabled="availableSpots === 0"
        class="w-100 btn-primary-gradient"
      >
        <span v-if="availableSpots > 0">Book Now</span>
        <span v-else>Lot Full</span>
      </BButton>
    </BCardFooter>
  </BCard>
</template>

<style scoped>
.lot-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}
.lot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
  border-color: var(--highlight-color);
}
.card-header,
.card-footer {
  background-color: rgba(255, 255, 255, 0.03);
  border-color: var(--input-border);
}
.card-header h5 {
  color: var(--text-color);
}
.list-group-item {
  background-color: transparent;
  color: var(--text-color);
  border-color: var(--input-border) !important;
  font-size: 0.95rem;
}
.text-color-muted {
  color: var(--text-color-muted);
}
.availability-badge {
  font-size: 0.8rem;
  font-weight: 600;
}
.btn-primary-gradient {
  background: linear-gradient(90deg, var(--button-bg-start), var(--button-bg-end));
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.2);
}
.btn-primary-gradient:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(32, 201, 151, 0.3);
}
.btn-primary-gradient:disabled {
  background: var(--input-bg);
  opacity: 0.5;
}
</style>
