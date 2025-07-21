import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { guestOnly: true },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/profile',
      name: 'UserProfile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'UserDashboard',
      component: () => import('../views/UserDashboardView.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/dashboard/my-parkings',
      name: 'UserParkings',
      component: () => import('../views/UserParkingsView.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/dashboard/summary',
      name: 'UserSummary',
      component: () => import('../views/UserSummaryView.vue'),
      meta: { requiresAuth: true, role: 'user' },
    },
    {
      path: '/admin',
      name: 'AdminDashboard',
      component: () => import('../views/AdminDashboardView.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/users',
      name: 'AdminUsers',
      component: () => import('../views/AdminUsersView.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/search',
      name: 'AdminSearch',
      component: () => import('../views/AdminSearchView.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/admin/summary',
      name: 'AdminSummary',
      component: () => import('../views/AdminSummaryView.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

// NAVIGATION GUARD
router.beforeEach((to, from, next) => {
  const { authState } = useAuth()
  const isAuthenticated = authState.isAuthenticated

  const requiresAuth = to.meta.requiresAuth
  const requiredRole = to.meta.role as 'admin' | 'user' | undefined

  // 1. If route requires authentication
  if (requiresAuth) {
    if (!isAuthenticated) {
      // User is not logged in, redirect to login page
      return next({ name: 'login' })
    }
    // User is logged in, check for role
    if (requiredRole && authState.user?.role !== requiredRole) {
      // User does not have the required role. Redirect them.
      // A good practice is to send them to their own dashboard or a 'Forbidden' page.
      if (authState.user?.role === 'admin') {
        return next({ name: 'AdminDashboard' })
      }
      return next({ name: 'UserDashboard' })
    }
    // User is authenticated and has the correct role (or no specific role is needed)
    return next()
  }
  // 2. If route is for guests only (like the login page)
  else if (to.meta.guestOnly && isAuthenticated) {
    // User is already logged in, redirect them away from the login page.
    if (authState.user?.role === 'admin') {
      return next({ name: 'AdminDashboard' })
    }
    return next({ name: 'UserDashboard' })
  } else {
    // 3. For all other public routes
    return next()
  }
})

export default router
