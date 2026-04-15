import { createApp } from 'vue'
import { createBootstrap } from 'bootstrap-vue-next'
import axios from 'axios'

// Add the necessary CSS
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

import App from './App.vue'
import router from './router'
import { useAuth } from '@/stores/auth'

// Configure Axios base URL
axios.defaults.baseURL = 'http://localhost:3000' // Your Flask backend URL
// This allows cookies to be sent with requests
axios.defaults.withCredentials = true

// Axios Interceptor for CSRF
// This will automatically add the CSRF token to requests if it exists.
axios.interceptors.request.use((config) => {
  // A helper function to get a cookie by name
  const getCookie = (name) => {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()?.split(';').shift() || null
    return null
  }

  const csrfToken = getCookie('csrf_access_token')
  if (csrfToken) {
    // The default header name for CSRF is 'X-CSRF-TOKEN'
    config.headers['X-CSRF-TOKEN'] = csrfToken
  }
  return config
})

const { initAuth } = useAuth()

async function startApp() {
  await initAuth()

  const app = createApp(App)

  app.use(createBootstrap())
  app.use(router)

  // mount after the initial navigation is ready
  await router.isReady()
  app.mount('#app')
}

startApp()
