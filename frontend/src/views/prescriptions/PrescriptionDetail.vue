<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Prescription Details</h1>
        <p class="mt-1 text-sm text-gray-500">View detailed prescription information</p>
      </div>
      <div class="flex items-center space-x-3">
        <router-link
          :to="`/prescriptions/edit/${$route.params.id}`"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit
        </router-link>
        <router-link
          to="/prescriptions"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to List
        </router-link>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading prescription details...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4"
    >
      <div class="flex items-center">
        <svg class="h-5 w-5 text-danger-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-danger-700">{{ error }}</p>
      </div>
    </div>

    <!-- Prescription Details -->
    <div v-else-if="prescription" class="space-y-6">
      <!-- Medication Information -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            Medication Information
          </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p class="text-sm text-gray-500">Medication Name</p>
            <p class="mt-1 text-lg font-medium text-gray-900">{{ prescription.medicationCodeableConcept?.text || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Status</p>
            <span
              class="inline-flex mt-1 px-3 py-1 text-sm font-semibold rounded-full"
              :class="{
                'bg-success-100 text-success-700': prescription.status === 'active',
                'bg-warning-100 text-warning-700': prescription.status === 'on-hold',
                'bg-danger-100 text-danger-700': prescription.status === 'cancelled',
                'bg-gray-100 text-gray-700': prescription.status === 'completed'
              }"
            >
              {{ prescription.status }}
            </span>
          </div>
          <div>
            <p class="text-sm text-gray-500">FHIR Resource ID</p>
            <p class="mt-1 text-sm font-mono text-gray-900">{{ prescription.id || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Intent</p>
            <p class="mt-1 text-sm text-gray-900">{{ prescription.intent || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <!-- Patient & Prescriber Information -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Patient & Prescriber
          </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p class="text-sm text-gray-500">Patient</p>
            <p class="mt-1 text-lg font-medium text-gray-900">{{ prescription.subject?.display || prescription.subject?.reference || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Prescriber</p>
            <p class="mt-1 text-lg font-medium text-gray-900">{{ prescription.requester?.display || prescription.requester?.reference || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <!-- Dosage Information -->
      <div v-if="prescription.dosageInstruction && prescription.dosageInstruction.length > 0" class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Dosage Instructions
          </h3>
        </div>
        <div class="space-y-4">
          <div v-for="(dosage, index) in prescription.dosageInstruction" :key="index">
            <p v-if="dosage.text" class="text-gray-700 mb-4">{{ dosage.text }}</p>
            <div v-if="dosage.timing?.repeat?.boundsPeriod" class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
              <div v-if="dosage.timing.repeat.boundsPeriod.start">
                <p class="text-sm text-gray-500">Period Start</p>
                <p class="mt-1 text-gray-900">{{ formatDate(dosage.timing.repeat.boundsPeriod.start) }}</p>
              </div>
              <div v-if="dosage.timing.repeat.boundsPeriod.end">
                <p class="text-sm text-gray-500">Period End</p>
                <p class="mt-1 text-gray-900">{{ formatDate(dosage.timing.repeat.boundsPeriod.end) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Notes -->
      <div v-if="prescription.note && prescription.note.length > 0" class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Additional Notes
          </h3>
        </div>
        <div class="space-y-3">
          <p v-for="(note, index) in prescription.note" :key="index" class="text-gray-700">
            {{ note.text }}
          </p>
        </div>
      </div>

      <!-- Metadata -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Metadata
          </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-if="prescription.authoredOn">
            <p class="text-sm text-gray-500">Authored On</p>
            <p class="mt-1 text-gray-900">{{ formatDate(prescription.authoredOn) }}</p>
          </div>
          <div v-if="prescription.meta?.lastUpdated">
            <p class="text-sm text-gray-500">Last Updated</p>
            <p class="mt-1 text-gray-900">{{ formatDateTime(prescription.meta.lastUpdated) }}</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <button
          @click="handleDelete"
          :disabled="loading"
          class="px-6 py-3 text-sm font-medium text-white bg-danger-600 rounded-xl hover:bg-danger-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Delete Prescription
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePrescriptionStore } from '../../stores/prescription'
import { storeToRefs } from 'pinia'
import type { MedicationRequest } from '../../types/fhir'

const router = useRouter()
const route = useRoute()
const prescriptionStore = usePrescriptionStore()

const { loading, error, currentPrescription: prescription } = storeToRefs(prescriptionStore)

onMounted(async () => {
  if (route.params.id) {
    try {
      await prescriptionStore.fetchPrescriptionById(route.params.id as string)
    } catch (err) {
      console.error('Failed to load prescription:', err)
    }
  }
})

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDateTime = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDelete = async (): Promise<void> => {
  if (!route.params.id) return

  if (confirm('Are you sure you want to delete this prescription? This action cannot be undone.')) {
    try {
      await prescriptionStore.deletePrescription(route.params.id as string)
      router.push('/prescriptions')
    } catch (err) {
      console.error('Failed to delete prescription:', err)
    }
  }
}
</script>
