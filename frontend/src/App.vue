<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <nav-bar />

  <main class="main-container w-100 overflow-auto">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
</template>

<style>
:root {
  /* Green Dark Mode Color Palette */
  --background-start: #0f2027;
  --background-middle: #203a43;
  --background-end: #2c5364;
  --form-bg: rgba(10, 25, 15, 0.4);
  --text-color: #e0e0e0;
  --text-color-muted: #a0a0a0;
  --input-bg: rgba(255, 255, 255, 0.05);
  --input-border: rgba(40, 167, 69, 0.4);
  --button-bg-start: #28a745;
  --button-bg-end: #20c997;
  --highlight-color: #20c997;
}

body {
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(
    135deg,
    var(--background-start),
    var(--background-middle),
    var(--background-end)
  );
  min-height: 100vh;
  padding-top: 65px; /* Adjust based on your navbar height */
  overflow: hidden;
  color: var(--text-color);

  color-scheme: dark;
}

.main-container {
  height: calc(100dvh - 65px); /* Adjust based on your navbar height */
  height: calc(100vh - 65px); /* Fallback for browsers that don't support 100dvh */
}

/* Add this CSS to App.vue or your main CSS file for page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
