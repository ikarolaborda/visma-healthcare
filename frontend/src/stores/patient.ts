/**
 * Pinia store for patient management
 * Implements state management following best practices
 */
import { defineStore } from 'pinia'
import { patientService } from '../services/api'
import type { Patient } from '../types/fhir'

interface PatientState {
  patients: Patient[]
  currentPatient: Patient | null
  loading: boolean
  error: string | null
}

export const usePatientStore = defineStore('patient', {
  state: (): PatientState => ({
    patients: [],
    currentPatient: null,
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get all patients sorted by creation date
     */
    sortedPatients: (state): Patient[] => {
      if (!Array.isArray(state.patients)) {
        return []
      }
      return [...state.patients].sort((a, b) => {
        const dateA = new Date(a.meta?.lastUpdated || 0).getTime()
        const dateB = new Date(b.meta?.lastUpdated || 0).getTime()
        return dateB - dateA
      })
    },

    /**
     * Get patient by ID
     */
    getPatientById: (state) => {
      return (id: string): Patient | undefined => {
        if (!Array.isArray(state.patients)) {
          return undefined
        }
        return state.patients.find((p) => p.id === id)
      }
    },

    /**
     * Check if patients are loaded
     */
    hasPatients: (state): boolean => {
      return Array.isArray(state.patients) && state.patients.length > 0
    },
  },

  actions: {
    /**
     * Fetch all patients from API
     */
    async fetchPatients(): Promise<void> {
      this.loading = true
      this.error = null

      try {
        const patients = await patientService.getAllPatients()
        this.patients = patients
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch patients'
        console.error('Error fetching patients:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single patient by ID
     */
    async fetchPatientById(id: string): Promise<Patient> {
      this.loading = true
      this.error = null

      try {
        this.currentPatient = await patientService.getPatientById(id)
        return this.currentPatient
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch patient'
        console.error(`Error fetching patient ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new patient
     */
    async createPatient(patientData: Patient): Promise<Patient> {
      this.loading = true
      this.error = null

      try {
        const newPatient = await patientService.createPatient(patientData)
        this.patients.push(newPatient)
        return newPatient
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to create patient'
        console.error('Error creating patient:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing patient
     */
    async updatePatient(id: string, patientData: Patient): Promise<Patient> {
      this.loading = true
      this.error = null

      try {
        const updatedPatient = await patientService.updatePatient(id, patientData)

        // Update in local state
        const index = this.patients.findIndex((p) => p.id === id)
        if (index !== -1) {
          this.patients[index] = updatedPatient
        }

        if (this.currentPatient?.id === id) {
          this.currentPatient = updatedPatient
        }

        return updatedPatient
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to update patient'
        console.error(`Error updating patient ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete a patient
     */
    async deletePatient(id: string): Promise<void> {
      this.loading = true
      this.error = null

      try {
        await patientService.deletePatient(id)

        // Remove from local state
        this.patients = this.patients.filter((p) => p.id !== id)

        if (this.currentPatient?.id === id) {
          this.currentPatient = null
        }
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to delete patient'
        console.error(`Error deleting patient ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Clear error state
     */
    clearError(): void {
      this.error = null
    },

    /**
     * Clear current patient
     */
    clearCurrentPatient(): void {
      this.currentPatient = null
    },
  },
})
