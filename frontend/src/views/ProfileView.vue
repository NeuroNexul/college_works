<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import type { RegisteredUser } from '@/types'
import axios from 'axios'
import {
  BRow,
  BCol,
  BCard,
  BCardBody,
  BButton,
  BForm,
  BFormGroup,
  BFormInput,
  BSpinner,
  BAlert,
} from 'bootstrap-vue-next'

const user = ref<RegisteredUser | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)
const isEditing = ref(false)
const isSubmitting = ref(false)

const formData = reactive({
  fullName: '',
  address: '',
  pinCode: '',
})

// API & Lifecycle
const fetchProfile = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await axios.get('/api/profile')
    user.value = response.data
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load your profile.'
  } finally {
    isLoading.value = false
  }
}
onMounted(fetchProfile)

// METHODS
const enterEditMode = () => {
  if (!user.value) return
  formData.fullName = user.value.fullName || ''
  formData.address = user.value.address || ''
  formData.pinCode = user.value.pinCode || ''
  isEditing.value = true
}

const handleUpdateProfile = async () => {
  isSubmitting.value = true
  try {
    const response = await axios.put('/api/profile', formData)
    user.value = response.data // Update display with fresh data from server
    isEditing.value = false // Exit edit mode on success
  } catch (err) {
    console.error(err)
    error.value = 'Failed to update profile. Please try again.'
    await fetchProfile()
  } finally {
    isSubmitting.value = false
  }
}

// TRANSITION HOOKS FOR SMOOTH HEIGHT ANIMATION
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
  <div class="profile-view">
    <!-- Loading and Error States -->
    <div v-if="isLoading" class="text-center py-5">...</div>
    <BAlert v-else-if="error" show variant="danger" class="text-center">{{ error }}</BAlert>

    <BRow v-else-if="user" class="g-4">
      <!-- Left Column: Profile Details & Edit Form -->
      <BCol lg="7">
        <BCard class="profile-card">
          <BCardBody>
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2 class="card-title">My Profile</h2>
              <BButton v-if="!isEditing" @click="enterEditMode" variant="outline-light">
                <i class="bi bi-pencil-square me-2"></i>Edit Profile
              </BButton>
            </div>

            <div class="tab-content">
              <Transition
                name="form-fade"
                mode="out-in"
                @before-leave="onBeforeLeave"
                @enter="onEnter"
                @after-enter="onAfterEnter"
              >
                <!-- Display Mode -->
                <div v-if="!isEditing" class="details-grid">
                  <dt>Full Name</dt>
                  <dd>{{ user.fullName || 'Not Set' }}</dd>
                  <dt>Email Address</dt>
                  <dd>{{ user.email }}</dd>
                  <dt>Address</dt>
                  <dd>{{ user.address || 'Not Set' }}</dd>
                  <dt>Pin Code</dt>
                  <dd>{{ user.pinCode || 'Not Set' }}</dd>
                </div>

                <!-- Editing Mode -->
                <BForm v-else @submit.prevent="handleUpdateProfile">
                  <BFormGroup label="Full Name" label-for="fullName" class="mb-3">
                    <BFormInput id="fullName" v-model="formData.fullName" />
                  </BFormGroup>
                  <BFormGroup label="Email Address" label-for="email" class="mb-3">
                    <BFormInput id="email" :model-value="user.email" disabled />
                  </BFormGroup>
                  <BFormGroup label="Address" label-for="address" class="mb-3">
                    <BFormInput id="address" v-model="formData.address" />
                  </BFormGroup>
                  <BFormGroup label="Pin Code" label-for="pinCode" class="mb-3">
                    <BFormInput id="pinCode" v-model="formData.pinCode" />
                  </BFormGroup>

                  <div class="d-flex justify-content-end mt-4">
                    <BButton variant="secondary" @click="isEditing = false" class="me-2"
                      >Cancel</BButton
                    >
                    <BButton
                      type="submit"
                      class="btn-primary-gradient"
                      variant="success"
                      :disabled="isSubmitting"
                    >
                      <BSpinner v-if="isSubmitting" small class="me-2" />Save Changes
                    </BButton>
                  </div>
                </BForm>
              </Transition>
            </div>
          </BCardBody>
        </BCard>
      </BCol>

      <!-- Right Column: Statistics -->
      <BCol lg="5">
        <div class="stats-grid">
          <BCard class="stat-card">
            <i class="bi bi-clock-history stat-icon"></i>
            <div class="stat-value">{{ user.totalBookings }}</div>
            <div class="stat-label">Total Bookings</div>
          </BCard>
          <BCard class="stat-card">
            <i class="bi bi-car-front-fill stat-icon"></i>
            <div class="stat-value">{{ user.activeBookings }}</div>
            <div class="stat-label">Active Sessions</div>
          </BCard>
          <BCard class="stat-card wide">
            <i class="bi bi-wallet2 stat-icon"></i>
            <div class="stat-value">${{ user.totalSpent.toFixed(2) }}</div>
            <div class="stat-label">Total Amount Spent</div>
          </BCard>
        </div>
      </BCol>
    </BRow>
  </div>
</template>

<style scoped>
.profile-view {
  width: 100%;
  max-width: 112rem;
  margin: 0 auto;
  padding: 2rem 4rem;
}

.profile-card,
.stat-card {
  background-color: var(--form-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
}
.card-title {
  color: var(--text-color);
  font-weight: 600;
}

.details-grid {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 1.25rem;
}
.details-grid dt {
  color: var(--text-color-muted);
  font-weight: 500;
}
.details-grid dd {
  color: var(--text-color);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.stat-card {
  padding: 1.5rem;
  text-align: center;
}
.stat-card.wide {
  grid-column: 1 / -1;
} /* Make this card span full width */

.stat-icon {
  font-size: 2.5rem;
  color: var(--highlight-color);
  margin-bottom: 0.5rem;
}
.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.2;
}
.stat-label {
  font-size: 0.9rem;
  color: var(--text-color-muted);
}

.btn-outline-light {
  color: var(--text-color-muted);
  border-color: var(--input-border);
}
.btn-outline-light:hover {
  color: var(--text-color);
  background-color: rgba(40, 167, 69, 0.2);
  border-color: var(--highlight-color);
}

/* Transition Styles */
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
  /* transform: translateY(15px); */
}

.tab-content {
  transition: height 0.3s ease;
}
</style>
