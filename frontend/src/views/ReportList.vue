<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Reports</h1>
        <p class="mt-1 text-sm text-gray-500">Generate and download reports in various formats</p>
      </div>
      <button
        @click="showGenerateModal = true"
        class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 space-x-2"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Generate Report</span>
      </button>
    </div>

    <!-- Filter Tabs -->
    <div class="flex space-x-2 border-b border-gray-200">
      <button
        v-for="status in ['all', 'completed', 'processing', 'failed']"
        :key="status"
        @click="filterStatus = status"
        :class="[
          'px-4 py-2 font-medium text-sm transition-all duration-200',
          filterStatus === status
            ? 'border-b-2 border-primary-600 text-primary-600'
            : 'text-gray-500 hover:text-gray-700'
        ]"
      >
        {{ status.charAt(0).toUpperCase() + status.slice(1) }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="text-gray-500 mt-4">Loading reports...</p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="filteredReports.length === 0"
      class="glass rounded-2xl shadow-lg p-12 text-center"
    >
      <div class="flex flex-col items-center space-y-4">
        <div class="h-24 w-24 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
          <svg class="h-12 w-12 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-900">No Reports Found</h3>
        <p class="text-gray-500 max-w-sm">Generate your first report to get started</p>
        <button
          @click="showGenerateModal = true"
          class="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-xl shadow-md hover:bg-primary-700 transition-all"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Generate Report
        </button>
      </div>
    </div>

    <!-- Reports Grid -->
    <div v-else class="grid grid-cols-1 gap-6">
      <div
        v-for="report in filteredReports"
        :key="report.id"
        class="glass rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-3">
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                :class="getStatusClass(report.status)"
              >
                {{ report.status }}
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                {{ report.format.toUpperCase() }}
              </span>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                {{ formatReportType(report.report_type) }}
              </span>
            </div>

            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ report.title }}</h3>
            <p v-if="report.description" class="text-sm text-gray-600 mb-3">{{ report.description }}</p>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
              <div>
                <span class="font-medium">Generated:</span> {{ formatDate(report.created_at) }}
              </div>
              <div v-if="report.record_count">
                <span class="font-medium">Records:</span> {{ report.record_count }}
              </div>
              <div v-if="report.file_size">
                <span class="font-medium">Size:</span> {{ formatFileSize(report.file_size) }}
              </div>
            </div>

            <p v-if="report.error_message" class="text-sm text-red-600 bg-red-50 rounded-lg p-3 mt-3">
              {{ report.error_message }}
            </p>
          </div>

          <div class="flex items-center space-x-2 ml-4">
            <button
              v-if="report.status === 'completed' && report.file"
              @click="handleDownload(report.id, report.title, report.format)"
              class="p-2 text-success-600 hover:bg-success-50 rounded-lg transition-colors"
              title="Download"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>
            <button
              @click="handleDelete(report.id, report.title)"
              class="p-2 text-danger-600 hover:bg-danger-50 rounded-lg transition-colors"
              title="Delete"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Generate Report Modal -->
    <div v-if="showGenerateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="glass rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">Generate Report</h2>
            <button
              @click="closeModal"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleGenerate" class="space-y-6">
            <!-- Basic Information Section -->
            <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 space-y-6">
              <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Basic Information
              </h3>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Report Type -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Report Type *</label>
                  <select
                    v-model="formData.report_type"
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                  >
                    <option value="">Select report type</option>
                    <option value="patients">Patients</option>
                    <option value="practitioners">Practitioners</option>
                    <option value="appointments">Appointments</option>
                    <option value="prescriptions">Prescriptions</option>
                    <option value="invoices">Invoices</option>
                    <option value="clinical_records">Clinical Records</option>
                  </select>
                </div>

                <!-- Format -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Output Format *</label>
                  <div class="grid grid-cols-4 gap-2">
                    <button
                      v-for="format in ['pdf', 'csv', 'txt', 'json']"
                      :key="format"
                      type="button"
                      @click="formData.format = format"
                      :class="[
                        'px-3 py-2 border-2 rounded-lg font-medium transition-all text-sm',
                        formData.format === format
                          ? 'border-primary-600 bg-primary-50 text-primary-700'
                          : 'border-gray-200 text-gray-700 hover:border-gray-300 bg-white'
                      ]"
                    >
                      {{ format.toUpperCase() }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Title -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Report Title *</label>
                <input
                  v-model="formData.title"
                  type="text"
                  required
                  placeholder="e.g., Monthly Patient Report"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                />
              </div>

              <!-- Description -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
                <textarea
                  v-model="formData.description"
                  rows="2"
                  placeholder="Brief description of the report"
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                ></textarea>
              </div>
            </div>

            <!-- Advanced Filters Section -->
            <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 space-y-6">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                  <svg class="h-5 w-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  Advanced Filters
                </h3>
                <button
                  type="button"
                  @click="showAdvancedFilters = !showAdvancedFilters"
                  class="text-sm text-purple-600 hover:text-purple-700 font-medium flex items-center"
                >
                  <span>{{ showAdvancedFilters ? 'Hide' : 'Show' }}</span>
                  <svg
                    class="h-4 w-4 ml-1 transition-transform"
                    :class="{ 'rotate-180': showAdvancedFilters }"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              <div v-show="showAdvancedFilters" class="space-y-4">
                <!-- Date Range -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Date From</label>
                    <input
                      v-model="formData.date_from"
                      type="date"
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Date To</label>
                    <input
                      v-model="formData.date_to"
                      type="date"
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                    />
                  </div>
                </div>

                <!-- Practitioner Filter -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Practitioner</label>
                  <select
                    v-model="formData.practitioner_id"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                  >
                    <option value="">All Practitioners</option>
                    <option v-for="practitioner in activePractitioners" :key="practitioner.id" :value="practitioner.id">
                      {{ getPractitionerName(practitioner) }}
                      <span v-if="practitioner.specialization"> - {{ practitioner.specialization }}</span>
                    </option>
                  </select>
                </div>

                <!-- Patient Filter -->
                <div v-if="formData.report_type === 'appointments' || formData.report_type === 'prescriptions' || formData.report_type === 'clinical_records'">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Patient (Optional)</label>
                  <select
                    v-model="formData.patient_id"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                  >
                    <option value="">All Patients</option>
                    <option v-for="patient in activePatients" :key="patient.id" :value="patient.id">
                      {{ getPatientName(patient) }}
                    </option>
                  </select>
                </div>

                <!-- Status Filter (for appointments) -->
                <div v-if="formData.report_type === 'appointments'">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Appointment Status</label>
                  <select
                    v-model="formData.status"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                  >
                    <option value="">All Statuses</option>
                    <option value="proposed">Proposed</option>
                    <option value="pending">Pending</option>
                    <option value="booked">Booked</option>
                    <option value="arrived">Arrived</option>
                    <option value="fulfilled">Fulfilled</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="noshow">No Show</option>
                  </select>
                </div>

                <!-- Billing Type Filter (for invoices) -->
                <div v-if="formData.report_type === 'invoices'">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Billing Type</label>
                  <select
                    v-model="formData.billing_type"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all bg-white"
                  >
                    <option value="">All Types</option>
                    <option value="insurance">Insurance</option>
                    <option value="self_pay">Self Pay</option>
                    <option value="medicare">Medicare</option>
                    <option value="medicaid">Medicaid</option>
                  </select>
                </div>

                <!-- Include Inactive Toggle -->
                <div class="flex items-center space-x-3 bg-white rounded-xl p-4 border border-gray-200">
                  <input
                    v-model="formData.include_inactive"
                    type="checkbox"
                    id="include-inactive"
                    class="h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label for="include-inactive" class="text-sm font-medium text-gray-700 cursor-pointer">
                    Include inactive records
                  </label>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                @click="closeModal"
                class="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="generating"
                class="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <span v-if="generating" class="flex items-center">
                  <svg class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </span>
                <span v-else class="flex items-center">
                  <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Generate Report
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useReportStore } from '../stores/report'
import { usePractitionerStore } from '../stores/practitioner'
import { usePatientStore } from '../stores/patient'
import { storeToRefs } from 'pinia'
import type { Practitioner, Patient } from '../types/fhir'

