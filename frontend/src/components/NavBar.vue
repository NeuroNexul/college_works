<script lang="ts" setup>
import {
  BNavbar,
  BNavbarBrand,
  BNavbarToggle,
  BCollapse,
  BNavbarNav,
  BNavItem,
  BNavItemDropdown,
  BDropdownItem,
  BDropdownDivider,
} from 'bootstrap-vue-next'
import { useAuth } from '@/stores/auth'
import { computed } from 'vue'

const { authState, logout } = useAuth()

const navLinks = computed(() => {
  if (authState.isAuthenticated) {
    if (authState.user?.role === 'admin') {
      return [
        { to: { name: 'AdminDashboard' }, text: 'Dashboard', icon: 'bi bi-speedometer2' },
        { to: { name: 'home' }, text: 'Users', icon: 'bi bi-people-fill' },
        { to: { name: 'home' }, text: 'Summary', icon: 'bi bi-bar-chart-line-fill' },
      ]
    } else if (authState.user?.role === 'user') {
      return [
        { to: { name: 'UserDashboard' }, text: 'Find Parking', icon: 'bi bi-search' },
        { to: { name: 'home' }, text: 'My Parking', icon: 'bi bi-car-front-fill' },
        { to: { name: 'home' }, text: 'History', icon: 'bi bi-clock-history' },
      ]
    }
  } else {
    return [
      { to: { name: 'home' }, text: 'Home', icon: 'bi bi-house-door-fill' },
      { to: { name: 'about' }, text: 'About', icon: 'bi bi-info-circle-fill' },
      { to: { name: 'login' }, text: 'Login', icon: 'bi bi-box-arrow-in-right' },
    ]
  }
})

const handleLogout = async () => {
  await logout()
  // The logout function already handles redirection
}
</script>

<template>
  <BNavbar toggleable="lg" class="fixed-top custom-navbar">
    <BNavbarBrand :to="{ name: 'home' }">
      <!-- Assuming you have a route named 'Home' -->
      <i class="bi bi-p-circle-fill me-2"></i>
      Vehicle Parking System
    </BNavbarBrand>

    <BNavbarToggle target="nav-collapse" />

    <BCollapse id="nav-collapse" is-nav>
      <!-- Role-based Links -->
      <BNavbarNav class="me-auto mb-2 mb-lg-0">
        <TransitionGroup name="nav-link-fade" tag="div" class="d-flex flex-column flex-lg-row">
          <BNavItem v-for="link in navLinks" :key="link.text" :to="link.to" class="nav-item">
            <i :class="[link.icon, 'me-1']"></i> {{ link.text }}
          </BNavItem>
        </TransitionGroup>
      </BNavbarNav>

      <!-- User Dropdown (Right side) -->
      <BNavbarNav>
        <BNavItemDropdown
          :text="
            authState.isAuthenticated ? authState.user?.fullName || authState.user?.email : 'Guest'
          "
          right
          :disabled="!authState.isAuthenticated"
        >
          <template #button-content>
            <i class="bi bi-person-circle me-2"></i>
            <span>{{
              authState.isAuthenticated
                ? authState.user?.fullName || authState.user?.email
                : 'Guest'
            }}</span>
          </template>

          <BDropdownItem :to="{ name: 'home' }">
            <i class="bi bi-person-lines-fill me-2"></i> Profile
          </BDropdownItem>
          <BDropdownDivider />
          <BDropdownItem href="#" @click.prevent="handleLogout" class="logout-item">
            <i class="bi bi-box-arrow-right me-2"></i> Logout
          </BDropdownItem>
        </BNavItemDropdown>
      </BNavbarNav>
    </BCollapse>
  </BNavbar>
</template>

<style scoped>
@import url('bootstrap-icons/font/bootstrap-icons.css');

/* This class is on the root element of THIS component, so it doesn't need :deep() */
.custom-navbar {
  background-color: var(--form-bg);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--input-border);
  padding: 0.75rem 1rem;
}

/* This targets the <BNavbarBrand> component's rendered content */
:deep(.navbar-brand) {
  color: var(--highlight-color);
  font-weight: 600;
  letter-spacing: 0.5px;
  font-size: 1.2rem;
  transition: color 0.3s ease;
}
:deep(.navbar-brand:hover) {
  color: #fff;
}

/* This targets the <a> tag inside <BNavItem> */
:deep(.nav-item .nav-link) {
  color: var(--text-color-muted);
  font-weight: 500;
  transition: color 0.3s ease;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
}

:deep(.nav-item .nav-link:hover),
:deep(.nav-item .nav-link:focus) {
  color: var(--text-color);
}

/* Vue Router adds this class automatically, so we need to target it deeply */
:deep(.nav-item .nav-link.router-link-exact-active) {
  color: var(--highlight-color) !important; /* !important can help with specificity here */
  font-weight: 600;
}

/* The dropdown menu is often rendered outside the component's DOM tree (in a portal)
   so :deep() is absolutely essential for it to work. */
:deep(.dropdown-menu) {
  background-color: #142b33;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  padding: 0.5rem 0;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

:deep(.dropdown-item) {
  color: var(--text-color-muted);
  padding: 0.75rem 1.5rem;
  transition: all 0.2s ease-in-out;
  display: flex;
  align-items: center;
}

:deep(.dropdown-item:hover),
:deep(.dropdown-item:focus) {
  background-color: rgba(40, 167, 69, 0.2);
  color: var(--highlight-color);
}

:deep(.dropdown-divider) {
  border-color: var(--input-border);
}

:deep(.logout-item:hover),
:deep(.logout-item:focus) {
  color: #ff5c5c !important;
  background-color: rgba(255, 92, 92, 0.1);
}

/* Customizing the hamburger menu icon for dark mode */
:deep(.navbar-toggler) {
  border-color: rgba(40, 167, 69, 0.5);
}

:deep(.navbar-toggler-icon) {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(32, 201, 151, 0.8)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

/* other styles... */

/* 1. Define the transition duration and easing for enter, leave, and move */
.nav-link-fade-enter-active,
.nav-link-fade-leave-active {
  transition: all 0.4s ease;
}
.nav-link-fade-move {
  transition: transform 0.4s ease;
}

/* 2. Define the starting state for entering elements */
.nav-link-fade-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

/* 3. Define the ending state for leaving elements */
.nav-link-fade-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 4. Ensure leaving elements don't disrupt layout */
.nav-link-fade-leave-active {
  position: absolute;
}
</style>
