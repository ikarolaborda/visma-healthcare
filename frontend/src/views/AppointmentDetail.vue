<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Loading State -->
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 animate-pulse">
      <div class="space-y-4">
        <div class="h-8 bg-gray-200 rounded w-1/3"></div>
        <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        <div class="h-4 bg-gray-200 rounded w-2/3"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="glass rounded-2xl shadow-lg p-12 animate-scale-in">
      <div class="flex flex-col items-center space-y-4">
        <svg class="h-16 w-16 text-danger-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-xl font-semibold text-gray-900">{{ $t('common.error') }}</h3>
        <p class="text-gray-500">{{ error }}</p>
        <router-link
          to="/appointments"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 hover:shadow-lg transition-all duration-200 space-x-2"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>{{ $t('common.back') }}</span>
        </router-link>
      </div>
    </div>

    <!-- Appointment Details -->
    <div v-else-if="appointment" class="space-y-6">
      <!-- Header Section -->
      <div class="glass rounded-2xl shadow-lg overflow-hidden">
        <div class="bg-gradient-to-r from-primary-600 to-primary-700 px-8 py-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex items-center space-x-4">
              <div class="h-20 w-20 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg">
                <svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-white">{{ $t('appointment.appointmentDetails') }}</h1>
                <div class="flex items-center gap-3 mt-2">
                  <span
                    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getStatusClass(appointment.status)"
                  >
                    {{ $t(`appointment.status.${appointment.status}`) }}
                  </span>
                  <span class="text-white/80 text-sm">{{ formatDate(appointment.start) }}</span>
                </div>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <router-link
                v-if="appointment.status !== 'cancelled' && appointment.status !== 'fulfilled'"
                :to="`/appointments/${appointment.id}/edit`"
                class="inline-flex items-center px-6 py-3 bg-white text-primary-600 font-medium rounded-xl shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200 space-x-2"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>{{ $t('common.edit') }}</span>
              </router-link>
              <button
                v-if="canCheckIn"
                @click="handleCheckIn"
                class="inline-flex items-center px-6 py-3 bg-success-600 text-white font-medium rounded-xl shadow-md hover:bg-success-700 hover:shadow-lg hover:scale-105 transition-all duration-200 space-x-2"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ $t('appointment.checkIn') }}</span>
              </button>
              <button
                v-if="appointment.status !== 'cancelled' && appointment.status !== 'fulfilled'"
                @click="handleCancel"
                class="inline-flex items-center px-6 py-3 bg-danger-600 text-white font-medium rounded-xl shadow-md hover:bg-danger-700 hover:shadow-lg hover:scale-105 transition-all duration-200 space-x-2"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>{{ $t('appointment.cancelAppointment') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Time & Duration -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ $t('appointment.scheduleInfo') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.startTime') }}</label>
            <p class="text-lg text-gray-900">{{ formatDateTime(appointment.start) }}</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.endTime') }}</label>
            <p class="text-lg text-gray-900">{{ formatDateTime(appointment.end) }}</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.duration') }}</label>
            <p class="text-lg text-gray-900">
              {{ appointment.minutesDuration || calculateDuration(appointment.start, appointment.end) }} {{ $t('appointment.minutes') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Participants -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          {{ $t('appointment.participants') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-if="getPatientInfo()" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.patient') }}</label>
            <div class="flex items-center space-x-2">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <router-link
                v-if="getPatientId()"
                :to="`/patient/${getPatientId()}`"
                class="text-lg text-primary-600 hover:text-primary-700 hover:underline"
              >
                {{ getPatientInfo() }}
              </router-link>
              <p v-else class="text-lg text-gray-900">{{ getPatientInfo() }}</p>
            </div>
          </div>
          <div v-if="getPractitionerInfo()" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.practitioner') }}</label>
            <div class="flex items-center space-x-2">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-lg text-gray-900">{{ getPractitionerInfo() }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Details -->
      <div v-if="hasDetails" class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {{ $t('appointment.details') }}
        </h2>
        <div class="space-y-6">
          <div v-if="getServiceType()" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.serviceType') }}</label>
            <p class="text-lg text-gray-900">{{ getServiceType() }}</p>
          </div>
          <div v-if="getReason()" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.reason') }}</label>
            <p class="text-lg text-gray-900">{{ getReason() }}</p>
          </div>
          <div v-if="appointment.description" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.description') }}</label>
            <p class="text-lg text-gray-900">{{ appointment.description }}</p>
          </div>
          <div v-if="appointment.comment" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('appointment.notes') }}</label>
            <p class="text-lg text-gray-900">{{ appointment.comment }}</p>
          </div>
        </div>
      </div>

      <!-- Back Button -->
      <div class="flex justify-start">
        <router-link
          to="/appointments"
          class="inline-flex items-center px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-xl shadow-md hover:bg-gray-200 hover:shadow-lg transition-all duration-200 space-x-2"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>{{ $t('common.back') }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppointmentStore } from '../stores/appointment'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const appointmentStore = useAppointmentStore()
const { loading, error } = storeToRefs(appointmentStore)

const appointment = ref(null)

onMounted(async () => {
  try {
    appointment.value = await appointmentStore.fetchAppointmentById(route.params.id)
  } catch (error) {
    console.error('Error fetching appointment:', error)
  }
})

const canCheckIn = computed(() => {
  return appointment.value?.status === 'booked' || appointment.value?.status === 'pending'
})

const hasDetails = computed(() => {
  return getServiceType() || getReason() || appointment.value?.description || appointment.value?.comment
})

const getPatientInfo = () => {
  const patientParticipant = appointment.value?.participant?.find(
    p => p.actor?.reference?.startsWith('Patient/')
  )
  return patientParticipant?.actor?.display || 'N/A'
}

const getPatientId = () => {
  const patientParticipant = appointment.value?.participant?.find(
    p => p.actor?.reference?.startsWith('Patient/')
  )
  return patientParticipant?.actor?.reference?.split('/')[1] || null
}

const getPractitionerInfo = () => {
  const practitionerParticipant = appointment.value?.participant?.find(
    p => p.actor?.reference?.startsWith('Practitioner/')
  )
  return practitionerParticipant?.actor?.display || null
}

const getServiceType = () => {
  return appointment.value?.serviceType?.[0]?.coding?.[0]?.display || ''
}

const getReason = () => {
  return appointment.value?.reasonCode?.[0]?.text || ''
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

const formatDateTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateDuration = (start, end) => {
  if (!start || !end) return 'N/A'
  const startDate = new Date(start)
  const endDate = new Date(end)
  const diffMs = endDate - startDate
  return Math.round(diffMs / 1000 / 60)
}

const getStatusClass = (status) => {
  const statusClasses = {
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

const handleCheckIn = async () => {
  try {
    await appointmentStore.checkInAppointment(route.params.id)
    appointment.value = await appointmentStore.fetchAppointmentById(route.params.id)
    alert(t('appointment.checkInSuccess'))
  } catch (error) {
    alert(t('appointment.checkInError'))
  }
}

const handleCancel = async () => {
  if (confirm(t('appointment.confirmCancel'))) {
    try {
      await appointmentStore.cancelAppointment(route.params.id)
      appointment.value = await appointmentStore.fetchAppointmentById(route.params.id)
      alert(t('appointment.cancelSuccess'))
    } catch (error) {
      alert(t('appointment.cancelError'))
    }
  }
}
</script>
