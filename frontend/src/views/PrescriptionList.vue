<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Prescriptions</h1>
      <router-link to="/prescriptions/add" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">Add Prescription</router-link>
    </div>
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    </div>
    <div v-else class="glass rounded-2xl shadow-lg p-6">
      <p v-if="prescriptions.length === 0" class="text-center text-gray-500 py-8">No prescriptions found</p>
      <div v-else class="space-y-4">
        <div
          v-for="prescription in prescriptions"
          :key="prescription.id"
          @click="showPrescriptionDetails(prescription)"
          class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <h3 class="font-semibold">{{ prescription.medication_name }}</h3>
          <p class="text-sm text-gray-600">Patient: {{ prescription.patient_name }}</p>
          <p class="text-sm text-gray-600">Prescriber: {{ prescription.prescriber_name }}</p>
          <span :class="['inline-block px-2 py-1 text-xs rounded', prescription.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700']">
            {{ prescription.status }}
          </span>
        </div>
      </div>
    </div>

    <!-- Prescription Details Modal -->
    <div
      v-if="selectedPrescription"
      @click="closePrescriptionDetails"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <div
        @click.stop
        class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 class="text-2xl font-bold text-gray-900">Prescription Details</h2>
          <button
            @click="closePrescriptionDetails"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-6">
          <!-- Medication Information -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Medication Information</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">Medication Name</p>
                <p class="font-medium text-gray-900">{{ selectedPrescription.medication_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Status</p>
                <span :class="['inline-block px-2 py-1 text-xs rounded', selectedPrescription.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700']">
                  {{ selectedPrescription.status }}
                </span>
              </div>
            </div>
          </div>

          <!-- Dosage Information -->
          <div v-if="selectedPrescription.dosage_text">
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Dosage Instructions</h3>
            <p class="text-gray-700">{{ selectedPrescription.dosage_text }}</p>
          </div>

          <!-- Patient Information -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Patient Information</h3>
            <p class="text-gray-700">{{ selectedPrescription.patient_name }}</p>
          </div>

          <!-- Prescriber Information -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Prescriber Information</h3>
            <p class="text-gray-700">{{ selectedPrescription.prescriber_name }}</p>
          </div>

          <!-- Dates -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Prescription Dates</h3>
            <div class="grid grid-cols-2 gap-4">
              <div v-if="selectedPrescription.authored_on">
                <p class="text-sm text-gray-500">Authored On</p>
                <p class="text-gray-900">{{ formatDate(selectedPrescription.authored_on) }}</p>
              </div>
              <div v-if="selectedPrescription.dosage_period_start">
                <p class="text-sm text-gray-500">Period Start</p>
                <p class="text-gray-900">{{ formatDate(selectedPrescription.dosage_period_start) }}</p>
              </div>
              <div v-if="selectedPrescription.dosage_period_end">
                <p class="text-sm text-gray-500">Period End</p>
                <p class="text-gray-900">{{ formatDate(selectedPrescription.dosage_period_end) }}</p>
              </div>
            </div>
          </div>

          <!-- Additional Notes -->
          <div v-if="selectedPrescription.note">
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Additional Notes</h3>
            <p class="text-gray-700">{{ selectedPrescription.note }}</p>
          </div>
        </div>

        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            @click="closePrescriptionDetails"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePrescriptionStore } from '../stores/prescription'
import { storeToRefs } from 'pinia'

const prescriptionStore = usePrescriptionStore()
const { prescriptions, loading } = storeToRefs(prescriptionStore)

const selectedPrescription = ref(null)

onMounted(() => {
  prescriptionStore.fetchPrescriptions()
})

const showPrescriptionDetails = (prescription) => {
  selectedPrescription.value = prescription
}

const closePrescriptionDetails = () => {
  selectedPrescription.value = null
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>
