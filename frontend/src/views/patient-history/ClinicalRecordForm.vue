<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Clinical Record' : 'Add New Clinical Record' }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ isEditMode ? 'Update clinical record information' : 'Create a new FHIR-compliant observation' }}
        </p>
      </div>
      <router-link
        to="/patient-history"
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

    <!-- Clinical Record Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Record Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Title/Code -->
          <div class="md:col-span-2">
            <label for="title" class="block text-sm font-medium text-gray-700 mb-1">
              Title/Description <span class="text-danger-500">*</span>
            </label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="e.g., Blood Pressure, Temperature, Diagnosis"
            />
          </div>

          <!-- Status -->
          <div>
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">
              Status <span class="text-danger-500">*</span>
            </label>
            <select
              id="status"
              v-model="formData.status"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            >
              <option value="" disabled>Select status</option>
              <option value="registered">Registered</option>
              <option value="preliminary">Preliminary</option>
              <option value="final">Final</option>
              <option value="amended">Amended</option>
            </select>
          </div>

          <!-- Recorded Date -->
          <div>
            <label for="effectiveDateTime" class="block text-sm font-medium text-gray-700 mb-1">
              Recorded Date <span class="text-danger-500">*</span>
            </label>
            <input
              id="effectiveDateTime"
              v-model="formData.effectiveDateTime"
              type="datetime-local"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            />
          </div>
        </div>
      </div>

      <!-- Patient & Practitioner Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Patient & Recorded By
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Patient -->
          <div>
            <label for="patientId" class="block text-sm font-medium text-gray-700 mb-1">
              Patient <span class="text-danger-500">*</span>
            </label>
            <SearchableSelect
              v-model="formData.patientId"
              :options="patientOptions"
              label-key="label"
              value-key="value"
              placeholder="Select patient..."
              required
            />
          </div>

          <!-- Recorded By (Practitioner) -->
          <div>
            <label for="performerId" class="block text-sm font-medium text-gray-700 mb-1">
              Recorded By
            </label>
            <SearchableSelect
              v-model="formData.performerId"
              :options="practitionerOptions"
              label-key="label"
              value-key="value"
              placeholder="Select practitioner..."
            />
          </div>
        </div>
      </div>

      <!-- Value Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Observation Value
          </h3>
        </div>

        <div class="space-y-6">
          <!-- Value Type Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">Value Type</label>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label class="relative flex items-center p-4 border-2 rounded-xl cursor-pointer hover:bg-gray-50 transition-colors" :class="formData.valueType === 'quantity' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'">
                <input type="radio" v-model="formData.valueType" value="quantity" class="sr-only" />
                <div>
                  <p class="font-medium text-gray-900">Quantity</p>
                  <p class="text-xs text-gray-500">Numeric measurement</p>
                </div>
              </label>
              <label class="relative flex items-center p-4 border-2 rounded-xl cursor-pointer hover:bg-gray-50 transition-colors" :class="formData.valueType === 'string' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'">
                <input type="radio" v-model="formData.valueType" value="string" class="sr-only" />
                <div>
                  <p class="font-medium text-gray-900">Text</p>
                  <p class="text-xs text-gray-500">Text description</p>
                </div>
              </label>
              <label class="relative flex items-center p-4 border-2 rounded-xl cursor-pointer hover:bg-gray-50 transition-colors" :class="formData.valueType === 'none' ? 'border-primary-500 bg-primary-50' : 'border-gray-200'">
                <input type="radio" v-model="formData.valueType" value="none" class="sr-only" />
                <div>
                  <p class="font-medium text-gray-900">None</p>
                  <p class="text-xs text-gray-500">No value</p>
                </div>
              </label>
            </div>
          </div>

          <!-- Quantity Value -->
          <div v-if="formData.valueType === 'quantity'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label for="valueQuantity" class="block text-sm font-medium text-gray-700 mb-1">
                Value
              </label>
              <input
                id="valueQuantity"
                v-model.number="formData.valueQuantity"
                type="number"
                step="any"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="e.g., 120"
              />
            </div>
            <div>
              <label for="valueUnit" class="block text-sm font-medium text-gray-700 mb-1">
                Unit
              </label>
              <input
                id="valueUnit"
                v-model="formData.valueUnit"
                type="text"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="e.g., mmHg, °C, kg"
              />
            </div>
          </div>

          <!-- String Value -->
          <div v-if="formData.valueType === 'string'">
            <label for="valueString" class="block text-sm font-medium text-gray-700 mb-1">
              Value
            </label>
            <textarea
              id="valueString"
              v-model="formData.valueString"
              rows="3"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Enter text value..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Notes Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Additional Notes
          </h3>
        </div>

        <div>
          <label for="note" class="block text-sm font-medium text-gray-700 mb-1">
            Clinical Notes
          </label>
          <textarea
            id="note"
            v-model="formData.note"
            rows="4"
            class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            placeholder="Any additional clinical notes..."
          ></textarea>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <router-link
          to="/patient-history"
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
          <span>{{ loading ? 'Saving...' : (isEditMode ? 'Update Record' : 'Create Record') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useClinicalRecordStore } from '../../stores/clinicalRecord'
import { usePatientStore } from '../../stores/patient'
import { usePractitionerStore } from '../../stores/practitioner'
import { storeToRefs } from 'pinia'
import SearchableSelect from '../../components/SearchableSelect.vue'
import type { Observation } from '../../types/fhir'

const router = useRouter()
const route = useRoute()
const recordStore = useClinicalRecordStore()
const patientStore = usePatientStore()
const practitionerStore = usePractitionerStore()

const { loading, error } = storeToRefs(recordStore)

const isEditMode = computed(() => !!route.params.id)

const formData = ref({
  title: '',
  status: '',
  effectiveDateTime: new Date().toISOString().slice(0, 16),
  patientId: '',
  performerId: '',
  valueType: 'quantity' as 'quantity' | 'string' | 'none',
  valueQuantity: 0,
  valueUnit: '',
  valueString: '',
  note: ''
})

const patientOptions = computed(() => {
  return patientStore.patients.map(p => ({
    label: `${p.name?.[0]?.given?.[0] || ''} ${p.name?.[0]?.family || ''}`.trim(),
    value: p.id || ''
  }))
})

const practitionerOptions = computed(() => {
  return practitionerStore.practitioners.map(p => ({
    label: `${p.name?.[0]?.given?.[0] || ''} ${p.name?.[0]?.family || ''}`.trim(),
    value: p.id || ''
  }))
})

onMounted(async () => {
  // Load patients and practitioners for dropdowns
  await Promise.all([
    patientStore.fetchPatients(),
    practitionerStore.fetchPractitioners()
  ])

  if (isEditMode.value && route.params.id) {
    try {
      const record = await recordStore.fetchRecordById(route.params.id as string)

      // Determine value type
      let valueType: 'quantity' | 'string' | 'none' = 'none'
      if (record.valueQuantity) valueType = 'quantity'
      else if (record.valueString) valueType = 'string'

      // Extract form data from FHIR resource
      formData.value = {
        title: record.code?.text || '',
        status: record.status,
        effectiveDateTime: record.effectiveDateTime?.slice(0, 16) || new Date().toISOString().slice(0, 16),
        patientId: record.subject?.reference?.replace('Patient/', '') || '',
        performerId: record.performer?.[0]?.reference?.replace('Practitioner/', '') || '',
        valueType: valueType,
        valueQuantity: record.valueQuantity?.value || 0,
        valueUnit: record.valueQuantity?.unit || '',
        valueString: record.valueString || '',
        note: record.note?.[0]?.text || ''
      }
    } catch (err) {
      console.error('Failed to load clinical record:', err)
      router.push('/patient-history')
    }
  }
})

const handleSubmit = async (): Promise<void> => {
  try {
    // Build FHIR Observation
    const observation: Observation = {
      resourceType: 'Observation',
      status: formData.value.status as Observation['status'],
      code: {
        text: formData.value.title
      },
      subject: {
        reference: `Patient/${formData.value.patientId}`
      },
      effectiveDateTime: formData.value.effectiveDateTime
    }

    // Add performer if specified
    if (formData.value.performerId) {
      observation.performer = [{
        reference: `Practitioner/${formData.value.performerId}`
      }]
    }

    // Add value based on type
    if (formData.value.valueType === 'quantity') {
      observation.valueQuantity = {
        value: formData.value.valueQuantity,
        unit: formData.value.valueUnit
      }
    } else if (formData.value.valueType === 'string') {
      observation.valueString = formData.value.valueString
    }

    // Add notes
    if (formData.value.note) {
      observation.note = [{
        text: formData.value.note
      }]
    }

    if (isEditMode.value && route.params.id) {
      await recordStore.updateRecord(route.params.id as string, observation)
    } else {
      await recordStore.createRecord(observation)
    }

    router.push('/patient-history')
  } catch (err) {
    console.error('Failed to save clinical record:', err)
  }
}
</script>
