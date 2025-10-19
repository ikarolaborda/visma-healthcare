<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? $t('appointment.editAppointment') : $t('appointment.addAppointment') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ isEditMode ? $t('appointment.updateDesc') : $t('appointment.createDesc') }}
        </p>
      </div>
      <router-link
        to="/appointments"
        class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
      >
        <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        {{ $t('common.back') }}
      </router-link>
    </div>

    <!-- Error Alert -->
    <div
      v-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4 animate-scale-in"
    >
      <div class="flex items-center">
        <svg class="h-5 w-5 text-danger-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-danger-700">{{ error }}</p>
      </div>
    </div>

    <!-- Appointment Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Schedule Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {{ $t('appointment.scheduleInfo') }}
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Start Date & Time -->
          <div>
            <label for="start" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.startTime') }} <span class="text-danger-500">*</span>
            </label>
            <input
              id="start"
              v-model="formData.start"
              type="datetime-local"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            />
          </div>

          <!-- End Date & Time -->
          <div>
            <label for="end" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.endTime') }} <span class="text-danger-500">*</span>
            </label>
            <input
              id="end"
              v-model="formData.end"
              type="datetime-local"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            />
          </div>

          <!-- Duration -->
          <div>
            <label for="minutesDuration" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.duration') }} ({{ $t('appointment.minutes') }})
            </label>
            <input
              id="minutesDuration"
              v-model.number="formData.minutesDuration"
              type="number"
              min="1"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="30"
            />
          </div>

          <!-- Status -->
          <div>
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('common.status') }} <span class="text-danger-500">*</span>
            </label>
            <select
              id="status"
              v-model="formData.status"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            >
              <option value="" disabled>{{ $t('appointment.selectStatus') }}</option>
              <option value="proposed">{{ $t('appointment.status.proposed') }}</option>
              <option value="pending">{{ $t('appointment.status.pending') }}</option>
              <option value="booked">{{ $t('appointment.status.booked') }}</option>
              <option value="arrived">{{ $t('appointment.status.arrived') }}</option>
              <option value="fulfilled">{{ $t('appointment.status.fulfilled') }}</option>
              <option value="cancelled">{{ $t('appointment.status.cancelled') }}</option>
              <option value="noshow">{{ $t('appointment.status.noshow') }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Participants Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {{ $t('appointment.participants') }}
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Patient -->
          <div>
            <label for="patientId" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.patient') }} <span class="text-danger-500">*</span>
            </label>
            <SearchableSelect
              v-model="formData.patientId"
              :options="patientOptions"
              :placeholder="$t('appointment.selectPatient')"
              required
            />
          </div>

          <!-- Practitioner -->
          <div>
            <label for="practitionerId" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.practitioner') }} <span class="text-danger-500">*</span>
            </label>
            <SearchableSelect
              v-model="formData.practitionerId"
              :options="practitionerOptions"
              :placeholder="$t('appointment.selectPractitioner')"
              required
            />
          </div>
        </div>
      </div>

      <!-- Appointment Details Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ $t('appointment.details') }}
          </h3>
        </div>

        <div class="space-y-6">
          <!-- Service Type -->
          <div>
            <label for="serviceType" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.serviceType') }}
            </label>
            <input
              id="serviceType"
              v-model="formData.serviceType"
              type="text"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="General Consultation, Check-up, Follow-up"
            />
          </div>

          <!-- Reason -->
          <div>
            <label for="reason" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.reason') }}
            </label>
            <input
              id="reason"
              v-model="formData.reason"
              type="text"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Annual physical exam"
            />
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.description') }}
            </label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="3"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Additional details about the appointment"
            ></textarea>
          </div>

          <!-- Comment/Notes -->
          <div>
            <label for="comment" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('appointment.notes') }}
            </label>
            <textarea
              id="comment"
              v-model="formData.comment"
              rows="3"
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
              placeholder="Internal notes about the appointment"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <router-link
          to="/appointments"
          class="px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          {{ $t('common.cancel') }}
        </router-link>
        <button
          type="submit"
          :disabled="loading"
          class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <svg
            v-if="loading"
            class="animate-spin h-5 w-5 mr-2 text-white"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ loading ? $t('common.saving') : (isEditMode ? $t('appointment.updateAppointment') : $t('appointment.createAppointment')) }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAppointmentStore } from '../stores/appointment'
import { usePatientStore } from '../stores/patient'
import { usePractitionerStore } from '../stores/practitioner'
import { buildFHIRAppointment, extractAppointmentFormData } from '../services/api'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import SearchableSelect from '../components/SearchableSelect.vue'
import type { Patient, Practitioner } from '../types/fhir'
import type { AppointmentFormData } from '../types'

const { t } = useI18n()
const toast = useToast()
const router = useRouter()
const route = useRoute()
const appointmentStore = useAppointmentStore()
const patientStore = usePatientStore()
const practitionerStore = usePractitionerStore()
const { loading, error } = storeToRefs(appointmentStore)
const { patients } = storeToRefs(patientStore)
const { practitioners } = storeToRefs(practitionerStore)

const isEditMode = computed(() => !!route.params.id)

const formData = ref<AppointmentFormData>({
  start: '',
  end: '',
  minutesDuration: 30,
  status: 'proposed',
  patientId: '',
  patientName: '',
  practitionerId: '',
  practitionerName: '',
  serviceType: '',
  reason: '',
  description: '',
  comment: ''
})

onMounted(async () => {
  // Load patients and practitioners for dropdowns
  await Promise.all([
    patientStore.fetchPatients(),
    practitionerStore.fetchPractitioners()
  ])

  // If editing, load appointment data
  if (isEditMode.value) {
    try {
      const appointment = await appointmentStore.fetchAppointmentById(route.params.id as string)
      formData.value = extractAppointmentFormData(appointment)
    } catch (err) {
      console.error('Failed to load appointment:', err)
      router.push('/appointments')
    }
  }

  // If patientId is in query params (coming from patient detail page)
  if (route.query.patientId) {
    formData.value.patientId = route.query.patientId as string
  }
})

const getPatientName = (patient: Patient): string => {
  const name = patient.name?.[0]
  if (!name) return 'Unknown Patient'
  const given = name.given?.join(' ') || ''
  return `${given} ${name.family || ''}`.trim() || 'Unknown Patient'
}

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

// Computed options for SearchableSelect components
const patientOptions = computed(() => {
  return patients.value.map(patient => ({
    label: getPatientName(patient),
    value: patient.id || ''
  }))
})

const practitionerOptions = computed(() => {
  return practitioners.value.map(practitioner => ({
    label: getPractitionerName(practitioner),
    value: practitioner.id || ''
  }))
})

const handleSubmit = async (): Promise<void> => {
  try {
    // Get patient name for display
    if (formData.value.patientId) {
      const patient = patients.value.find(p => p.id === formData.value.patientId)
      if (patient) {
        formData.value.patientName = getPatientName(patient)
      }
    }

    const fhirAppointment = buildFHIRAppointment(formData.value)

    if (isEditMode.value) {
      await appointmentStore.updateAppointment(route.params.id as string, fhirAppointment)
      toast.success(t('appointment.updateSuccess'))
    } else {
      await appointmentStore.createAppointment(fhirAppointment)
      toast.success(t('appointment.bookSuccess'))
    }

    router.push('/appointments')
  } catch (err) {
    console.error('Failed to save appointment:', err)
    toast.error(t(isEditMode.value ? 'appointment.updateError' : 'appointment.bookError'))
  }
}
</script>
