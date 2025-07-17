<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

// useRoute provides access to the current route object
const route = useRoute()

// This computed property determines which tab should be active
// based on the URL path. It makes the component reactive to URL changes.
const activeTab = computed(() => {
  // Assuming your routes are named 'login' and 'register'
  if (route.path.includes('/signup')) {
    return 'signup'
  }
  return 'login'
})

// --- FORM HANDLING ---
const loginForm = ref({
  email: '',
  password: '',
  rememberMe: false,
})

const signupForm = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  address: '',
  pin: '',
})

const handleLogin = () => {
  console.log('Logging in with:', loginForm.value)
  // TODO: Add API call to backend for login
}

const handleSignup = () => {
  console.log('Signing up with:', signupForm.value)
  // TODO: Add validation and API call to backend for signup
}

// --- TRANSITION HOOKS FOR SMOOTH HEIGHT ANIMATION ---
const onBeforeLeave = (el: Element) => {
  // Set the container's height to the leaving element's height
  // to prevent the container from collapsing during the transition.
  // @ts-ignore
  el.parentElement!.style.height = `${el.offsetHeight}px`
}

const onEnter = (el: Element) => {
  // Set the container's height to the new element's height
  // to trigger the CSS height transition.
  // @ts-ignore
  el.parentElement!.style.height = `${el.offsetHeight}px`
}

const onAfterEnter = (el: Element) => {
  // After the transition is done, set the height back to auto
  // so it can be responsive (e.g., on window resize).
  el.parentElement!.style.height = 'auto'
}
</script>

<template>
  <main class="d-grid vh-100 p-4 overflow-auto" style="place-items: center">
    <div class="form-container">
      <!-- Tab Navigation -->
      <ul class="nav nav-tabs" id="myTab" role="tablist">
        <li class="nav-item" role="presentation">
          <router-link to="/login" class="nav-link" :class="{ active: activeTab === 'login' }"
            >Login</router-link
          >
        </li>
        <li class="nav-item" role="presentation">
          <router-link to="/signup" class="nav-link" :class="{ active: activeTab === 'signup' }"
            >Sign Up</router-link
          >
        </li>
      </ul>

      <!-- Tab Content -->
      <div class="tab-content" id="myTabContent">
        <Transition
          name="form-fade"
          mode="out-in"
          @before-leave="onBeforeLeave"
          @enter="onEnter"
          @after-enter="onAfterEnter"
        >
          <!-- Login Pane -->
          <div
            v-if="activeTab === 'login'"
            class="tab-pane fade show active"
            id="login-tab-pane"
            key="login-form"
          >
            <h2 class="text-white">Welcome Back!</h2>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <input
                  type="email"
                  class="form-control"
                  id="loginEmail"
                  placeholder="Email Address"
                  v-model="loginForm.email"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  type="password"
                  class="form-control"
                  id="loginPassword"
                  placeholder="Password"
                  v-model="loginForm.password"
                  required
                />
              </div>
              <div class="d-flex justify-content-between align-items-center mb-4">
                <div class="form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="rememberMe"
                    v-model="loginForm.rememberMe"
                  />
                  <label class="form-check-label" for="rememberMe">Remember Me</label>
                </div>
                <div class="form-text">
                  <a href="#">Forgot Password?</a>
                </div>
              </div>
              <button type="submit" class="btn btn-custom">Login</button>
            </form>
          </div>

          <!-- Sign Up Pane -->
          <div
            v-else-if="activeTab === 'signup'"
            class="tab-pane fade show active"
            id="signup-tab-pane"
            key="signup-form"
          >
            <h2 class="text-white">Create Account</h2>
            <form @submit.prevent="handleSignup">
              <div class="mb-3">
                <input
                  type="text"
                  class="form-control"
                  id="signupName"
                  placeholder="Full Name"
                  v-model="signupForm.name"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  type="email"
                  class="form-control"
                  id="signupEmail"
                  placeholder="Email Address"
                  v-model="signupForm.email"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  type="password"
                  class="form-control"
                  id="signupPassword"
                  placeholder="Create Password"
                  v-model="signupForm.password"
                  required
                />
              </div>
              <div class="mb-3">
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  placeholder="Confirm Password"
                  v-model="signupForm.confirmPassword"
                  required
                />
              </div>
              <div class="mb-3">
                <textarea
                  class="form-control"
                  style="min-height: 100px"
                  id="signupAddress"
                  placeholder="Address"
                  rows="5"
                  v-model="signupForm.address"
                  required
                ></textarea>
              </div>
              <div class="mb-4">
                <input
                  type="number"
                  class="form-control"
                  id="signupPin"
                  placeholder="Pin Code"
                  v-model="signupForm.pin"
                  min="100000"
                  max="999999"
                  required
                />
              </div>
              <button type="submit" class="btn btn-custom">Sign Up</button>
            </form>
          </div>
        </Transition>
      </div>
    </div>
  </main>
</template>

<style scoped>
.form-container {
  background: var(--form-bg);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(40, 167, 69, 0.2);
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-container h2 {
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
  color: #ffffff;
}

.nav-tabs {
  border-bottom: 0;
  justify-content: center;
  margin-bottom: 30px;
}

.nav-tabs .nav-link {
  background: transparent;
  border: none;
  color: var(--text-color-muted);
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.nav-tabs .nav-link.active {
  background: rgba(40, 167, 69, 0.2);
  color: #ffffff;
  font-weight: 600;
}

.form-control {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 10px;
  height: 50px;
  color: var(--text-color);
  padding-left: 20px;
  transition: all 0.3s ease;
}

.form-control::placeholder {
  color: var(--text-color-muted);
}

.form-control:focus {
  background: var(--input-bg);
  color: #ffffff;
  border-color: var(--highlight-color);
  box-shadow: 0 0 15px rgba(32, 201, 151, 0.3);
}

.btn-custom {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--button-bg-start), var(--button-bg-end));
  border: none;
  font-weight: 600;
  color: white;
  transition: all 0.4s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-custom:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
  filter: brightness(1.15);
}

.form-check-label,
.form-text a {
  color: var(--text-color-muted);
  font-size: 0.9rem;
}

.form-text a {
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.form-text a:hover {
  color: var(--highlight-color);
  text-decoration: underline;
}

.tab-content {
  animation: slideUp 0.5s ease-in-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* --- Transition Styles --- */
/* These classes are used by the <Transition> component */
.form-fade-enter-active,
.form-fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.form-fade-enter-from,
.form-fade-leave-to {
  opacity: 0;
  transform: translateY(15px);
}

.tab-content {
  transition: height 0.3s ease;
}
</style>
