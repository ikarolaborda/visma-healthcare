/**
 * API Service Layer
 * Handles all HTTP requests to the backend FHIR API with JWT authentication
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosError } from 'axios'
import type {
  Patient,
  Practitioner,
  Appointment,
  MedicationRequest,
  Observation,
  Invoice
} from '../types/fhir'
import type {
  PatientFormData,
  PractitionerFormData,
  AppointmentFormData
} from '../types'

// Use relative URL so requests go through nginx proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Track if we're currently refreshing the token to avoid race conditions
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string | null) => void
  reject: (error: any) => void
}> = []

const processQueue = (error: any, token: string | null = null): void => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          if (originalRequest.headers && token) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return apiClient(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refreshToken')

      if (!refreshToken) {
        // No refresh token, redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        // Try to refresh the token
        const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken
        })

        const newAccessToken = response.data.access
        localStorage.setItem('accessToken', newAccessToken)
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        }

        processQueue(null, newAccessToken)
        isRefreshing = false

        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        isRefreshing = false

        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'

        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

/**
 * Patient API Service
 */
export const patientService = {
  /**
   * Get all patients
   */
  async getAllPatients(): Promise<Patient[]> {
    try {
      const response = await apiClient.get<Patient[]>('/fhir/Patient/')
      return response.data
    } catch (error) {
      console.error('Error fetching patients:', error)
      throw error
    }
  },

  /**
   * Get a single patient by ID
   */
  async getPatientById(id: string): Promise<Patient> {
    try {
      const response = await apiClient.get<Patient>(`/fhir/Patient/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching patient ${id}:`, error)
      throw error
    }
  },

  /**
   * Create a new patient
   */
  async createPatient(patientData: Patient): Promise<Patient> {
    try {
      const response = await apiClient.post<Patient>('/fhir/Patient/', patientData)
      return response.data
    } catch (error) {
      console.error('Error creating patient:', error)
      throw error
    }
  },

  /**
   * Update an existing patient
   */
  async updatePatient(id: string, patientData: Patient): Promise<Patient> {
    try {
      const response = await apiClient.put<Patient>(`/fhir/Patient/${id}/`, patientData)
      return response.data
    } catch (error) {
      console.error(`Error updating patient ${id}:`, error)
      throw error
    }
  },

  /**
   * Delete a patient
   */
  async deletePatient(id: string): Promise<void> {
    try {
      await apiClient.delete(`/fhir/Patient/${id}/`)
    } catch (error) {
      console.error(`Error deleting patient ${id}:`, error)
      throw error
    }
  },
}

/**
 * Appointment API Service
 */
export const appointmentService = {
  /**
   * Get all appointments
   */
  async getAllAppointments(): Promise<Appointment[]> {
    try {
      const response = await apiClient.get<Appointment[]>('/fhir/Appointment/')
      return response.data
    } catch (error) {
      console.error('Error fetching appointments:', error)
      throw error
    }
  },

  /**
   * Get a single appointment by ID
   */
  async getAppointmentById(id: string): Promise<Appointment> {
    try {
      const response = await apiClient.get<Appointment>(`/fhir/Appointment/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching appointment ${id}:`, error)
      throw error
    }
  },

  /**
   * Get appointments for a specific patient
   */
  async getAppointmentsByPatient(patientId: string): Promise<Appointment[]> {
    try {
      const response = await apiClient.get<Appointment[]>(`/fhir/Appointment/?patient=${patientId}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching appointments for patient ${patientId}:`, error)
      throw error
    }
  },

  /**
   * Create a new appointment
   */
  async createAppointment(appointmentData: Appointment): Promise<Appointment> {
    try {
      const response = await apiClient.post<Appointment>('/fhir/Appointment/', appointmentData)
      return response.data
    } catch (error) {
      console.error('Error creating appointment:', error)
      throw error
    }
  },

  /**
   * Update an existing appointment
   */
  async updateAppointment(id: string, appointmentData: Appointment): Promise<Appointment> {
    try {
      const response = await apiClient.put<Appointment>(`/fhir/Appointment/${id}/`, appointmentData)
      return response.data
    } catch (error) {
      console.error(`Error updating appointment ${id}:`, error)
      throw error
    }
  },

  /**
   * Delete an appointment
   */
  async deleteAppointment(id: string): Promise<void> {
    try {
      await apiClient.delete(`/fhir/Appointment/${id}/`)
    } catch (error) {
      console.error(`Error deleting appointment ${id}:`, error)
      throw error
    }
  },

  /**
   * Cancel an appointment (update status to cancelled)
   */
  async cancelAppointment(id: string): Promise<Appointment> {
    try {
      const appointment = await this.getAppointmentById(id)
      appointment.status = 'cancelled'
      return await this.updateAppointment(id, appointment)
    } catch (error) {
      console.error(`Error cancelling appointment ${id}:`, error)
      throw error
    }
  },

  /**
   * Check-in an appointment (update status to arrived)
   */
  async checkInAppointment(id: string): Promise<Appointment> {
    try {
      const appointment = await this.getAppointmentById(id)
      appointment.status = 'arrived'
      return await this.updateAppointment(id, appointment)
    } catch (error) {
      console.error(`Error checking in appointment ${id}:`, error)
      throw error
    }
  },
}

