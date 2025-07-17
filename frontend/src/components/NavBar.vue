<script lang="ts" setup>
import { useAuth } from '@/stores/auth'

const { authState, logout } = useAuth()
</script>

<template>
  <nav v-if="authState.isAuthenticated">
    <p>Welcome, {{ authState.user?.fullName || authState.user?.email }}</p>
    <router-link to="/admin" v-if="authState.user?.role === 'admin'">Admin</router-link>
    <router-link to="/dashboard" v-if="authState.user?.role === 'user'">Dashboard</router-link>
    <button @click="logout">Logout</button>
  </nav>
</template>
