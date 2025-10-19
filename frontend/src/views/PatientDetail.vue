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
          to="/"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 hover:shadow-lg transition-all duration-200 space-x-2"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>{{ $t('common.back') }}</span>
        </router-link>
      </div>
    </div>

    <!-- Patient Details -->
    <div v-else-if="patient" class="space-y-6">
      <!-- Header Section -->
      <div class="glass rounded-2xl shadow-lg overflow-hidden">
        <div class="bg-gradient-to-r from-primary-600 to-primary-700 px-8 py-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div class="flex items-center space-x-4">
              <div class="h-20 w-20 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg">
                <span class="text-white font-bold text-3xl">
                  {{ getInitials() }}
                </span>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-white">{{ getPatientName() }}</h1>
                <div class="flex items-center gap-3 mt-2">
                  <span
                    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="patient.active ? 'bg-success-100 text-success-700' : 'bg-gray-100 text-gray-700'"
                  >
                    {{ patient.active ? $t('common.active') : $t('common.inactive') }}
                  </span>
                  <span class="text-white/80 text-sm capitalize">{{ patient.gender }}</span>
                </div>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <router-link
                :to="`/patient/${patient.id}/edit`"
                class="inline-flex items-center px-6 py-3 bg-white text-primary-600 font-medium rounded-xl shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200 space-x-2"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span>{{ $t('common.edit') }}</span>
              </router-link>
              <button
                @click="handleDelete"
                class="inline-flex items-center px-6 py-3 bg-danger-600 text-white font-medium rounded-xl shadow-md hover:bg-danger-700 hover:shadow-lg hover:scale-105 transition-all duration-200 space-x-2"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>{{ $t('common.delete') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Personal Information -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          {{ $t('patient.personalInfo') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('patient.fullName') }}</label>
            <p class="text-lg text-gray-900">{{ getPatientName() }}</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('patient.gender') }}</label>
            <p class="text-lg text-gray-900 capitalize">{{ patient.gender }}</p>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('patient.birthDate') }}</label>
            <p class="text-lg text-gray-900">{{ formatDate(patient.birthDate) }}</p>
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div v-if="hasContactInfo" class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {{ $t('patient.contactInfo') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-if="getEmail()" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('patient.email') }}</label>
            <div class="flex items-center space-x-2">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <p class="text-lg text-gray-900">{{ getEmail() }}</p>
            </div>
          </div>
          <div v-if="getPhone()" class="space-y-2">
            <label class="text-sm font-semibold text-gray-500 uppercase tracking-wider">{{ $t('patient.phone') }}</label>
            <div class="flex items-center space-x-2">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <p class="text-lg text-gray-900">{{ getPhone() }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Address -->
      <div v-if="hasAddress" class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {{ $t('patient.address') }}
        </h2>
        <p class="text-lg text-gray-900">{{ getAddress() }}</p>
      </div>

      <!-- Appointments Section -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900 flex items-center">
            <svg class="h-6 w-6 mr-3 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ $t('appointment.appointments') }}
          </h2>
          <router-link
            :to="`/appointments/add?patientId=${patient.id}`"
            class="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors duration-200 space-x-2"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>{{ $t('appointment.bookAppointment') }}</span>
          </router-link>
        </div>

        <!-- Loading State -->
        <div v-if="appointmentsLoading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p class="mt-2 text-sm text-gray-500">{{ $t('common.loading') }}</p>
        </div>

        <!-- No Appointments -->
        <div v-else-if="!patientAppointments || patientAppointments.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">{{ $t('appointment.noAppointments') }}</h3>
          <p class="mt-1 text-sm text-gray-500">{{ $t('appointment.noAppointmentsForPatient') }}</p>
          <div class="mt-6">
            <router-link
              :to="`/appointments/add?patientId=${patient.id}`"
              class="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors space-x-2"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>{{ $t('appointment.bookAppointment') }}</span>
            </router-link>
          </div>
        </div>

        <!-- Appointments List -->
        <div v-else class="space-y-4">
          <div
            v-for="apt in patientAppointments.slice(0, 5)"
            :key="apt.id"
            class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:bg-primary-50/30 transition-all duration-200"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                    :class="getAppointmentStatusClass(apt.status)"
                  >
                    {{ $t(`appointment.status.${apt.status}`) }}
                  </span>
                  <span class="text-sm text-gray-500">{{ formatAppointmentDate(apt.start) }}</span>
                </div>
                <p class="text-sm text-gray-900 font-medium">{{ getAppointmentReason(apt) }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ formatAppointmentTime(apt.start) }}</p>
              </div>
              <router-link
                :to="`/appointments/${apt.id}`"
                class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
              >
                {{ $t('common.view') }}
                <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </div>
          </div>

          <!-- View All Link -->
          <div v-if="patientAppointments.length > 5" class="text-center pt-4 border-t border-gray-200">
            <router-link
              to="/appointments"
              class="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              {{ $t('appointment.viewAll') }} ({{ patientAppointments.length }})
            </router-link>
          </div>
        </div>
      </div>

      <!-- Back Button -->
      <div class="flex justify-start">
        <router-link
          to="/"
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
import { usePatientStore } from '../stores/patient'
import { useAppointmentStore } from '../stores/appointment'
import { useI18n } from 'vue-i18n'
import { useToast } from 'vue-toastification'
import { storeToRefs } from 'pinia'
import type { Patient, Appointment } from '../types/fhir'