/**
 * Practitioner API Service
 */
export const practitionerService = {
  /**
   * Get all practitioners
   */
  async getAllPractitioners(): Promise<Practitioner[]> {
    console.log('[PractitionerService] getAllPractitioners called')
    try {
      console.log('[PractitionerService] Making API request to /fhir/Practitioner/')
      const response = await apiClient.get<Practitioner[]>('/fhir/Practitioner/')
      console.log('[PractitionerService] Response received:', response.data.length, 'practitioners')
      console.log('[PractitionerService] First practitioner:', response.data[0])
      return response.data
    } catch (error) {
      console.error('[PractitionerService] Error fetching practitioners:', error)
      throw error
    }
  },

  /**
   * Get a single practitioner by ID
   */
  async getPractitionerById(id: string): Promise<Practitioner> {
    try {
      const response = await apiClient.get<Practitioner>(`/fhir/Practitioner/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching practitioner ${id}:`, error)
      throw error
    }
  },

  /**
   * Create a new practitioner
   */
  async createPractitioner(practitionerData: Practitioner): Promise<Practitioner> {
    try {
      const response = await apiClient.post<Practitioner>('/fhir/Practitioner/', practitionerData)
      return response.data
    } catch (error) {
      console.error('Error creating practitioner:', error)
      throw error
    }
  },

  /**
   * Update an existing practitioner
   */
  async updatePractitioner(id: string, practitionerData: Practitioner): Promise<Practitioner> {
    try {
      const response = await apiClient.put<Practitioner>(`/fhir/Practitioner/${id}/`, practitionerData)
      return response.data
    } catch (error) {
      console.error(`Error updating practitioner ${id}:`, error)
      throw error
    }
  },

  /**
   * Delete a practitioner
   */
  async deletePractitioner(id: string): Promise<void> {
    try {
      await apiClient.delete(`/fhir/Practitioner/${id}/`)
    } catch (error) {
      console.error(`Error deleting practitioner ${id}:`, error)
      throw error
    }
  },
}

/**
 * Prescription API Service
 */
export const prescriptionService = {
  async getAllPrescriptions(): Promise<MedicationRequest[]> {
    const response = await apiClient.get<MedicationRequest[]>('/fhir/MedicationRequest/')
    return response.data
  },

  async getPrescriptionById(id: string): Promise<MedicationRequest> {
    const response = await apiClient.get<MedicationRequest>(`/fhir/MedicationRequest/${id}/`)
    return response.data
  },

  async createPrescription(data: MedicationRequest): Promise<MedicationRequest> {
    const response = await apiClient.post<MedicationRequest>('/fhir/MedicationRequest/', data)
    return response.data
  },

  async updatePrescription(id: string, data: MedicationRequest): Promise<MedicationRequest> {
    const response = await apiClient.put<MedicationRequest>(`/fhir/MedicationRequest/${id}/`, data)
    return response.data
  },

  async deletePrescription(id: string): Promise<void> {
    await apiClient.delete(`/fhir/MedicationRequest/${id}/`)
  }
}

/**
 * Clinical Record (Patient History) API Service
 */
export const clinicalRecordService = {
  async getAllRecords(): Promise<Observation[]> {
    const response = await apiClient.get<Observation[]>('/fhir/ClinicalRecord/')
    return response.data
  },

  async getRecordById(id: string): Promise<Observation> {
    const response = await apiClient.get<Observation>(`/fhir/ClinicalRecord/${id}/`)
    return response.data
  },

  async createRecord(data: Observation): Promise<Observation> {
    const response = await apiClient.post<Observation>('/fhir/ClinicalRecord/', data)
    return response.data
  },

  async updateRecord(id: string, data: Observation): Promise<Observation> {
    const response = await apiClient.put<Observation>(`/fhir/ClinicalRecord/${id}/`, data)
    return response.data
  },

  async deleteRecord(id: string): Promise<void> {
    await apiClient.delete(`/fhir/ClinicalRecord/${id}/`)
  }
}

/**
 * Invoice (Billing) API Service
 */
