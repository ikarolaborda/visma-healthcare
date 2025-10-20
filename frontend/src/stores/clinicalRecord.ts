/**
 * Clinical Record Store
 * Manages clinical records/observations state using Pinia
 */
import { defineStore } from 'pinia'
import { clinicalRecordService } from '../services/api'
import type { Observation } from '../types/fhir'

interface ClinicalRecordState {
  records: Observation[]
  currentRecord: Observation | null
  loading: boolean
  error: string | null
}

export const useClinicalRecordStore = defineStore('clinicalRecord', {
  state: (): ClinicalRecordState => ({
    records: [],
    currentRecord: null,
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Get records sorted by date (most recent first)
     */
    sortedRecords: (state): Observation[] => {
      return [...state.records].sort((a, b) => {
        const dateA = new Date(a.effectiveDateTime || a.meta?.lastUpdated || 0).getTime()
        const dateB = new Date(b.effectiveDateTime || b.meta?.lastUpdated || 0).getTime()
        return dateB - dateA
      })
    },

    /**
     * Get record by ID
     */
    getRecordById: (state) => {
      return (id: string): Observation | undefined =>
        state.records.find(r => r.id === id)
    },

    /**
     * Get records by patient ID
     */
    getRecordsByPatient: (state) => {
      return (patientId: string): Observation[] =>
        state.records.filter(r => r.subject?.reference === `Patient/${patientId}`)
    },

    /**
     * Check if records are loaded
     */
    hasRecords: (state): boolean => state.records.length > 0
  },

  actions: {
    /**
     * Fetch all clinical records
     */
    async fetchRecords(): Promise<void> {
      this.loading = true
      this.error = null
      try {
        this.records = await clinicalRecordService.getAllRecords()
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch records'
        console.error('Error fetching clinical records:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single record by ID
     */
    async fetchRecordById(id: string): Promise<Observation> {
      this.loading = true
      this.error = null
      try {
        const record = await clinicalRecordService.getRecordById(id)
        this.currentRecord = record

        // Update in records array if it exists
        const index = this.records.findIndex(r => r.id === id)
        if (index !== -1) {
          this.records[index] = record
        } else {
          this.records.push(record)
        }

        return record
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch record'
        console.error(`Error fetching record ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new clinical record
     */
    async createRecord(data: Observation): Promise<Observation> {
      this.loading = true
      this.error = null
      try {
        const record = await clinicalRecordService.createRecord(data)
        this.records.push(record)
        return record
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to create record'
        console.error('Error creating clinical record:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing clinical record
     */
    async updateRecord(id: string, data: Observation): Promise<Observation> {
      this.loading = true
      this.error = null
      try {
        const record = await clinicalRecordService.updateRecord(id, data)

        // Update in records array
        const index = this.records.findIndex(r => r.id === id)
        if (index !== -1) {
          this.records[index] = record
        }

        // Update current record if it's the same one
        if (this.currentRecord?.id === id) {
          this.currentRecord = record
        }

        return record
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update record'
        console.error(`Error updating record ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete a clinical record
     */
    async deleteRecord(id: string): Promise<void> {
      this.loading = true
      this.error = null
      try {
        await clinicalRecordService.deleteRecord(id)

        // Remove from records array
        this.records = this.records.filter(r => r.id !== id)

        // Clear current record if it's the same one
        if (this.currentRecord?.id === id) {
          this.currentRecord = null
        }
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to delete record'
        console.error(`Error deleting record ${id}:`, error)
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
     * Clear current record
     */
    clearCurrentRecord(): void {
      this.currentRecord = null
    }
  }
})
