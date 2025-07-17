<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
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
  overflow: hidden;
  color: var(--text-color);

  color-scheme: dark;
}
</style>