const toast = useToast()
const reportStore = useReportStore()
const practitionerStore = usePractitionerStore()
const patientStore = usePatientStore()

const { reports, loading } = storeToRefs(reportStore)
const { practitioners } = storeToRefs(practitionerStore)
const { patients } = storeToRefs(patientStore)

const showGenerateModal = ref(false)
const showAdvancedFilters = ref(false)
const generating = ref(false)
const filterStatus = ref('all')

const formData = ref({
  report_type: '',
  format: 'pdf',
  title: '',
  description: '',
  date_from: '',
  date_to: '',
  practitioner_id: '',
  patient_id: '',
  status: '',
  billing_type: '',
  include_inactive: false,
  filters: {}
})

onMounted(async () => {
  await Promise.all([
    reportStore.fetchReports(),
    practitionerStore.fetchPractitioners(),
    patientStore.fetchPatients()
  ])
})

// Computed properties for filtered lists
const activePractitioners = computed(() => {
  if (!Array.isArray(practitioners.value)) return []
  return practitioners.value.filter((p: Practitioner) => p.active)
})

const activePatients = computed(() => {
  if (!Array.isArray(patients.value)) return []
  return patients.value.filter((p: Patient) => p.active !== false)
})

// Helper functions for formatting names
const getPractitionerName = (practitioner: Practitioner): string => {
  if (!practitioner.name || !practitioner.name[0]) return 'Unknown'
  const name = practitioner.name[0]
  const given = name.given?.join(' ') || ''
  const family = name.family || ''
  return `${given} ${family}`.trim() || 'Unknown'
}

