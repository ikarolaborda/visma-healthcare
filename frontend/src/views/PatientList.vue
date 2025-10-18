<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Patient Directory</h1>
        <p class="mt-1 text-sm text-gray-500">Manage and view all patient records</p>
      </div>
      <router-link
        to="/add"
        class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 space-x-2"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Add New Patient</span>
      </router-link>
    </div>

    <!-- Search and Filter Bar -->
    <div class="glass rounded-2xl shadow-lg p-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search patients by name, email, or phone..."
              class="block w-full pl-10 pr-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            />
          </div>
        </div>
        <button
          v-if="searchQuery"
          @click="searchQuery = ''"
          class="px-4 py-3 text-gray-600 hover:text-gray-900 transition-colors rounded-xl hover:bg-gray-100"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div
      v-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4 animate-scale-in"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <svg class="h-5 w-5 text-danger-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <p class="text-sm font-medium text-danger-700">{{ error }}</p>
        </div>
        <button
          @click="clearError"
          class="text-danger-500 hover:text-danger-700 transition-colors"
        >
          <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="glass rounded-2xl p-6 animate-pulse">
        <div class="h-12 w-12 bg-gray-200 rounded-xl mb-4"></div>
        <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div class="h-3 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!hasPatients"
      class="glass rounded-2xl shadow-lg p-12 text-center animate-scale-in"
    >
      <div class="flex flex-col items-center space-y-4">
        <div class="h-24 w-24 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
          <svg class="h-12 w-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900">No patients found</h3>
        <p class="text-gray-500 max-w-sm">Get started by adding your first patient to the system</p>
        <router-link
          to="/add"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 hover:shadow-lg transition-all duration-200 space-x-2"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Add First Patient</span>
        </router-link>
      </div>
    </div>

    <!-- Patient Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="patient in filteredPatients"
        :key="patient.id"
        class="glass rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group animate-scale-in"
      >
        <div class="p-6">
          <!-- Patient Avatar and Info -->
          <div class="flex items-start space-x-4 mb-4">
            <div class="flex-shrink-0">
              <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-md">
                <span class="text-white font-bold text-lg">
                  {{ getInitials(patient) }}
                </span>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-semibold text-gray-900 truncate">
                {{ getPatientName(patient) }}
              </h3>
              <p class="text-sm text-gray-500 capitalize">{{ patient.gender }}</p>
            </div>
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="patient.active ? 'bg-success-100 text-success-700' : 'bg-gray-100 text-gray-700'"
            >
              {{ patient.active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <!-- Patient Details -->
          <div class="space-y-3">
            <div class="flex items-center text-sm text-gray-600">
              <svg class="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{{ formatDate(patient.birthDate) }}</span>
            </div>

            <div v-if="getEmail(patient)" class="flex items-center text-sm text-gray-600 truncate">
              <svg class="h-4 w-4 mr-2 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span class="truncate">{{ getEmail(patient) }}</span>
            </div>

            <div v-if="getPhone(patient)" class="flex items-center text-sm text-gray-600">
              <svg class="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span>{{ getPhone(patient) }}</span>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-6 flex gap-2">
            <router-link
              :to="`/patient/${patient.id}`"
              class="flex-1 inline-flex items-center justify-center px-4 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 space-x-2"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>View</span>
            </router-link>

            <router-link
              :to="`/patient/${patient.id}/edit`"
              class="inline-flex items-center justify-center px-4 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors duration-200"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </router-link>

            <button
              @click="handleDelete(patient.id, getPatientName(patient))"
              class="inline-flex items-center justify-center px-4 py-2.5 bg-danger-50 text-danger-600 text-sm font-medium rounded-lg hover:bg-danger-100 transition-colors duration-200"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Count -->
    <div v-if="!loading && hasPatients" class="text-center text-sm text-gray-500">
      Showing {{ filteredPatients.length }} of {{ patients.length }} patients
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePatientStore } from '../stores/patient'
import { storeToRefs } from 'pinia'

const patientStore = usePatientStore()
const { patients, loading, error } = storeToRefs(patientStore)
const searchQuery = ref('')

onMounted(async () => {
  await patientStore.fetchPatients()
})

const sortedPatients = computed(() => {
  return [...patients.value].sort((a, b) => {
    const nameA = getPatientName(a).toLowerCase()
    const nameB = getPatientName(b).toLowerCase()
    return nameA.localeCompare(nameB)
  })
})

const filteredPatients = computed(() => {
  if (!searchQuery.value) return sortedPatients.value

  const query = searchQuery.value.toLowerCase()
  return sortedPatients.value.filter(patient => {
    const name = getPatientName(patient).toLowerCase()
    const email = getEmail(patient).toLowerCase()
    const phone = getPhone(patient).toLowerCase()
    return name.includes(query) || email.includes(query) || phone.includes(query)
  })
})

const hasPatients = computed(() => patients.value.length > 0)

const getPatientName = (patient) => {
  const name = patient.name?.[0]
  if (!name) return 'Unknown Patient'
  const given = name.given?.join(' ') || ''
  return `${given} ${name.family || ''}`.trim() || 'Unknown Patient'
}

const getInitials = (patient) => {
  const name = patient.name?.[0]
  if (!name) return 'UP'
  const firstInitial = name.given?.[0]?.[0] || ''
  const lastInitial = name.family?.[0] || ''
  return (firstInitial + lastInitial).toUpperCase() || 'UP'
}

const getEmail = (patient) => {
  return patient.telecom?.find(t => t.system === 'email')?.value || 'N/A'
}

const getPhone = (patient) => {
  return patient.telecom?.find(t => t.system === 'phone')?.value || 'N/A'
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleDelete = async (id, patientName) => {
  if (confirm(`Are you sure you want to delete ${patientName}? This action cannot be undone.`)) {
    try {
      await patientStore.deletePatient(id)
    } catch (err) {
      console.error('Delete error:', err)
    }
  }
}

const clearError = () => {
  patientStore.clearError()
}
</script>