export const invoiceService = {
  async getAllInvoices(): Promise<Invoice[]> {
    const response = await apiClient.get<Invoice[]>('/fhir/Invoice/')
    return response.data
  },

  async getInvoiceById(id: string): Promise<Invoice> {
    const response = await apiClient.get<Invoice>(`/fhir/Invoice/${id}/`)
    return response.data
  },

  async createInvoice(data: Invoice): Promise<Invoice> {
    const response = await apiClient.post<Invoice>('/fhir/Invoice/', data)
    return response.data
  },

  async updateInvoice(id: string, data: Invoice): Promise<Invoice> {
    const response = await apiClient.put<Invoice>(`/fhir/Invoice/${id}/`, data)
    return response.data
  },

  async deleteInvoice(id: string): Promise<void> {
    await apiClient.delete(`/fhir/Invoice/${id}/`)
  }
}

/**
 * Helper function to build FHIR Appointment resource from form data
 */
export function buildFHIRAppointment(formData: AppointmentFormData): Appointment {
  const appointment: Appointment = {
    resourceType: 'Appointment',
    status: (formData.status as Appointment['status']) || 'proposed',
    description: formData.description || undefined,
    start: formData.start,
    end: formData.end,
    minutesDuration: formData.minutesDuration || undefined,
    comment: formData.comment || undefined,
    participant: []
  }

  // Add patient participant
  if (formData.patientId) {
    appointment.participant.push({
      actor: {
        reference: `Patient/${formData.patientId}`,
        display: formData.patientName || undefined
      },
      status: 'accepted'
    })
  }

  // Add practitioner participant
  if (formData.practitionerId) {
    appointment.participant.push({
      actor: {
        reference: `Practitioner/${formData.practitionerId}`,
        display: formData.practitionerName || undefined
      },
      status: 'accepted'
    })
  }

  // Add service type
  if (formData.serviceType) {
    appointment.serviceType = [{
      text: formData.serviceType
    }]
  }

  // Add reason code
  if (formData.reason) {
    appointment.reasonCode = [{
      text: formData.reason
    }]
  }

  return appointment
}

/**
 * Helper function to extract form data from FHIR Appointment resource
 */
export function extractAppointmentFormData(fhirAppointment: Appointment): AppointmentFormData {
  const patientParticipant = fhirAppointment.participant?.find(
    p => p.actor?.reference?.startsWith('Patient/')
  )
  const practitionerParticipant = fhirAppointment.participant?.find(
    p => p.actor?.reference?.startsWith('Practitioner/')
  )

  return {
    id: fhirAppointment.id,
    status: fhirAppointment.status || 'proposed',
    description: fhirAppointment.description || '',
    start: fhirAppointment.start || '',
    end: fhirAppointment.end || '',
    minutesDuration: fhirAppointment.minutesDuration || 30,
    comment: fhirAppointment.comment || '',
    patientId: patientParticipant?.actor?.reference?.split('/')[1] || '',
    patientName: patientParticipant?.actor?.display || '',
    practitionerId: practitionerParticipant?.actor?.reference?.split('/')[1] || '',
    practitionerName: practitionerParticipant?.actor?.display || '',
    serviceType: fhirAppointment.serviceType?.[0]?.text || '',
    reason: fhirAppointment.reasonCode?.[0]?.text || ''
  }
}

/**
 * Helper function to build FHIR Patient resource from form data
 */
export function buildFHIRPatient(formData: PatientFormData): Patient {
  const patient: Patient = {
    resourceType: 'Patient',
    active: formData.active !== undefined ? formData.active : true,
    name: [
      {
        use: 'official',
        family: formData.familyName,
        given: [formData.givenName],
      },
    ],
    gender: formData.gender as Patient['gender'],
    birthDate: formData.birthDate,
  }

  // Add middle name if provided
  if (formData.middleName && patient.name?.[0]) {
    patient.name[0].given?.push(formData.middleName)
  }

  // Add address if provided
  if (formData.addressLine || formData.city || formData.state || formData.postalCode || formData.country) {
    patient.address = [
      {
        use: 'home',
        line: formData.addressLine ? [formData.addressLine] : undefined,
        city: formData.city || undefined,
        state: formData.state || undefined,
        postalCode: formData.postalCode || undefined,
        country: formData.country || undefined,
      },
    ]
  }

  // Add telecom (email/phone)
  patient.telecom = []
  if (formData.email) {
    patient.telecom.push({
      system: 'email',
      value: formData.email,
      use: 'home',
    })
  }
  if (formData.phone) {
    patient.telecom.push({
      system: 'phone',
      value: formData.phone,
      use: 'home',
    })
  }

  return patient
}

/**
 * Helper function to extract form data from FHIR Patient resource
 */
