/**
 * Practitioner Store
 * Manages practitioner state using Pinia
 */
import { defineStore } from 'pinia'
import { practitionerService } from '../services/api'

export const usePractitionerStore = defineStore('practitioner', {
  state: () => ({
    practitioners: [],
    currentPractitioner: null,
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Get practitioners sorted by name
     */
    sortedPractitioners: (state) => {
      return [...state.practitioners].sort((a, b) => {
        const nameA = `${a.given_name} ${a.family_name}`.toLowerCase()
        const nameB = `${b.given_name} ${b.family_name}`.toLowerCase()
        return nameA.localeCompare(nameB)
      })
    },

    /**
     * Get only active practitioners
     */
    activePractitioners: (state) => {
      return state.practitioners.filter(p => p.active)
    },

    /**
     * Get practitioners by specialization
     */
    getPractitionersBySpecialization: (state) => {
      return (specialization) => {
        return state.practitioners.filter(
          p => p.specialization.toLowerCase().includes(specialization.toLowerCase())
        )
      }
    },

    /**
     * Get practitioner by ID
     */
    getPractitionerById: (state) => {
      return (id) => {
        return state.practitioners.find(p => p.id === id)
      }
    },

    /**
     * Get practitioners grouped by specialization
     */
    practitionersBySpecialization: (state) => {
      const grouped = {}
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
    async fetchPractitioners() {
      this.loading = true
      this.error = null
      try {
        const bundle = await practitionerService.getAllPractitioners()
        // Handle FHIR Bundle format
        this.practitioners = bundle.entry?.map((entry) => entry.resource) || []
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch practitioners'
        console.error('Error fetching practitioners:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single practitioner by ID
     */
    async fetchPractitionerById(id) {
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
      } catch (error) {
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
    async createPractitioner(practitionerData) {
      this.loading = true
      this.error = null
      try {
        const newPractitioner = await practitionerService.createPractitioner(practitionerData)
        this.practitioners.push(newPractitioner)
        return newPractitioner
      } catch (error) {
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
    async updatePractitioner(id, practitionerData) {
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
      } catch (error) {
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
    async deletePractitioner(id) {
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
      } catch (error) {
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
    clearError() {
      this.error = null
    },

    /**
     * Clear current practitioner
     */
    clearCurrentPractitioner() {
      this.currentPractitioner = null
    }
  }
})
