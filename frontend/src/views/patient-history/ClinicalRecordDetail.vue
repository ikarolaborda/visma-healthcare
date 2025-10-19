<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Clinical Record Details</h1>
        <p class="mt-1 text-sm text-gray-500">View detailed clinical record information</p>
      </div>
      <div class="flex items-center space-x-3">
        <router-link
          :to="`/patient-history/edit/${$route.params.id}`"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit
        </router-link>
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
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading clinical record...</p>
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

    <!-- Record Details -->
    <div v-else-if="record" class="space-y-6">
      <!-- Record Header -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Record Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="md:col-span-2">
            <p class="text-sm text-gray-500">Title/Description</p>
            <p class="mt-1 text-xl font-semibold text-gray-900">{{ record.code?.text || 'N/A' }}</p>
          </div>

          <div>
            <p class="text-sm text-gray-500">Status</p>
            <span
              class="inline-flex mt-1 px-3 py-1 text-sm font-semibold rounded-full"
              :class="{
                'bg-blue-100 text-blue-700': record.status === 'registered',
                'bg-yellow-100 text-yellow-700': record.status === 'preliminary',
                'bg-success-100 text-success-700': record.status === 'final',
                'bg-gray-100 text-gray-700': record.status === 'amended'
              }"
            >
              {{ record.status }}
            </span>
          </div>

          <div>
            <p class="text-sm text-gray-500">FHIR Resource ID</p>
            <p class="mt-1 text-sm font-mono text-gray-900">{{ record.id || 'N/A' }}</p>
          </div>

          <div>
            <p class="text-sm text-gray-500">Recorded Date/Time</p>
            <p class="mt-1 text-gray-900">{{ formatDateTime(record.effectiveDateTime) }}</p>
          </div>

          <div v-if="record.meta?.lastUpdated">
            <p class="text-sm text-gray-500">Last Updated</p>
            <p class="mt-1 text-gray-900">{{ formatDateTime(record.meta.lastUpdated) }}</p>
          </div>
        </div>
      </div>

      <!-- Patient & Performer Information -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Patient & Recorded By
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p class="text-sm text-gray-500">Patient</p>
            <p class="mt-1 text-lg font-medium text-gray-900">
              {{ record.subject?.display || record.subject?.reference || 'N/A' }}
            </p>
          </div>

          <div v-if="record.performer && record.performer.length > 0">
            <p class="text-sm text-gray-500">Recorded By</p>
            <p class="mt-1 text-lg font-medium text-gray-900">
              {{ record.performer[0]?.display || record.performer[0]?.reference || 'N/A' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Observation Value -->
      <div v-if="record.valueQuantity || record.valueString" class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Observation Value
          </h3>
        </div>

        <div class="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6">
          <div v-if="record.valueQuantity">
            <p class="text-sm text-primary-700 mb-2">Quantity Measurement</p>
            <p class="text-4xl font-bold text-primary-900">
              {{ record.valueQuantity.value }}
              <span v-if="record.valueQuantity.unit" class="text-2xl font-medium ml-2">
                {{ record.valueQuantity.unit }}
              </span>
            </p>
          </div>

          <div v-else-if="record.valueString">
            <p class="text-sm text-primary-700 mb-2">Text Value</p>
            <p class="text-lg font-medium text-primary-900">{{ record.valueString }}</p>
          </div>
        </div>
      </div>

      <!-- Additional Information -->
      <div v-if="record.interpretation || record.bodySite || record.method" class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Additional Information
          </h3>
        </div>

        <div class="space-y-4">
          <div v-if="record.interpretation && record.interpretation.length > 0">
            <p class="text-sm text-gray-500">Interpretation</p>
            <p class="mt-1 text-gray-900">{{ record.interpretation[0]?.text }}</p>
          </div>

          <div v-if="record.bodySite">
            <p class="text-sm text-gray-500">Body Site</p>
            <p class="mt-1 text-gray-900">{{ record.bodySite.text }}</p>
          </div>

          <div v-if="record.method">
            <p class="text-sm text-gray-500">Method</p>
            <p class="mt-1 text-gray-900">{{ record.method.text }}</p>
          </div>
        </div>
      </div>

      <!-- Clinical Notes -->
      <div v-if="record.note && record.note.length > 0" class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Clinical Notes
          </h3>
        </div>

        <div class="space-y-3">
          <div v-for="(note, index) in record.note" :key="index" class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-700">{{ note.text }}</p>
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
          Delete Record
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useClinicalRecordStore } from '../../stores/clinicalRecord'
import { storeToRefs } from 'pinia'
import type { Observation } from '../../types/fhir'

const router = useRouter()
const route = useRoute()
const recordStore = useClinicalRecordStore()

const { loading, error, currentRecord: record } = storeToRefs(recordStore)

onMounted(async () => {
  if (route.params.id) {
    try {
      await recordStore.fetchRecordById(route.params.id as string)
    } catch (err) {
      console.error('Failed to load clinical record:', err)
    }
  }
})

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

  if (confirm('Are you sure you want to delete this clinical record? This action cannot be undone.')) {
    try {
      await recordStore.deleteRecord(route.params.id as string)
      router.push('/patient-history')
    } catch (err) {
      console.error('Failed to delete clinical record:', err)
    }
  }
}
</script>
