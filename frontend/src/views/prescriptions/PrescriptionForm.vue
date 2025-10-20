<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Prescription' : 'Add New Prescription' }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ isEditMode ? 'Update prescription information' : 'Create a new FHIR-compliant medication request' }}
        </p>
      </div>
      <router-link
        to="/prescriptions"
        class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
      >
        <svg
          class="h-5 w-5 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
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
        <svg
          class="h-5 w-5 text-danger-500 mr-2"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clip-rule="evenodd"
          />
        </svg>
        <p class="text-sm font-medium text-danger-700">
          {{ error }}
        </p>
      </div>
    </div>

    <!-- Prescription Form -->
    <form
      class="space-y-6"
      @submit.prevent="handleSubmit"
    >
      <!-- Medication Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
              />
            </svg>
            Medication Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Medication Name -->
          <div>
            <label
              for="medicationName"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
              Medication Name <span class="text-danger-500">*</span>
            </label>
            <input
              id="medicationName"
              v-model="formData.medicationName"
              type="text"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Aspirin"
            >
          </div>

          <!-- Status -->
          <div>
            <label
              for="status"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
              Status <span class="text-danger-500">*</span>
            </label>
            <select
              id="status"
              v-model="formData.status"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            >
              <option
                value=""
                disabled
              >
                Select status
              </option>
              <option value="active">
                Active
              </option>
              <option value="on-hold">
                On Hold
              </option>
              <option value="cancelled">
                Cancelled
              </option>
              <option value="completed">
                Completed
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Patient and Prescriber Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            Patient & Prescriber
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Patient -->
          <div>
            <label
              for="patientId"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
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

          <!-- Prescriber (Practitioner) -->
          <div>
            <label
              for="practitionerId"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
              Prescriber <span class="text-danger-500">*</span>
            </label>
            <SearchableSelect
              v-model="formData.practitionerId"
              :options="practitionerOptions"
              label-key="label"
              value-key="value"
              placeholder="Select prescriber..."
              required
            />
          </div>
        </div>
      </div>

      <!-- Dosage Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Dosage Instructions
          </h3>
        </div>

        <div class="space-y-6">
          <!-- Dosage Text -->
          <div>
            <label
              for="dosageText"
              class="block text-sm font-medium text-gray-700 mb-1"
            >
              Dosage Instructions
            </label>
            <textarea
              id="dosageText"
              v-model="formData.dosageText"
              rows="3"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Take one tablet twice daily with food"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Period Start -->
            <div>
              <label
                for="periodStart"
                class="block text-sm font-medium text-gray-700 mb-1"
              >
                Period Start
              </label>
              <input
                id="periodStart"
                v-model="formData.periodStart"
                type="date"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              >
            </div>

            <!-- Period End -->
            <div>
              <label
                for="periodEnd"
                class="block text-sm font-medium text-gray-700 mb-1"
              >
                Period End
              </label>
              <input
                id="periodEnd"
                v-model="formData.periodEnd"
                type="date"
                class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              >
            </div>
          </div>
        </div>
      </div>

      <!-- Notes Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
              />
            </svg>
            Additional Notes
          </h3>
        </div>

        <div>
          <label
            for="note"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            Notes
          </label>
          <textarea
            id="note"
            v-model="formData.note"
            rows="4"
            class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            placeholder="Any additional notes about this prescription..."
          />
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <router-link
          to="/prescriptions"
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
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>{{ loading ? 'Saving...' : (isEditMode ? 'Update Prescription' : 'Create Prescription') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePrescriptionStore } from '../../stores/prescription'
import { usePatientStore } from '../../stores/patient'
import { usePractitionerStore } from '../../stores/practitioner'
import { storeToRefs } from 'pinia'
import { useToast } from 'vue-toastification'
import SearchableSelect from '../../components/SearchableSelect.vue'
import type { MedicationRequest } from '../../types/fhir'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const prescriptionStore = usePrescriptionStore()
const patientStore = usePatientStore()
const practitionerStore = usePractitionerStore()

const { loading, error } = storeToRefs(prescriptionStore)

const isEditMode = computed(() => !!route.params.id)

const formData = ref({
  medicationName: '',
  status: '',
  patientId: '',
  practitionerId: '',
  dosageText: '',
  periodStart: '',
  periodEnd: '',
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
      const prescription = await prescriptionStore.fetchPrescriptionById(route.params.id as string)
      // Extract form data from FHIR resource
      formData.value = {
        medicationName: prescription.medicationCodeableConcept?.text || '',
        status: prescription.status,
        patientId: prescription.subject?.reference?.replace('Patient/', '') || '',
        practitionerId: prescription.requester?.reference?.replace('Practitioner/', '') || '',
        dosageText: prescription.dosageInstruction?.[0]?.text || '',
        periodStart: prescription.dosageInstruction?.[0]?.timing?.repeat?.boundsPeriod?.start || '',
        periodEnd: prescription.dosageInstruction?.[0]?.timing?.repeat?.boundsPeriod?.end || '',
        note: prescription.note?.[0]?.text || ''
      }
    } catch (err) {
      console.error('Failed to load prescription:', err)
      router.push('/prescriptions')
    }
  }
})

const handleSubmit = async (): Promise<void> => {
  try {
    // Build FHIR MedicationRequest
    const prescription: MedicationRequest = {
      resourceType: 'MedicationRequest',
      status: formData.value.status as MedicationRequest['status'],
      intent: 'order',
      medicationCodeableConcept: {
        text: formData.value.medicationName
      },
      subject: {
        reference: `Patient/${formData.value.patientId}`
      },
      requester: {
        reference: `Practitioner/${formData.value.practitionerId}`
      }
    }

    if (formData.value.dosageText || formData.value.periodStart || formData.value.periodEnd) {
      prescription.dosageInstruction = [{
        text: formData.value.dosageText
      }]

      if (formData.value.periodStart || formData.value.periodEnd) {
        const dosageInstruction = prescription.dosageInstruction?.[0]
        if (dosageInstruction) {
          dosageInstruction.timing = {
            repeat: {
              boundsPeriod: {
                start: formData.value.periodStart,
                end: formData.value.periodEnd
              }
            }
          }
        }
      }
    }

    if (formData.value.note) {
      prescription.note = [{
        text: formData.value.note
      }]
    }

    if (isEditMode.value && route.params.id) {
      await prescriptionStore.updatePrescription(route.params.id as string, prescription)
      toast.success('Prescription updated successfully')
    } else {
      await prescriptionStore.createPrescription(prescription)
      toast.success('Prescription created successfully')
    }

    router.push('/prescriptions')
  } catch (err) {
    console.error('Failed to save prescription:', err)
    toast.error(isEditMode.value ? 'Failed to update prescription' : 'Failed to create prescription')
  }
}
</script>
