<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          Patient History
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          Clinical records, conditions, and observations
        </p>
      </div>
      <router-link
        to="/patient-history/add"
        class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 space-x-2"
      >
        <svg
          class="h-5 w-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          />
        </svg>
        <span>Add Clinical Record</span>
      </router-link>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="glass rounded-2xl shadow-lg p-12 text-center"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto" />
      <p class="text-gray-500 mt-4">
        Loading clinical records...
      </p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="records.length === 0"
      class="glass rounded-2xl shadow-lg p-12 text-center"
    >
      <div class="flex flex-col items-center space-y-4">
        <div class="h-24 w-24 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
          <svg
            class="h-12 w-12 text-primary-600"
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
        </div>
        <h3 class="text-xl font-semibold text-gray-900">
          No Clinical Records Found
        </h3>
        <p class="text-gray-500 max-w-sm">
          Start documenting patient medical history
        </p>
        <router-link
          to="/patient-history/add"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 transition-all"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add First Record
        </router-link>
      </div>
    </div>

    <!-- Records Grid -->
    <div
      v-else
      class="grid grid-cols-1 gap-6"
    >
      <div
        v-for="record in records"
        :key="record.id"
        class="glass rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-3">
              <span
                v-if="record.category && record.category.length > 0"
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                :class="getTypeClass(record.category[0]?.coding?.[0]?.display || '')"
              >
                {{ formatType(record.category[0]?.coding?.[0]?.display || '') }}
              </span>
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                :class="getStatusClass(record.status)"
              >
                {{ record.status }}
              </span>
              <span
                v-if="record.interpretation && record.interpretation.length > 0"
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                :class="getSeverityClass(record.interpretation[0]?.coding?.[0]?.display || '')"
              >
                {{ record.interpretation[0]?.coding?.[0]?.display }}
              </span>
            </div>

            <h3 class="text-lg font-semibold text-gray-900 mb-2">
              {{ record.code?.text || '' }}
            </h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
              <div>
                <span class="font-medium">Patient:</span> {{ record.subject?.display || 'N/A' }}
              </div>
              <div>
                <span class="font-medium">Recorded by:</span> {{ record.performer?.[0]?.display || 'N/A' }}
              </div>
              <div>
                <span class="font-medium">Date:</span> {{ formatDate(record.effectiveDateTime) }}
              </div>
              <div v-if="record.valueQuantity">
                <span class="font-medium">Value:</span> {{ record.valueQuantity.value }} {{ record.valueQuantity.unit }}
              </div>
            </div>

            <p
              v-if="record.note && record.note.length > 0"
              class="text-sm text-gray-700 bg-gray-50 rounded-lg p-3"
            >
              {{ record.note.map(n => n.text).join('; ') }}
            </p>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <router-link
              :to="`/patient-history/${record.id}`"
              class="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              title="View Details"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
            </router-link>
            <button
              class="p-2 text-danger-600 hover:bg-danger-50 rounded-lg transition-colors"
              title="Delete"
              @click="handleDelete(record.id, record.code?.text)"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useClinicalRecordStore } from '../stores/clinicalRecord'
import { storeToRefs } from 'pinia'

const toast = useToast()
const recordStore = useClinicalRecordStore()
const { records, loading } = storeToRefs(recordStore)

onMounted(() => {
  recordStore.fetchRecords()
})

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'condition': 'Condition/Diagnosis',
    'observation': 'Observation',
    'allergy': 'Allergy',
    'procedure': 'Procedure',
    'family-history': 'Family History'
  }
  return typeMap[type] || type
}

const getTypeClass = (type: string): string => {
  const typeClasses: Record<string, string> = {
    'condition': 'bg-red-100 text-red-700',
    'observation': 'bg-blue-100 text-blue-700',
    'allergy': 'bg-orange-100 text-orange-700',
    'procedure': 'bg-purple-100 text-purple-700',
    'family-history': 'bg-indigo-100 text-indigo-700'
  }
  return typeClasses[type] || 'bg-gray-100 text-gray-700'
}

const getStatusClass = (status: string): string => {
  const statusClasses: Record<string, string> = {
    active: 'bg-success-100 text-success-700',
    resolved: 'bg-gray-100 text-gray-700',
    inactive: 'bg-gray-100 text-gray-500'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-700'
}

const getSeverityClass = (severity: string): string => {
  const severityClasses: Record<string, string> = {
    mild: 'bg-yellow-100 text-yellow-700',
    moderate: 'bg-orange-100 text-orange-700',
    severe: 'bg-red-100 text-red-700'
  }
  return severityClasses[severity] || 'bg-gray-100 text-gray-700'
}

const handleDelete = async (id: string | undefined, title: string | undefined): Promise<void> => {
  if (!id) return
  if (confirm(`Are you sure you want to delete the record "${title || 'this record'}"?`)) {
    try {
      await recordStore.deleteRecord(id)
      toast.success('Clinical record deleted successfully')
    } catch (err) {
      console.error('Delete error:', err)
      toast.error('Failed to delete clinical record')
    }
  }
}
</script>
