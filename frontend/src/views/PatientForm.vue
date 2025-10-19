<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Patient' : 'Add New Patient' }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ isEditMode ? 'Update patient information' : 'Create a new FHIR-compliant patient record' }}
        </p>
      </div>
      <router-link
        to="/"
        class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
      >
        <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to List
      </router-link>
    </div>

    <!-- Error Alert -->
    <div
      v-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4 animate-scale-in"
    >
      <div class="flex items-center">
        <svg class="h-5 w-5 text-danger-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-danger-700">{{ error }}</p>
      </div>
    </div>

    <!-- Patient Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Personal Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Personal Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- First Name -->
          <div>
            <label for="givenName" class="block text-sm font-medium text-gray-700 mb-1">
              First Name <span class="text-danger-500">*</span>
            </label>
            <input
              id="givenName"
              v-model="formData.givenName"
              type="text"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="John"
            />
          </div>

          <!-- Middle Name -->
          <div>
            <label for="middleName" class="block text-sm font-medium text-gray-700 mb-1">
              Middle Name
            </label>
            <input
              id="middleName"
              v-model="formData.middleName"
              type="text"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Michael"
            />
          </div>

          <!-- Last Name -->
          <div>
            <label for="familyName" class="block text-sm font-medium text-gray-700 mb-1">
              Last Name <span class="text-danger-500">*</span>
            </label>
            <input
              id="familyName"
              v-model="formData.familyName"
              type="text"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Doe"
            />
          </div>

          <!-- Gender -->
          <div>
            <label for="gender" class="block text-sm font-medium text-gray-700 mb-1">
              Gender <span class="text-danger-500">*</span>
            </label>
            <select
              id="gender"
              v-model="formData.gender"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            >
              <option value="" disabled>Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>

          <!-- Birth Date -->
          <div>
            <label for="birthDate" class="block text-sm font-medium text-gray-700 mb-1">
              Birth Date <span class="text-danger-500">*</span>
            </label>
            <input
              id="birthDate"
              v-model="formData.birthDate"
              type="date"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            />
          </div>

          <!-- Active Status -->
          <div class="flex items-center">
            <input
              id="active"
              v-model="formData.active"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="active" class="ml-2 block text-sm text-gray-700">
              Active Patient
            </label>
          </div>
        </div>
      </div>

      <!-- Contact Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Contact Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="john.doe@example.com"
              />
            </div>
          </div>

          <!-- Phone -->
          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
              Phone Number
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <input
                id="phone"
                v-model="formData.phone"
                type="tel"
                class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="+1-555-123-4567"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Address Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Address
          </h3>
        </div>

        <div class="space-y-6">
          <!-- Street Address -->
          <div>
            <label for="addressLine" class="block text-sm font-medium text-gray-700 mb-1">
              Street Address
            </label>
            <input
              id="addressLine"
              v-model="formData.addressLine"
              type="text"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="123 Main Street, Apt 4B"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- City -->
            <div>
              <label for="city" class="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                id="city"
                v-model="formData.city"
                type="text"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="New York"
              />
            </div>

            <!-- State/Province -->
            <div>
              <label for="state" class="block text-sm font-medium text-gray-700 mb-1">
                State/Province
              </label>
              <input
                id="state"
                v-model="formData.state"
                type="text"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="NY"
              />
            </div>

            <!-- Postal Code -->
            <div>
              <label for="postalCode" class="block text-sm font-medium text-gray-700 mb-1">
                Postal Code
              </label>
              <input
                id="postalCode"
                v-model="formData.postalCode"
                type="text"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="10001"
              />
            </div>

            <!-- Country -->
            <div>
              <label for="country" class="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <input
                id="country"
                v-model="formData.country"
                type="text"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="USA"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <router-link
          to="/"
          class="px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          Cancel
        </router-link>
        <button
          type="submit"
          :disabled="loading"
          class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <svg
            v-if="loading"
            class="animate-spin h-5 w-5 mr-2 text-white"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ loading ? 'Saving...' : (isEditMode ? 'Update Patient' : 'Create Patient') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import { buildFHIRPatient, extractFormData } from '../services/api'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()
const patientStore = usePatientStore()
const { loading, error } = storeToRefs(patientStore)

const isEditMode = computed(() => !!route.params.id)

const formData = ref({
  givenName: '',
  middleName: '',
  familyName: '',
  gender: '',
  birthDate: '',
  email: '',
  phone: '',
  addressLine: '',
  city: '',
  state: '',
  postalCode: '',
  country: '',
  active: true,
})

onMounted(async () => {
  if (isEditMode.value) {
    try {
      const patient = await patientStore.fetchPatientById(route.params.id)
      formData.value = extractFormData(patient)
    } catch (err) {
      console.error('Failed to load patient:', err)
      router.push('/')
    }
  }
})

const handleSubmit = async () => {
  try {
    const fhirPatient = buildFHIRPatient(formData.value)

    if (isEditMode.value) {
      await patientStore.updatePatient(route.params.id, fhirPatient)
    } else {
      await patientStore.createPatient(fhirPatient)
    }

    router.push('/')
  } catch (err) {
    console.error('Failed to save patient:', err)
  }
}
</script>
