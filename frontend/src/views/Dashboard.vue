<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900">
        {{ $t('dashboard.dashboard') }}
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        {{ $t('dashboard.overview') }}
      </p>
    </div>

    <!-- Error Alert -->
    <div
      v-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4"
    >
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
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="glass rounded-2xl shadow-lg p-12"
    >
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
      <p class="text-center text-gray-500 mt-4">
        {{ $t('dashboard.loading') }}
      </p>
    </div>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- Statistics Cards -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Total Patients Card -->
        <router-link
          to="/patients"
          class="glass rounded-2xl shadow-lg p-6 hover:shadow-xl hover:scale-105 transition-all duration-200 cursor-pointer"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl">
              <svg
                class="h-8 w-8 text-white"
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
            </div>
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-500">
                {{ $t('dashboard.totalPatients') }}
              </p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.totalPatients }}
              </p>
            </div>
          </div>
        </router-link>

        <!-- Total Practitioners Card -->
        <router-link
          to="/practitioners"
          class="glass rounded-2xl shadow-lg p-6 hover:shadow-xl hover:scale-105 transition-all duration-200 cursor-pointer"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl">
              <svg
                class="h-8 w-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-500">
                {{ $t('dashboard.totalPractitioners') }}
              </p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.totalPractitioners }}
              </p>
            </div>
          </div>
        </router-link>

        <!-- Total Appointments Card -->
        <router-link
          to="/appointments"
          class="glass rounded-2xl shadow-lg p-6 hover:shadow-xl hover:scale-105 transition-all duration-200 cursor-pointer"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl">
              <svg
                class="h-8 w-8 text-white"
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
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-500">
                {{ $t('dashboard.totalAppointments') }}
              </p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.totalAppointments }}
              </p>
            </div>
          </div>
        </router-link>

        <!-- Today's Appointments Card -->
        <router-link
          to="/appointments"
          class="glass rounded-2xl shadow-lg p-6 hover:shadow-xl hover:scale-105 transition-all duration-200 cursor-pointer"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0 p-3 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl">
              <svg
                class="h-8 w-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-500">
                {{ $t('dashboard.todayAppointments') }}
              </p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.todayAppointments }}
              </p>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Appointments by Status Pie Chart -->
        <div class="glass rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            {{ $t('dashboard.appointmentsByStatus') }}
          </h3>
          <div class="h-64">
            <Doughnut
              v-if="appointmentsByStatusData"
              :data="appointmentsByStatusData"
              :options="chartOptions"
            />
            <div
              v-else
              class="flex items-center justify-center h-full text-gray-500"
            >
              {{ $t('dashboard.noData') }}
            </div>
          </div>
        </div>

        <!-- Gender Distribution Pie Chart -->
        <div class="glass rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            {{ $t('dashboard.genderDistribution') }}
          </h3>
          <div class="h-64">
            <Pie
              v-if="genderDistributionData"
              :data="genderDistributionData"
              :options="chartOptions"
            />
            <div
              v-else
              class="flex items-center justify-center h-full text-gray-500"
            >
              {{ $t('dashboard.noData') }}
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments Timeline -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          {{ $t('dashboard.appointmentsTimeline') }} - {{ $t('dashboard.last7Days') }}
        </h3>
        <div class="h-80">
          <Line
            v-if="appointmentsTimelineData"
            :data="appointmentsTimelineData"
            :options="lineChartOptions"
          />
          <div
            v-else
            class="flex items-center justify-center h-full text-gray-500"
          >
            {{ $t('dashboard.noData') }}
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent Patients -->
        <div class="glass rounded-2xl shadow-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ $t('dashboard.recentPatients') }}
            </h3>
            <router-link
              to="/"
              class="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              {{ $t('dashboard.viewAll') }} →
            </router-link>
          </div>
          <div
            v-if="recentPatients.length > 0"
            class="space-y-3"
          >
            <div
              v-for="patient in recentPatients"
              :key="patient.id"
              class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50/50 transition-colors"
            >
              <div class="flex-shrink-0 h-10 w-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                <span class="text-white font-semibold text-sm">{{ getInitials(patient.name?.[0]) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ getPatientName(patient) }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ patient.gender }}
                </p>
              </div>
            </div>
          </div>
          <div
            v-else
            class="text-center py-8 text-gray-500"
          >
            {{ $t('dashboard.noData') }}
          </div>
        </div>

        <!-- Recent Appointments -->
        <div class="glass rounded-2xl shadow-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ $t('dashboard.recentAppointments') }}
            </h3>
            <router-link
              to="/appointments"
              class="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              {{ $t('dashboard.viewAll') }} →
            </router-link>
          </div>
          <div
            v-if="recentAppointments.length > 0"
            class="space-y-3"
          >
            <div
              v-for="apt in recentAppointments"
              :key="apt.id"
              class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50/50 transition-colors"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ getAppointmentPatientName(apt) }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ formatDateTime(apt.start) }}
                </p>
              </div>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusClass(apt.status)"
              >
                {{ $t(`appointment.status.${apt.status}`) }}
              </span>
            </div>
          </div>
          <div
            v-else
            class="text-center py-8 text-gray-500"
          >
            {{ $t('dashboard.noData') }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePatientStore } from '../stores/patient'
import { useAppointmentStore } from '../stores/appointment'
import { usePractitionerStore } from '../stores/practitioner'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, Filler } from 'chart.js'
import { Doughnut, Pie, Line } from 'vue-chartjs'
import type { Patient, Appointment, HumanName } from '../types/fhir'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, Filler)