const getPatientName = (patient: Patient): string => {
  if (!patient.name || !patient.name[0]) return 'Unknown'
  const name = patient.name[0]
  const given = name.given?.join(' ') || ''
  const family = name.family || ''
  return `${given} ${family}`.trim() || 'Unknown'
}

const filteredReports = computed(() => {
  const validReports = reports.value.filter((r: any) => r && r.id)
  if (filterStatus.value === 'all') {
    return validReports
  }
  return validReports.filter((r: any) => r.status === filterStatus.value)
})

const formatDate = (dateStr: string): string => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes: number): string => {
  if (!bytes) return 'N/A'
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(2)} KB`
  const mb = kb / 1024
  return `${mb.toFixed(2)} MB`
}

const formatReportType = (type: string): string => {
  const typeMap: Record<string, string> = {
    patients: 'Patients',
    practitioners: 'Practitioners',
    appointments: 'Appointments',
    prescriptions: 'Prescriptions',
    invoices: 'Invoices',
    clinical_records: 'Clinical Records'
  }
  return typeMap[type] || type
}

const getStatusClass = (status: string): string => {
  const statusClasses: Record<string, string> = {
    completed: 'bg-success-100 text-success-700',
    processing: 'bg-blue-100 text-blue-700',
    failed: 'bg-danger-100 text-danger-700',
    pending: 'bg-yellow-100 text-yellow-700'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-700'
}

const handleDownload = async (id: string, title: string, format: string) => {
  try {
    const blob = await reportStore.downloadReport(id)

    // Create a temporary URL for the blob
    const url = window.URL.createObjectURL(blob)

    // Create a temporary anchor element and trigger download
    const link = document.createElement('a')
    link.href = url
    link.download = `${title}.${format}`
    document.body.appendChild(link)
    link.click()

    // Clean up
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Download error:', err)
    toast.error('Failed to download report')
  }
}

const closeModal = () => {
  showGenerateModal.value = false
  showAdvancedFilters.value = false
  formData.value = {
    report_type: '',
    format: 'pdf',
    title: '',
    description: '',
    date_from: '',
    date_to: '',
    practitioner_id: '',
    patient_id: '',
    status: '',
    billing_type: '',
    include_inactive: false,
    filters: {}
  }
}

const handleGenerate = async () => {
  generating.value = true
  try {
    // Prepare data with enhanced filter fields
    const reportData: any = {
      report_type: formData.value.report_type,
      format: formData.value.format,
      title: formData.value.title,
      description: formData.value.description
    }

    // Add filter fields if they have values
    if (formData.value.date_from) {
      reportData.date_from = formData.value.date_from
    }
    if (formData.value.date_to) {
      reportData.date_to = formData.value.date_to
    }
    if (formData.value.practitioner_id) {
      reportData.practitioner_id = formData.value.practitioner_id
    }
    if (formData.value.patient_id) {
      reportData.patient_id = formData.value.patient_id
    }
    if (formData.value.status) {
      reportData.status = formData.value.status
    }
    if (formData.value.billing_type) {
      reportData.billing_type = formData.value.billing_type
    }
    if (formData.value.include_inactive) {
      reportData.include_inactive = formData.value.include_inactive
    }

    await reportStore.generateReport(reportData)
    toast.success('Report generated successfully!')
    closeModal()
    await reportStore.fetchReports()
  } catch (err) {
    console.error('Generate error:', err)
    toast.error('Failed to generate report')
  } finally {
    generating.value = false
  }
}

const handleDelete = async (id: string, title: string) => {
  if (confirm(`Are you sure you want to delete "${title}"?`)) {
    try {
      await reportStore.deleteReport(id)
      toast.success('Report deleted successfully')
    } catch (err) {
      console.error('Delete error:', err)
      toast.error('Failed to delete report')
    }
  }
}
</script>