export function extractFormData(fhirPatient: Patient): PatientFormData {
  const name = fhirPatient.name?.[0] || {}
  const address = fhirPatient.address?.[0] || {}
  const email = fhirPatient.telecom?.find((t) => t.system === 'email')?.value
  const phone = fhirPatient.telecom?.find((t) => t.system === 'phone')?.value

  return {
    id: fhirPatient.id,
    familyName: name.family || '',
    givenName: name.given?.[0] || '',
    middleName: name.given?.[1] || '',
    gender: fhirPatient.gender || '',
    birthDate: fhirPatient.birthDate || '',
    addressLine: address.line?.[0] || '',
    city: address.city || '',
    state: address.state || '',
    postalCode: address.postalCode || '',
    country: address.country || '',
    email: email || '',
    phone: phone || '',
    active: fhirPatient.active !== undefined ? fhirPatient.active : true,
  }
}

/**
 * Helper function to build FHIR Practitioner resource from form data
 */
export function buildPractitioner(formData: PractitionerFormData): Practitioner {
  const practitioner: Practitioner = {
    resourceType: 'Practitioner',
    active: formData.active !== undefined ? formData.active : true,
    name: []
  }

  // Build name
  const nameData: any = {
    use: 'official',
    family: formData.familyName,
    given: [formData.givenName]
  }

  if (formData.middleName) {
    nameData.given.push(formData.middleName)
  }

  if (formData.prefix) {
    nameData.prefix = [formData.prefix]
  }

  practitioner.name?.push(nameData)

  // Add gender
  if (formData.gender) {
    practitioner.gender = formData.gender as Practitioner['gender']
  }

  // Add birth date
  if (formData.birthDate) {
    practitioner.birthDate = formData.birthDate
  }

  // Add identifiers
  practitioner.identifier = []
  if (formData.npi) {
    practitioner.identifier.push({
      system: 'http://hl7.org/fhir/sid/us-npi',
      value: formData.npi,
      use: 'official'
    })
  }

  if (formData.licenseNumber) {
    practitioner.identifier.push({
      system: 'http://hospital.example.org/practitioners/license',
      value: formData.licenseNumber,
      use: 'official'
    })
  }

  // Add address
  if (formData.addressLine || formData.city || formData.state || formData.postalCode || formData.country) {
    practitioner.address = [{
      use: 'work',
      line: formData.addressLine ? [formData.addressLine] : undefined,
      city: formData.city || undefined,
      state: formData.state || undefined,
      postalCode: formData.postalCode || undefined,
      country: formData.country || undefined
    }]
  }

  // Add telecom
  practitioner.telecom = []
  if (formData.email) {
    practitioner.telecom.push({
      system: 'email',
      value: formData.email,
      use: 'work'
    })
  }
  if (formData.phone) {
    practitioner.telecom.push({
      system: 'phone',
      value: formData.phone,
      use: 'work'
    })
  }

  // Add qualification
  if (formData.qualification) {
    practitioner.qualification = [{
      code: {
        text: formData.qualification
      }
    }]
  }

  // Add custom fields (non-standard FHIR but supported by backend)
  if (formData.specialization) {
    practitioner.specialization = formData.specialization
  }

  if (formData.yearsOfExperience) {
    practitioner.years_of_experience = formData.yearsOfExperience
  }

  return practitioner
}

/**
 * Helper function to extract form data from FHIR Practitioner resource
 */
export function extractPractitionerFormData(practitioner: Practitioner): PractitionerFormData {
  const name = practitioner.name?.[0] || {}
  const address = practitioner.address?.[0] || {}
  const email = practitioner.telecom?.find(t => t.system === 'email')?.value
  const phone = practitioner.telecom?.find(t => t.system === 'phone')?.value

  // Extract identifiers
  let npi = ''
  let licenseNumber = ''
  if (practitioner.identifier) {
    for (const identifier of practitioner.identifier) {
      if (identifier.system === 'http://hl7.org/fhir/sid/us-npi') {
        npi = identifier.value || ''
      } else if (identifier.system?.includes('license')) {
        licenseNumber = identifier.value || ''
      }
    }
  }

  return {
    id: practitioner.id,
    prefix: name.prefix?.[0] || '',
    familyName: name.family || '',
    givenName: name.given?.[0] || '',
    middleName: name.given?.[1] || '',
    gender: practitioner.gender || '',
    birthDate: practitioner.birthDate || '',
    npi: npi,
    licenseNumber: licenseNumber,
    specialization: practitioner.specialization || '',
    qualification: practitioner.qualification?.[0]?.code?.text || '',
    yearsOfExperience: practitioner.years_of_experience || 0,
    addressLine: address.line?.[0] || '',
    city: address.city || '',
    state: address.state || '',
    postalCode: address.postalCode || '',
    country: address.country || '',
    email: email || '',
    phone: phone || '',
    active: practitioner.active !== undefined ? practitioner.active : true
  }
}

export default apiClient