const { t } = useI18n()
const patientStore = usePatientStore()
const appointmentStore = useAppointmentStore()
const practitionerStore = usePractitionerStore()

const loading = ref<boolean>(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    await Promise.all([
      patientStore.fetchPatients(),
      appointmentStore.fetchAppointments(),
      practitionerStore.fetchPractitioners()
    ])
  } catch (err) {
    error.value = 'Failed to load dashboard data'
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
})

const stats = computed(() => ({
  totalPatients: Array.isArray(patientStore.patients) ? patientStore.patients.length : 0,
  totalPractitioners: Array.isArray(practitionerStore.practitioners) ? practitionerStore.practitioners.length : 0,
  totalAppointments: Array.isArray(appointmentStore.appointments) ? appointmentStore.appointments.length : 0,
  todayAppointments: appointmentStore.todayAppointments.length
}))

const appointmentsByStatusData = computed(() => {
  const statusCounts: Record<string, number> = {}
  const appointments = Array.isArray(appointmentStore.appointments) ? appointmentStore.appointments : []

  appointments.forEach(apt => {
    const status = apt.status || 'unknown'
    statusCounts[status] = (statusCounts[status] || 0) + 1
  })

  const labels = Object.keys(statusCounts).map(status => t(`appointment.status.${status}`))
  const data = Object.values(statusCounts) as number[]

  return {
    labels,
    datasets: [{
      data,
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(251, 146, 60, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)'
      ],
      borderWidth: 0
    }]
  }
})

const genderDistributionData = computed(() => {
  const genderCounts: Record<string, number> = {}
  const patients = Array.isArray(patientStore.patients) ? patientStore.patients : []

  patients.forEach(patient => {
    const gender = patient.gender || 'unknown'
    genderCounts[gender] = (genderCounts[gender] || 0) + 1
  })

  const labels = Object.keys(genderCounts).map(gender => t(`patient.${gender}`))
  const data = Object.values(genderCounts) as number[]

  return {
    labels,
    datasets: [{
      data,
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(156, 163, 175, 0.8)'
      ],
      borderWidth: 0
    }]
  }
})

const appointmentsTimelineData = computed(() => {
  const last7Days: string[] = []
  const counts: Record<string, number> = {}

  // Generate last 7 days
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0] || ''
    if (dateStr) {
      last7Days.push(dateStr)
      counts[dateStr] = 0
    }
  }

  // Count appointments per day
  const appointments = Array.isArray(appointmentStore.appointments) ? appointmentStore.appointments : []
  appointments.forEach(apt => {
    if (apt.start) {
      const aptDate = apt.start.substring(0, 10)
      if (aptDate && aptDate in counts) {
        counts[aptDate] = (counts[aptDate] || 0) + 1
      }
    }
  })

  return {
    labels: last7Days.map(date => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [{
      label: t('appointment.appointments'),
      data: last7Days.map(date => counts[date] ?? 0),
      borderColor: 'rgba(59, 130, 246, 1)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  }
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    }
  }
}

const recentPatients = computed(() => {
  const patients = Array.isArray(patientStore.patients) ? patientStore.patients : []
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

  return [...patients]
    .filter(p => {
      if (!p.created_at) return false
      const createdDate = new Date(p.created_at)
      return createdDate >= sevenDaysAgo
    })
    .sort((a, b) => new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime())
    .slice(0, 5)
})

const recentAppointments = computed(() => {
  const appointments = Array.isArray(appointmentStore.appointments) ? appointmentStore.appointments : []
  return [...appointments]
    .sort((a, b) => new Date(b.start || 0).getTime() - new Date(a.start || 0).getTime())
    .slice(0, 5)
})

const getPatientName = (patient: Patient): string => {
  const name = patient.name?.[0]
  if (!name) return 'Unknown Patient'
  const given = name.given?.join(' ') || ''
  return `${given} ${name.family || ''}`.trim() || 'Unknown Patient'
}

const getInitials = (name: HumanName | undefined): string => {
  if (!name) return 'UP'
  const firstInitial = name.given?.[0]?.[0] || ''
  const lastInitial = name.family?.[0] || ''
  return (firstInitial + lastInitial).toUpperCase() || 'UP'
}

const getAppointmentPatientName = (appointment: Appointment): string => {
  const patientParticipant = appointment.participant?.find(
    p => p.actor?.reference?.startsWith('Patient/')
  )

  // Try to get display name first
  if (patientParticipant?.actor?.display) {
    return patientParticipant.actor.display
  }

  // Extract patient ID from reference and lookup in store
  const reference = patientParticipant?.actor?.reference
  if (reference) {
    const patientId = reference.replace('Patient/', '')
    const patient = patientStore.patients.find(p => p.id === patientId)
    if (patient) {
      return getPatientName(patient)
    }
  }

  return 'Unknown Patient'
}

const formatDateTime = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClass = (status: string): string => {
  const statusClasses: Record<string, string> = {
    proposed: 'bg-gray-100 text-gray-700',
    pending: 'bg-yellow-100 text-yellow-700',
    booked: 'bg-blue-100 text-blue-700',
    arrived: 'bg-purple-100 text-purple-700',
    fulfilled: 'bg-success-100 text-success-700',
    cancelled: 'bg-danger-100 text-danger-700',
    noshow: 'bg-orange-100 text-orange-700'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-700'
}
</script>
