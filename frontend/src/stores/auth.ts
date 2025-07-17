import { reactive, readonly } from 'vue'
import axios from 'axios'
import router from '@/router' // Import router to redirect on logout

// Define a type for our user object for type safety
interface User {
  id: number
  email: string
  fullName: string | null
  role: 'admin' | 'user'
}

// Define the shape of our state
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

// The reactive state object
const state = reactive<AuthState>({
  user: null,
  token: null,
  isAuthenticated: false,
})

// ACTIONS (methods to mutate the state)

/**
 * Initializes the auth state by checking localStorage and sessionStorage.
 * This should be called once when the app starts.
 */
async function initAuth(): Promise<void> {
  const userFromLocalStorage = localStorage.getItem('user')
  const userFromSessionStorage = sessionStorage.getItem('user')
  const tokenFromSessionStorage = sessionStorage.getItem('token')

  let potentialUser: User | null = null
  let potentialToken: string | null = null

  // Case 1: "Remember Me" was used. User is in localStorage, token is in a cookie.
  if (userFromLocalStorage) {
    potentialUser = JSON.parse(userFromLocalStorage)
    // Token is sent automatically by the browser via cookie.
  }
  // Case 2: Regular login. User and token are in sessionStorage.
  else if (userFromSessionStorage && tokenFromSessionStorage) {
    potentialUser = JSON.parse(userFromSessionStorage)
    potentialToken = tokenFromSessionStorage
  }

  if (potentialUser) {
    // Re-validate the session with the backend to ensure the token/cookie isn't stale
    try {
      // This relies on the cookie or the token being set in axios headers below
      if (potentialToken) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${potentialToken}`
      }
      // A simple protected endpoint to verify the token is still valid.
      const response = await axios.get('/api/profile')
      // If the above call succeeds, the session is valid.
      _setAuth(response.data, potentialToken)
    } catch (error) {
      // If it fails (e.g., 401 Unauthorized), the token is invalid. Log out.
      console.error('Session revalidation failed:', error)
      logout()
    }
  }
}

/**
 * Sets the authentication state.
 */
function _setAuth(userData: User, token: string | null): void {
  state.user = userData
  state.token = token
  state.isAuthenticated = true
  if (token) {
    // Set token for subsequent requests if it's not in a cookie
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
}

/**
 * Handles the login process.
 */
async function login(credentials: {
  email: any
  password: any
  rememberMe: boolean
}): Promise<void> {
  const { data } = await axios.post('/api/auth/login', credentials)

  _setAuth(data.user, data.access_token || null)
  console.log('Login response:', data)

  if (credentials.rememberMe) {
    // Backend sets the cookie, frontend stores user data in localStorage.
    localStorage.setItem('user', JSON.stringify(data.user))
  } else {
    // Store both token and user data in sessionStorage.
    sessionStorage.setItem('user', JSON.stringify(data.user))
    sessionStorage.setItem('token', data.access_token)
  }

  // Redirect to the appropriate dashboard
  router.push(data.user.role === 'admin' ? '/admin' : '/dashboard')
}

/**
 * Clears all authentication data from state and storage.
 */
async function logout(): Promise<void> {
  // Clear state
  state.user = null
  state.token = null
  state.isAuthenticated = false

  // Clear storage
  localStorage.removeItem('user')
  sessionStorage.removeItem('user')
  sessionStorage.removeItem('token')

  // Clear axios header
  delete axios.defaults.headers.common['Authorization']

  // Tell backend to clear the auth cookie, just in case
  try {
    await axios.post('/api/auth/logout')
  } catch (error) {
    console.error('Logout API call failed:', error)
  }

  // Redirect to login page
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login' })
  }
}

// COMPOSABLE (the hook to use in components)
export function useAuth() {
  return {
    // Use readonly to prevent direct state mutation from components
    authState: readonly(state),
    initAuth,
    login,
    logout,
  }
}
