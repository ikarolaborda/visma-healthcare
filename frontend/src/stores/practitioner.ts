/**
 * Practitioner Store
 * Manages practitioner state using Pinia
 */
import { defineStore } from 'pinia'
import { practitionerService } from '../services/api'
import type { Practitioner } from '../types/fhir'

interface PractitionerState {
  practitioners: Practitioner[]
  currentPractitioner: Practitioner | null
  loading: boolean
  error: string | null
}

console.log('[PractitionerStore] Store definition loading')

export const usePractitionerStore = defineStore('practitioner', {
  state: (): PractitionerState => ({
    practitioners: [],
    currentPractitioner: null,
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Get practitioners sorted by name
     */
    sortedPractitioners: (state): Practitioner[] => {
      if (!Array.isArray(state.practitioners)) {
        return []
      }
      return [...state.practitioners].sort((a, b) => {
        const nameA = `${a.name?.[0]?.given?.[0] || ''} ${a.name?.[0]?.family || ''}`.toLowerCase()
        const nameB = `${b.name?.[0]?.given?.[0] || ''} ${b.name?.[0]?.family || ''}`.toLowerCase()
        return nameA.localeCompare(nameB)
      })
    },

    /**
     * Get only active practitioners
     */
    activePractitioners: (state): Practitioner[] => {
      if (!Array.isArray(state.practitioners)) {
        return []
      }
      return state.practitioners.filter(p => p.active)
    },

    /**
     * Get practitioners by specialization
     */
    getPractitionersBySpecialization: (state) => {
      return (specialization: string): Practitioner[] => {
        if (!Array.isArray(state.practitioners)) {
          return []
        }
        return state.practitioners.filter(
          p => p.specialization?.toLowerCase().includes(specialization.toLowerCase())
        )
      }
    },

    /**
     * Get practitioner by ID
     */
    getPractitionerById: (state) => {
      return (id: string): Practitioner | undefined => {
        if (!Array.isArray(state.practitioners)) {
          return undefined
        }
        return state.practitioners.find(p => p.id === id)
      }
    },

    /**
     * Get practitioners grouped by specialization
     */
    practitionersBySpecialization: (state): Record<string, Practitioner[]> => {
      const grouped: Record<string, Practitioner[]> = {}
      state.practitioners.forEach(p => {
        const spec = p.specialization || 'Other'
        if (!grouped[spec]) {
          grouped[spec] = []
        }
        grouped[spec].push(p)
      })
      return grouped
    }
  },

  actions: {
    /**
     * Fetch all practitioners
     */
    async fetchPractitioners(): Promise<void> {
      console.log('[PractitionerStore] fetchPractitioners called')
      this.loading = true
      this.error = null
      try {
        const practitioners = await practitionerService.getAllPractitioners()
        console.log('[PractitionerStore] Fetched practitioners:', practitioners.length, 'practitioners')
        console.log('[PractitionerStore] First practitioner:', practitioners[0])
        this.practitioners = practitioners
        console.log('[PractitionerStore] Store updated, practitioners.length:', this.practitioners.length)
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch practitioners'
        console.error('[PractitionerStore] Error fetching practitioners:', error)
        throw error
      } finally {
        this.loading = false
        console.log('[PractitionerStore] fetchPractitioners complete, loading:', this.loading)
      }
    },

    /**
     * Fetch a single practitioner by ID
     */
    async fetchPractitionerById(id: string): Promise<Practitioner> {
      this.loading = true
      this.error = null
      try {
        const practitioner = await practitionerService.getPractitionerById(id)
        this.currentPractitioner = practitioner

        // Update in practitioners array if it exists
        const index = this.practitioners.findIndex(p => p.id === id)
        if (index !== -1) {
          this.practitioners[index] = practitioner
        } else {
          this.practitioners.push(practitioner)
        }

        return practitioner
      } catch (error: any) {
        this.error = error.response?.data?.detail || `Failed to fetch practitioner ${id}`
        console.error(`Error fetching practitioner ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new practitioner
     */
    async createPractitioner(practitionerData: Practitioner): Promise<Practitioner> {
      this.loading = true
      this.error = null
      try {
        const newPractitioner = await practitionerService.createPractitioner(practitionerData)
        this.practitioners.push(newPractitioner)
        return newPractitioner
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to create practitioner'
        console.error('Error creating practitioner:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing practitioner
     */
    async updatePractitioner(id: string, practitionerData: Practitioner): Promise<Practitioner> {
      this.loading = true
      this.error = null
      try {
        const updatedPractitioner = await practitionerService.updatePractitioner(id, practitionerData)

        // Update in practitioners array
        const index = this.practitioners.findIndex(p => p.id === id)
        if (index !== -1) {
          this.practitioners[index] = updatedPractitioner
        }

        // Update current practitioner if it's the same one
        if (this.currentPractitioner?.id === id) {
          this.currentPractitioner = updatedPractitioner
        }

        return updatedPractitioner
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update practitioner'
        console.error('Error updating practitioner:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete a practitioner
     */
    async deletePractitioner(id: string): Promise<void> {
      this.loading = true
      this.error = null
      try {
        await practitionerService.deletePractitioner(id)

        // Remove from practitioners array
        this.practitioners = this.practitioners.filter(p => p.id !== id)

        // Clear current practitioner if it's the same one
        if (this.currentPractitioner?.id === id) {
          this.currentPractitioner = null
        }
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to delete practitioner'
        console.error('Error deleting practitioner:', error)
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
     * Clear current practitioner
     */
    clearCurrentPractitioner(): void {
      this.currentPractitioner = null
    }
  }
})
