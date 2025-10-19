<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ $t('appointment.appointmentSchedule') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ $t('appointment.noAppointmentsDesc') }}
        </p>
      </div>
      <router-link
        to="/appointments/add"
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
        <span>{{ $t('appointment.addAppointment') }}</span>
      </router-link>
    </div>

    <!-- Filter Tabs -->
    <div class="glass rounded-2xl shadow-lg overflow-hidden">
      <div class="flex border-b border-gray-200">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="flex-1 px-6 py-4 text-sm font-medium transition-colors"
          :class="activeTab === tab.value
            ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50/50'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
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
          <svg
            class="h-5 w-5 text-danger-500"
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
        <button
          class="text-danger-500 hover:text-danger-700 transition-colors"
          @click="clearError"
        >
          <svg
            class="h-5 w-5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="glass rounded-2xl shadow-lg p-12 animate-pulse"
    >
      <div class="space-y-4">
        <div class="h-8 bg-gray-200 rounded w-1/3" />
        <div class="h-4 bg-gray-200 rounded w-1/2" />
        <div class="h-4 bg-gray-200 rounded w-2/3" />
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!hasAppointments"
      class="glass rounded-2xl shadow-lg p-12 text-center animate-scale-in"
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
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900">
          {{ $t('appointment.noAppointments') }}
        </h3>
        <p class="text-gray-500 max-w-sm">
          {{ $t('appointment.noAppointmentsDesc') }}
        </p>
        <router-link
          to="/appointments/add"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 hover:shadow-lg transition-all duration-200 space-x-2"
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
          <span>{{ $t('appointment.scheduleFirst') }}</span>
        </router-link>
      </div>
    </div>

    <!-- Appointment Data Table -->
    <DataTable
      v-else
      :data="filteredAppointments"
      :columns="columns"
      :searchable="true"
      :paginate="true"
      :per-page="10"
      row-key="id"
    >
      <!-- Patient Column -->
      <template #cell-patient="{ row }">
        <div class="text-sm font-medium text-gray-900">
          {{ row._displayPatient }}
        </div>
      </template>

      <!-- Date Column -->
      <template #cell-date="{ row }">
        <span class="text-sm text-gray-900">{{ formatDate(row.start) }}</span>
      </template>

      <!-- Time Column -->
      <template #cell-time="{ row }">
        <span class="text-sm text-gray-900">{{ formatTime(row.start) }}</span>
      </template>

      <!-- Duration Column -->
      <template #cell-duration="{ row }">
        <span class="text-sm text-gray-600">
          {{ row.minutesDuration || calculateDuration(row.start, row.end) }} {{ $t('appointment.minutes') }}
        </span>
      </template>

      <!-- Reason Column -->
      <template #cell-reason="{ row }">
        <span class="text-sm text-gray-600">{{ getReason(row) }}</span>
      </template>

      <!-- Status Column -->
      <template #cell-status="{ row }">
        <span
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          :class="getStatusClass(row.status)"
        >
          {{ $t(`appointment.status.${row.status}`) }}
        </span>
      </template>

      <!-- Actions Column -->
      <template #actions="{ row }">
        <div
          v-if="row"
          class="flex items-center justify-end gap-2"
        >
          <router-link
            :to="`/appointments/${row.id}`"
            class="inline-flex items-center px-3 py-1.5 bg-primary-600 text-white text-xs font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200"
            :title="$t('common.view')"
          >
            <svg
              class="h-4 w-4"
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

          <router-link
            v-if="row.status !== 'cancelled' && row.status !== 'fulfilled'"
            :to="`/appointments/${row.id}/edit`"
            class="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-lg hover:bg-gray-200 transition-colors duration-200"
            :title="$t('common.edit')"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </router-link>

          <button
            v-if="row.status !== 'cancelled' && row.status !== 'fulfilled'"
            class="inline-flex items-center px-3 py-1.5 bg-danger-50 text-danger-600 text-xs font-medium rounded-lg hover:bg-danger-100 transition-colors duration-200"
            :title="$t('appointment.cancelAppointment')"
            @click="handleCancel(row.id, getPatientName(row))"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppointmentStore } from '../stores/appointment'
