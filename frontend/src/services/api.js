/**
 * API Service Layer
 * Handles all HTTP requests to the backend FHIR API with JWT authentication
 */
import axios from 'axios'

// Use relative URL so requests go through nginx proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Track if we're currently refreshing the token to avoid race conditions
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
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
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
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
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`

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
   * @returns {Promise} FHIR Bundle with all patients
   */
  async getAllPatients() {
    try {
      const response = await apiClient.get('/fhir/Patient/')
      return response.data
    } catch (error) {
      console.error('Error fetching patients:', error)
      throw error
    }
  },

  /**
   * Get a single patient by ID
   * @param {string} id - Patient UUID
   * @returns {Promise} FHIR Patient resource
   */
  async getPatientById(id) {
    try {
      const response = await apiClient.get(`/fhir/Patient/${id}/`)
      return response.data
    } catch (error) {
      console.error(`Error fetching patient ${id}:`, error)
      throw error
    }
  },

  /**
   * Create a new patient
   * @param {Object} patientData - FHIR Patient resource
   * @returns {Promise} Created FHIR Patient resource
   */
  async createPatient(patientData) {
    try {
      const response = await apiClient.post('/fhir/Patient/', patientData)
      return response.data
    } catch (error) {
      console.error('Error creating patient:', error)
      throw error
    }
  },

  /**
   * Update an existing patient
   * @param {string} id - Patient UUID
   * @param {Object} patientData - FHIR Patient resource
   * @returns {Promise} Updated FHIR Patient resource
   */
  async updatePatient(id, patientData) {
    try {
      const response = await apiClient.put(`/fhir/Patient/${id}/`, patientData)
      return response.data
    } catch (error) {
      console.error(`Error updating patient ${id}:`, error)
      throw error
    }
  },

  /**
   * Delete a patient
   * @param {string} id - Patient UUID
   * @returns {Promise}
   */
  async deletePatient(id) {
    try {
      await apiClient.delete(`/fhir/Patient/${id}/`)
    } catch (error) {
      console.error(`Error deleting patient ${id}:`, error)
      throw error
    }
  },
}

/**
 * Helper function to build FHIR Patient resource from form data
 * @param {Object} formData - Form data from Vue component
 * @returns {Object} FHIR Patient resource
 */
export function buildFHIRPatient(formData) {
  const patient = {
    resourceType: 'Patient',
    active: formData.active !== undefined ? formData.active : true,
    name: [
      {
        use: 'official',
        family: formData.familyName,
        given: [formData.givenName],
      },
    ],
    gender: formData.gender,
    birthDate: formData.birthDate,
  }

  // Add middle name if provided
  if (formData.middleName) {
    patient.name[0].given.push(formData.middleName)
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
 * @param {Object} fhirPatient - FHIR Patient resource
 * @returns {Object} Form data for Vue component
 */
export function extractFormData(fhirPatient) {
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

export default apiClient
