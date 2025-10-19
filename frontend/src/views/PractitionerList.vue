<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">{{ $t('practitioner.practitionerDirectory') }}</h1>
        <p class="mt-1 text-sm text-gray-500">{{ $t('practitioner.noPractitionersDesc') }}</p>
      </div>
      <router-link
        to="/practitioners/add"
        class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 space-x-2"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>{{ $t('practitioner.addPractitioner') }}</span>
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
      v-else-if="!hasPractitioners"
      class="glass rounded-2xl shadow-lg p-12 text-center animate-scale-in"
    >
      <div class="flex flex-col items-center space-y-4">
        <div class="h-24 w-24 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
          <svg class="h-12 w-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900">{{ $t('practitioner.noPractitioners') }}</h3>
        <p class="text-gray-500 max-w-sm">{{ $t('practitioner.noPractitionersDesc') }}</p>
        <router-link
          to="/practitioners/add"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 hover:shadow-lg transition-all duration-200 space-x-2"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>{{ $t('practitioner.addFirstPractitioner') }}</span>
        </router-link>
      </div>
    </div>

    <!-- Practitioner Data Table -->
    <DataTable
      v-else
      :data="sortedPractitioners"
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
            <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center shadow-sm">
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

      <!-- Specialization Column -->
      <template #cell-specialization="{ row }">
        <span class="text-sm text-gray-900">{{ row.specialization }}</span>
      </template>

      <!-- Email Column -->
      <template #cell-email="{ row }">
        <span class="text-sm text-gray-600">{{ row.email }}</span>
      </template>

      <!-- Phone Column -->
      <template #cell-phone="{ row }">
        <span class="text-sm text-gray-600">{{ row.phone }}</span>
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
            :to="`/practitioners/${row.id}`"
            class="inline-flex items-center px-3 py-1.5 bg-primary-600 text-white text-xs font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
            :title="$t('common.view')"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </router-link>

          <router-link
            :to="`/practitioners/${row.id}/edit`"
            class="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-lg hover:bg-gray-200 transition-colors duration-200"
            :title="$t('common.edit')"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </router-link>

          <button
            @click="handleDelete(row.id, getPractitionerName(row))"
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
import { useI18n } from 'vue-i18n'
import { useToast } from 'vue-toastification'
import { usePractitionerStore } from '../stores/practitioner'
import { storeToRefs } from 'pinia'
import DataTable from '../components/DataTable.vue'
import type { Practitioner } from '../types/fhir'

const { t } = useI18n()
const toast = useToast()
const practitionerStore = usePractitionerStore()
const { practitioners, loading, error } = storeToRefs(practitionerStore)

onMounted(async () => {
  console.log('[PractitionerList] Component mounted, calling fetchPractitioners')
  try {
    await practitionerStore.fetchPractitioners()
    console.log('[PractitionerList] Fetch complete, practitioners.value.length:', practitioners.value.length)
  } catch (error) {
    console.error('[PractitionerList] Error during fetch:', error)
  }
})

const columns = computed(() => [
  { key: '_displayName', label: t('practitioner.fullName') },
  { key: 'specialization', label: t('practitioner.specialization') },
  { key: 'email', label: t('practitioner.email') },
  { key: 'phone', label: t('practitioner.phone') },
  { key: '_displayStatus', label: t('common.status') }
])

const sortedPractitioners = computed(() => {
  return [...practitioners.value]
    .map(practitioner => {
      // Create extended practitioner object with computed display fields
      const extended: any = { ...practitioner }
      extended._displayName = getPractitionerName(practitioner)
      extended._displayStatus = practitioner.active ? t('common.active') : t('common.inactive')
      return extended
    })
    .sort((a, b) => {
      const nameA = a._displayName.toLowerCase()
      const nameB = b._displayName.toLowerCase()
      return nameA.localeCompare(nameB)
    })
})

const hasPractitioners = computed(() => practitioners.value.length > 0)

const getPractitionerName = (practitioner: Practitioner): string => {
  // Handle FHIR format (name[0].given, name[0].family)
  if (practitioner.name && practitioner.name.length > 0) {
    const nameObj = practitioner.name[0]
    if (nameObj) {
      const prefix = nameObj.prefix?.join(' ') || ''
      const given = nameObj.given?.join(' ') || ''
      const family = nameObj.family || ''
      return `${prefix} ${given} ${family}`.trim() || 'Unknown Practitioner'
    }
  }
  // Fallback to legacy format
  const prefix = practitioner.prefix ? `${practitioner.prefix} ` : ''
  const given = practitioner.given_name || ''
  const family = practitioner.family_name || ''
  return `${prefix}${given} ${family}`.trim() || 'Unknown Practitioner'
}

const getInitials = (practitioner: Practitioner): string => {
  // Handle FHIR format
  if (practitioner.name && practitioner.name.length > 0) {
    const nameObj = practitioner.name[0]
    if (nameObj) {
      const firstInitial = nameObj.given?.[0]?.[0] || ''
      const lastInitial = nameObj.family?.[0] || ''
      return (firstInitial + lastInitial).toUpperCase() || 'UP'
    }
  }
  // Fallback to legacy format
  const firstInitial = practitioner.given_name?.[0] || ''
  const lastInitial = practitioner.family_name?.[0] || ''
  return (firstInitial + lastInitial).toUpperCase() || 'UP'
}

const handleDelete = async (id: string, practitionerName: string): Promise<void> => {
  if (confirm(t('practitioner.confirmDelete', { name: practitionerName }))) {
    try {
      await practitionerStore.deletePractitioner(id)
      toast.success(t('practitioner.deleteSuccess'))
    } catch (err) {
      console.error('Delete error:', err)
      toast.error(t('practitioner.deleteError'))
    }
  }
}

const clearError = (): void => {
  practitionerStore.clearError()
}
</script>
