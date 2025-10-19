<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">{{ $t('patient.patientDirectory') }}</h1>
        <p class="mt-1 text-sm text-gray-500">{{ $t('patient.noPatientsDesc') }}</p>
      </div>
      <router-link
        to="/add"
        class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 space-x-2"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>{{ $t('patient.addPatient') }}</span>
      </router-link>
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
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 animate-pulse">
      <div class="space-y-4">
        <div class="h-8 bg-gray-200 rounded w-1/3"></div>
        <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        <div class="h-4 bg-gray-200 rounded w-2/3"></div>
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
        <h3 class="text-xl font-semibold text-gray-900">{{ $t('patient.noPatients') }}</h3>
        <p class="text-gray-500 max-w-sm">{{ $t('patient.noPatientsDesc') }}</p>
        <router-link
          to="/add"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 hover:shadow-lg transition-all duration-200 space-x-2"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>{{ $t('patient.addFirstPatient') }}</span>
        </router-link>
      </div>
    </div>

    <!-- Patient Data Table -->
    <DataTable
      v-else
      :data="sortedPatients"
      :columns="columns"
      :searchable="true"
      :paginate="true"
      :per-page="10"
      row-key="id"
    >
      <!-- Name Column with Avatar -->
      <template #cell-name="{ row }">
        <div class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-sm">
              <span class="text-white font-semibold text-sm">
                {{ getInitials(row) }}
              </span>
            </div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-900">
              {{ row._displayName }}
            </div>
          </div>
        </div>
      </template>

      <!-- Gender Column -->
      <template #cell-gender="{ row }">
        <span class="text-sm text-gray-900 capitalize">{{ row.gender }}</span>
      </template>

      <!-- Birth Date Column -->
      <template #cell-birthDate="{ row }">
        <span class="text-sm text-gray-900">{{ formatDate(row.birthDate) }}</span>
      </template>

      <!-- Email Column -->
      <template #cell-email="{ row }">
        <span class="text-sm text-gray-600">{{ getEmail(row) }}</span>
      </template>

      <!-- Phone Column -->
      <template #cell-phone="{ row }">
        <span class="text-sm text-gray-600">{{ getPhone(row) }}</span>
      </template>

      <!-- Status Column -->
      <template #cell-status="{ row }">
        <span
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          :class="row.active ? 'bg-success-100 text-success-700' : 'bg-gray-100 text-gray-700'"
        >
          {{ row.active ? $t('common.active') : $t('common.inactive') }}
        </span>
      </template>

      <!-- Actions Column -->
      <template #actions="{ row }">
        <div v-if="row" class="flex items-center justify-end gap-2">
          <router-link
            :to="`/patient/${row.id}`"
            class="inline-flex items-center px-3 py-1.5 bg-primary-600 text-white text-xs font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
            :title="$t('common.view')"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </router-link>

          <router-link
            :to="`/patient/${row.id}/edit`"
            class="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-lg hover:bg-gray-200 transition-colors duration-200"
            :title="$t('common.edit')"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </router-link>

          <button
            @click="handleDelete(row.id, getPatientName(row))"
            class="inline-flex items-center px-3 py-1.5 bg-danger-50 text-danger-600 text-xs font-medium rounded-lg hover:bg-danger-100 transition-colors duration-200"
            :title="$t('common.delete')"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { usePatientStore } from '../stores/patient'
import { useI18n } from 'vue-i18n'
import { useToast } from 'vue-toastification'
import { storeToRefs } from 'pinia'
import DataTable from '../components/DataTable.vue'
import type { Patient } from '../types/fhir'

const { t } = useI18n()
const toast = useToast()
const patientStore = usePatientStore()
const { patients, loading, error } = storeToRefs(patientStore)

onMounted(async () => {
  await patientStore.fetchPatients()
})

const columns = computed(() => [
  { key: '_displayName', label: t('patient.fullName') },
  { key: 'gender', label: t('patient.gender') },
  { key: 'birthDate', label: t('patient.birthDate') },
  { key: '_displayEmail', label: t('patient.email') },
  { key: '_displayPhone', label: t('patient.phone') },
  { key: '_displayStatus', label: t('common.status') }
])

const sortedPatients = computed(() => {
  return [...patients.value]
    .map(patient => {
      // Create extended patient object with computed display fields
      const extended: any = { ...patient }
      extended._displayName = getPatientName(patient)
      extended._displayEmail = getEmail(patient)
      extended._displayPhone = getPhone(patient)
      extended._displayStatus = patient.active ? t('common.active') : t('common.inactive')
      return extended
    })
    .sort((a, b) => {
      const nameA = a._displayName.toLowerCase()
      const nameB = b._displayName.toLowerCase()
      return nameA.localeCompare(nameB)
    })
})

const hasPatients = computed(() => patients.value.length > 0)

const getPatientName = (patient: Patient): string => {
  const name = patient.name?.[0]
  if (!name) return 'Unknown Patient'
  const given = name.given?.join(' ') || ''
  return `${given} ${name.family || ''}`.trim() || 'Unknown Patient'
}

const getInitials = (patient: Patient): string => {
  const name = patient.name?.[0]
  if (!name) return 'UP'
  const firstInitial = name.given?.[0]?.[0] || ''
  const lastInitial = name.family?.[0] || ''
  return (firstInitial + lastInitial).toUpperCase() || 'UP'
}

const getEmail = (patient: Patient): string => {
  return patient.telecom?.find(t => t.system === 'email')?.value || 'N/A'
}

const getPhone = (patient: Patient): string => {
  return patient.telecom?.find(t => t.system === 'phone')?.value || 'N/A'
}

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleDelete = async (id: string, patientName: string): Promise<void> => {
  if (confirm(t('patient.confirmDelete', { name: patientName }))) {
    try {
      await patientStore.deletePatient(id)
      toast.success(t('patient.deleteSuccess'))
    } catch (err) {
      console.error('Delete error:', err)
      toast.error(t('patient.deleteError'))
    }
  }
}

const clearError = (): void => {
  patientStore.clearError()
}
</script>
