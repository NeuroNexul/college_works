<script lang="ts" setup>
import { BCard } from 'bootstrap-vue-next'
defineProps<{
  icon: string
  value: string | number
  label: string
}>()
</script>

<template>
  <BCard class="stat-card">
    <div class="d-flex align-items-center">
      <div class="stat-icon-wrapper">
        <i :class="['stat-icon', icon]"></i>
      </div>
      <div class="stat-content">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-label">{{ label }}</div>
      </div>
    </div>
  </BCard>
</template>

<style scoped>
.stat-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-left: 4px solid var(--highlight-color);
  border-radius: 8px;
  padding: 1.25rem;
  transition: all 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-5px);
  background-color: rgba(32, 201, 151, 0.05);
}
.stat-icon-wrapper {
  font-size: 2rem;
  color: var(--highlight-color);
  margin-right: 1rem;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.stat-label {
  font-size: 0.9rem;
  color: var(--text-color-muted);
}
</style>
