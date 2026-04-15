<script setup lang="ts"></script>

<template>
  <div class="not-found-container d-flex align-items-center justify-content-center text-center">
    <transition name="fade-in-up" appear>
      <div class="not-found-card">
        <h1 class="display-1 fw-bolder">404</h1>
        <h2 class="mb-3 fw-light">Page Not Found</h2>
        <p class="text-color-muted mb-4 px-3">
          Oops! It seems you've taken a wrong turn. The page you're looking for has either been
          moved or doesn't exist.
        </p>
        <router-link to="/" class="btn btn-primary-gradient btn-lg">
          <i class="bi bi-house-door-fill me-2"></i>
          Return to Homepage
        </router-link>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* Ensure you have Bootstrap Icons installed or linked for the icon */
/* npm install bootstrap-icons */
@import 'bootstrap-icons/font/bootstrap-icons.css';

.not-found-container {
  min-height: 100vh;
}

.not-found-card {
  background-color: var(--form-bg);
  padding: 3rem 2rem;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(40, 167, 69, 0.2);
  max-width: 550px;
  width: 90%;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
}

h1.display-1 {
  font-size: clamp(6rem, 25vw, 10rem); /* Responsive font size */
  color: var(--highlight-color);
  text-shadow:
    0 0 15px rgba(32, 201, 151, 0.4),
    0 0 25px rgba(32, 201, 151, 0.2);
  margin-bottom: 0;
  line-height: 1;
}

h2 {
  color: var(--text-color);
  font-weight: 400;
  letter-spacing: 1px;
}

p.text-color-muted {
  color: var(--text-color-muted);
  font-size: 1rem;
}

.btn-primary-gradient {
  background: linear-gradient(90deg, var(--button-bg-start), var(--button-bg-end));
  border: none;
  color: white;
  padding: 0.8rem 2.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary-gradient:hover,
.btn-primary-gradient:focus {
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(32, 201, 151, 0.4);
}

/* Animation using Vue's <Transition> */
.fade-in-up-enter-active,
.fade-in-up-leave-active {
  transition:
    opacity 0.6s ease,
    transform 0.6s ease;
}

.fade-in-up-enter-from,
.fade-in-up-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style>