import { useI18n } from 'vue-i18n'
import { useToast } from 'vue-toastification'
import { storeToRefs } from 'pinia'
import DataTable from '../components/DataTable.vue'
import type { Appointment } from '../types/fhir'

const { t } = useI18n()
const toast = useToast()
const appointmentStore = useAppointmentStore()
const { appointments, loading, error } = storeToRefs(appointmentStore)

const activeTab = ref<string>('all')

const tabs = computed(() => [
  { value: 'all', label: t('appointment.appointments') },
  { value: 'today', label: t('appointment.today') },
  { value: 'upcoming', label: t('appointment.upcoming') },
  { value: 'past', label: t('appointment.past') }
])

onMounted(async () => {
  await appointmentStore.fetchAppointments()
})

const columns = computed(() => [
  { key: 'patient', label: t('appointment.patient') },
  { key: 'date', label: t('common.date') },
  { key: 'time', label: t('common.time') },
  { key: 'duration', label: t('appointment.duration') },
  { key: 'reason', label: t('appointment.reason') },
  { key: 'status', label: t('common.status') }
])

const filteredAppointments = computed(() => {
  let appointments: Appointment[] = []
  switch (activeTab.value) {
    case 'today':
      appointments = appointmentStore.todayAppointments
      break
    case 'upcoming':
      appointments = appointmentStore.upcomingAppointments
      break
    case 'past':
      appointments = appointmentStore.pastAppointments
      break
    default:
      appointments = appointmentStore.sortedAppointments
  }

  // Add flattened fields for filtering and display
  return appointments.map(appointment => {
    const extended: any = { ...appointment }
    extended._displayPatient = getPatientName(appointment)
    extended._displayDate = formatDate(appointment.start)
    extended._displayTime = formatTime(appointment.start)
    extended._displayDuration = `${appointment.minutesDuration || calculateDuration(appointment.start, appointment.end)} ${t('appointment.minutes')}`
    extended._displayReason = getReason(appointment)
    extended._displayStatus = t(`appointment.status.${appointment.status}`)
    return extended
  })
})

const hasAppointments = computed(() => appointments.value.length > 0)

const getPatientName = (appointment: Appointment): string => {
  const patientParticipant = appointment.participant?.find(
    p => p.actor?.reference?.startsWith('Patient/')
  )
  return patientParticipant?.actor?.display || 'Unknown Patient'
}

const getReason = (appointment: Appointment): string => {
  return appointment.reasonCode?.[0]?.text || appointment.description || 'N/A'
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

const formatTime = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateDuration = (start: string | undefined, end: string | undefined): number | string => {
  if (!start || !end) return 'N/A'
  const startDate = new Date(start)
  const endDate = new Date(end)
  const diffMs = endDate.getTime() - startDate.getTime()
  return Math.round(diffMs / 1000 / 60)
}

const getStatusClass = (status: string): string => {
  const statusClasses: Record<string, string> = {
    proposed: 'bg-gray-100 text-gray-700',
    pending: 'bg-yellow-100 text-yellow-700',
    booked: 'bg-blue-100 text-blue-700',
    arrived: 'bg-purple-100 text-purple-700',
    fulfilled: 'bg-success-100 text-success-700',
    cancelled: 'bg-danger-100 text-danger-700',
    noshow: 'bg-orange-100 text-orange-700',
    'checked-in': 'bg-teal-100 text-teal-700',
    waitlist: 'bg-indigo-100 text-indigo-700'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-700'
}

const handleCancel = async (id: string, _patientName: string): Promise<void> => {
  if (confirm(t('appointment.confirmCancel'))) {
    try {
      await appointmentStore.cancelAppointment(id)
      toast.success(t('appointment.cancelSuccess'))
    } catch (err) {
      console.error('Cancel error:', err)
      toast.error(t('appointment.cancelError'))
    }
  }
}

const clearError = (): void => {
  appointmentStore.clearError()
}
</script>
