/**
 * Prescription Store
 * Manages prescription/medication request state using Pinia
 */
import { defineStore } from 'pinia'
import { prescriptionService } from '../services/api'
import type { MedicationRequest } from '../types/fhir'

interface PrescriptionState {
  prescriptions: MedicationRequest[]
  currentPrescription: MedicationRequest | null
  loading: boolean
  error: string | null
}

export const usePrescriptionStore = defineStore('prescription', {
  state: (): PrescriptionState => ({
    prescriptions: [],
    currentPrescription: null,
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Get only active prescriptions
     */
    activePrescriptions: (state): MedicationRequest[] =>
      state.prescriptions.filter(p => p.status === 'active'),

    /**
     * Get prescription by ID
     */
    getPrescriptionById: (state) => {
      return (id: string): MedicationRequest | undefined =>
        state.prescriptions.find(p => p.id === id)
    }
  },

  actions: {
    /**
     * Fetch all prescriptions
     */
    async fetchPrescriptions(): Promise<void> {
      this.loading = true
      this.error = null
      try {
        this.prescriptions = await prescriptionService.getAllPrescriptions()
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch prescriptions'
        console.error('Error fetching prescriptions:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single prescription by ID
     */
    async fetchPrescriptionById(id: string): Promise<MedicationRequest> {
      this.loading = true
      this.error = null
      try {
        const prescription = await prescriptionService.getPrescriptionById(id)
        this.currentPrescription = prescription

        // Update in prescriptions array if it exists
        const index = this.prescriptions.findIndex(p => p.id === id)
        if (index !== -1) {
          this.prescriptions[index] = prescription
        } else {
          this.prescriptions.push(prescription)
        }

        return prescription
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch prescription'
        console.error(`Error fetching prescription ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new prescription
     */
    async createPrescription(data: MedicationRequest): Promise<MedicationRequest> {
      this.loading = true
      this.error = null
      try {
        const prescription = await prescriptionService.createPrescription(data)
        this.prescriptions.push(prescription)
        return prescription
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to create prescription'
        console.error('Error creating prescription:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing prescription
     */
    async updatePrescription(id: string, data: MedicationRequest): Promise<MedicationRequest> {
      this.loading = true
      this.error = null
      try {
        const prescription = await prescriptionService.updatePrescription(id, data)

        // Update in prescriptions array
        const index = this.prescriptions.findIndex(p => p.id === id)
        if (index !== -1) {
          this.prescriptions[index] = prescription
        }

        // Update current prescription if it's the same one
        if (this.currentPrescription?.id === id) {
          this.currentPrescription = prescription
        }

        return prescription
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update prescription'
        console.error(`Error updating prescription ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete a prescription
     */
    async deletePrescription(id: string): Promise<void> {
      this.loading = true
      this.error = null
      try {
        await prescriptionService.deletePrescription(id)

        // Remove from prescriptions array
        this.prescriptions = this.prescriptions.filter(p => p.id !== id)

        // Clear current prescription if it's the same one
        if (this.currentPrescription?.id === id) {
          this.currentPrescription = null
        }
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to delete prescription'
        console.error(`Error deleting prescription ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Clear any errors
     */
    clearError(): void {
      this.error = null
    },

    /**
     * Clear current prescription
     */
    clearCurrentPrescription(): void {
      this.currentPrescription = null
    }
  }
})
