<script lang="ts" setup>
import { ref, reactive, watch, computed } from 'vue'
import type { ParkingLot } from '@/types'
import {
  BForm,
  BRow,
  BCol,
  BFormGroup,
  BFormInput,
  BFormInvalidFeedback,
  BButton,
  BSpinner,
} from 'bootstrap-vue-next'

// Define the shape of the data this form handles
export type LotFormData = Omit<ParkingLot, 'id' | 'occupied_spots_count' | 'spots'>

// PROPS
interface Props {
  lotData: ParkingLot | null
  isLoading: boolean
}
const props = defineProps<Props>()

// EMITS
const emit = defineEmits<{
  (e: 'submit', formData: LotFormData, id: number | null): void
  (e: 'cancel'): void
}>()

// STATE
const initialFormState: LotFormData = {
  name: '',
  address: '',
  pin_code: '',
  price_per_hour: 0,
  total_spots: 10,
}

const formData = reactive<LotFormData>({ ...initialFormState })
const validated = ref(false)

const isEditing = computed(() => !!props.lotData)

// LOGIC
// Watch for changes in the prop to populate or reset the form
watch(
  () => props.lotData,
  (newLot) => {
    validated.value = false // Reset validation state
    if (newLot) {
      // Populate form for editing
      formData.name = newLot.name
      formData.address = newLot.address
      formData.pin_code = newLot.pin_code
      formData.price_per_hour = newLot.price_per_hour
      formData.total_spots = newLot.total_spots
    } else {
      // Reset form for adding a new lot
      Object.assign(formData, initialFormState)
    }
  },
  { immediate: true },
)

const handleSubmit = (event: Event) => {
  const form = event.currentTarget as HTMLFormElement
  validated.value = true

  if (form.checkValidity() === false) {
    event.preventDefault()
    event.stopPropagation()
    return
  }

  // If form is valid, emit the data to the parent
  emit('submit', { ...formData }, props.lotData?.id || null)
}
</script>

<template>
  <BForm @submit.prevent="handleSubmit" novalidate :validated="validated">
    <BRow class="g-3">
      <BCol md="12">
        <BFormGroup label="Lot Name" label-for="lot-name">
          <BFormInput
            id="lot-name"
            v-model="formData.name"
            required
            placeholder="e.g., Downtown Plaza Lot"
          />
          <BFormInvalidFeedback>Lot name is required.</BFormInvalidFeedback>
        </BFormGroup>
      </BCol>

      <BCol md="12">
        <BFormGroup label="Address" label-for="lot-address">
          <BFormInput
            id="lot-address"
            v-model="formData.address"
            required
            placeholder="123 Main St, Anytown"
          />
          <BFormInvalidFeedback>Address is required.</BFormInvalidFeedback>
        </BFormGroup>
      </BCol>

      <BCol md="6">
        <BFormGroup label="Pin Code" label-for="lot-pincode">
          <BFormInput id="lot-pincode" v-model="formData.pin_code" required />
          <BFormInvalidFeedback>Pin Code is required.</BFormInvalidFeedback>
        </BFormGroup>
      </BCol>

      <BCol md="6">
        <BFormGroup label="Price per Hour ($)" label-for="lot-price">
          <BFormInput
            id="lot-price"
            type="number"
            v-model.number="formData.price_per_hour"
            required
            min="0"
            step="0.01"
          />
          <BFormInvalidFeedback>Please enter a valid price.</BFormInvalidFeedback>
        </BFormGroup>
      </BCol>

      <BCol md="12">
        <BFormGroup
          label="Total Number of Spots"
          label-for="lot-spots"
          description="Note: You cannot change the number of spots after creation."
        >
          <BFormInput
            id="lot-spots"
            type="number"
            v-model.number="formData.total_spots"
            required
            min="1"
          />
          <BFormInvalidFeedback>Must be at least 1 spot.</BFormInvalidFeedback>
        </BFormGroup>
      </BCol>
    </BRow>

    <div class="d-flex justify-content-end mt-4">
      <BButton type="button" variant="secondary" @click="$emit('cancel')" class="me-2">
        Cancel
      </BButton>
      <BButton type="submit" class="btn-primary-gradient" :disabled="isLoading">
        <BSpinner v-if="isLoading" small class="me-2"></BSpinner>
        {{ isEditing ? 'Save Changes' : 'Create Lot' }}
      </BButton>
    </div>
  </BForm>
</template>

<style scoped>
/* The global modal styles will handle most of the theming.
   These are just for fine-tuning. */
.form-group label {
  font-weight: 500;
  color: var(--text-color-muted);
  margin-bottom: 0.5rem;
}
.form-group small {
  color: var(--text-color-muted) !important;
  opacity: 0.7;
}

.btn-primary-gradient {
  background: linear-gradient(90deg, var(--button-bg-start), var(--button-bg-end));
  color: var(--text-color) !important;
  border: none;
  font-weight: 600;
  padding: 0.6rem 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(32, 201, 151, 0.2);
}
.btn-primary-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(32, 201, 151, 0.3);
}

.btn-secondary {
  background-color: var(--input-bg);
  border-color: var(--input-border);
  color: var(--text-color-muted);
}
.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: var(--highlight-color);
  color: var(--text-color);
}
</style>