const { t } = useI18n()
const toast = useToast()
const router = useRouter()
const route = useRoute()
const patientStore = usePatientStore()
const appointmentStore = useAppointmentStore()
const { loading, error } = storeToRefs(patientStore)

const patient = ref<Patient | null>(null)
const patientAppointments = ref<Appointment[]>([])
const appointmentsLoading = ref<boolean>(false)

onMounted(async () => {
  try {
    patient.value = await patientStore.fetchPatientById(route.params.id as string)

    // Load appointments for this patient
    appointmentsLoading.value = true
    try {
      patientAppointments.value = await appointmentStore.fetchAppointmentsByPatient(route.params.id as string)
      // Sort by date (most recent first)
      patientAppointments.value.sort((a, b) => new Date(b.start || 0).getTime() - new Date(a.start || 0).getTime())
    } catch (aptError) {
      console.error('Error fetching appointments:', aptError)
    } finally {
      appointmentsLoading.value = false
    }
  } catch (error) {
    console.error('Error fetching patient:', error)
  }
})

const getPatientName = (): string => {
  const name = patient.value?.name?.[0]
  if (!name) return 'N/A'
  const given = name.given?.join(' ') || ''
  return `${given} ${name.family || ''}`.trim()
}

const getInitials = (): string => {
  const name = patient.value?.name?.[0]
  if (!name) return 'UP'
  const firstInitial = name.given?.[0]?.[0] || ''
  const lastInitial = name.family?.[0] || ''
  return (firstInitial + lastInitial).toUpperCase() || 'UP'
}

const getEmail = (): string | null => {
  return patient.value?.telecom?.find(t => t.system === 'email')?.value || null
}

const getPhone = (): string | null => {
  return patient.value?.telecom?.find(t => t.system === 'phone')?.value || null
}

const getAddress = (): string => {
  const address = patient.value?.address?.[0]
  if (!address) return 'N/A'

  const parts = [
    address.line?.join(', '),
    address.city,
    address.state,
    address.postalCode,
    address.country,
  ].filter(Boolean)

  return parts.join(', ') || 'N/A'
}

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const hasContactInfo = computed(() => getEmail() || getPhone())
const hasAddress = computed(() => {
  const address = patient.value?.address?.[0]
  return address && (address.line || address.city || address.state || address.postalCode || address.country)
})

const handleDelete = async (): Promise<void> => {
  if (confirm(t('patient.confirmDelete', { name: getPatientName() }))) {
    try {
      await patientStore.deletePatient(route.params.id as string)
      toast.success(t('patient.deleteSuccess'))
      router.push('/')
    } catch (error) {
      toast.error(t('patient.deleteError'))
    }
  }
}

const getAppointmentReason = (appointment: Appointment): string => {
  return appointment.reasonCode?.[0]?.text || appointment.description || t('appointment.noReason')
}

const formatAppointmentDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatAppointmentTime = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAppointmentStatusClass = (status: string): string => {
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
</script>
