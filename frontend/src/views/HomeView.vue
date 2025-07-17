<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main>
    <h1 class="">Home Page</h1>
    <router-link to="/login" class="btn btn-primary">Go to Login</router-link>
    <router-link to="/about" class="btn btn-primary">Go to About</router-link>
  </main>
</template>
