/**
 * Pinia store for appointment management
 * Implements state management following best practices
 */
import { defineStore } from 'pinia'
import { appointmentService } from '../services/api'
import type { Appointment } from '../types/fhir'

interface AppointmentState {
  appointments: Appointment[]
  currentAppointment: Appointment | null
  loading: boolean
  error: string | null
}

export const useAppointmentStore = defineStore('appointment', {
  state: (): AppointmentState => ({
    appointments: [],
    currentAppointment: null,
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get all appointments sorted by start date (descending)
     */
    sortedAppointments: (state): Appointment[] => {
      if (!Array.isArray(state.appointments)) {
        return []
      }
      return [...state.appointments].sort((a, b) => {
        const dateA = new Date(a.start || 0)
        const dateB = new Date(b.start || 0)
        return dateB.getTime() - dateA.getTime()
      })
    },

    /**
     * Get upcoming appointments (start date in the future)
     */
    upcomingAppointments: (state): Appointment[] => {
      if (!Array.isArray(state.appointments)) {
        return []
      }
      const now = new Date()
      return state.appointments
        .filter(apt => new Date(apt.start || 0) >= now && apt.status !== 'cancelled')
        .sort((a, b) => new Date(a.start || 0).getTime() - new Date(b.start || 0).getTime())
    },

    /**
     * Get past appointments (start date in the past)
     */
    pastAppointments: (state): Appointment[] => {
      if (!Array.isArray(state.appointments)) {
        return []
      }
      const now = new Date()
      return state.appointments
        .filter(apt => new Date(apt.start || 0) < now)
        .sort((a, b) => new Date(b.start || 0).getTime() - new Date(a.start || 0).getTime())
    },

    /**
     * Get today's appointments
     */
    todayAppointments: (state): Appointment[] => {
      // Ensure appointments is an array
      if (!Array.isArray(state.appointments)) {
        return []
      }

      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)

      return state.appointments
        .filter(apt => {
          const aptDate = new Date(apt.start || 0)
          return aptDate >= today && aptDate < tomorrow && apt.status !== 'cancelled'
        })
        .sort((a, b) => new Date(a.start || 0).getTime() - new Date(b.start || 0).getTime())
    },

    /**
     * Get appointment by ID
     */
    getAppointmentById: (state) => {
      return (id: string): Appointment | undefined => {
        if (!Array.isArray(state.appointments)) {
          return undefined
        }
        return state.appointments.find((a) => a.id === id)
      }
    },

    /**
     * Get appointments by patient ID
     */
    getAppointmentsByPatient: (state) => {
      return (patientId: string): Appointment[] => {
        if (!Array.isArray(state.appointments)) {
          return []
        }
        return state.appointments.filter(apt => {
          return apt.participant?.some(p =>
            p.actor?.reference === `Patient/${patientId}`
          )
        })
      }
    },

    /**
     * Check if appointments are loaded
     */
    hasAppointments: (state): boolean => {
      return Array.isArray(state.appointments) && state.appointments.length > 0
    },
  },

  actions: {
    /**
     * Fetch all appointments from API
     */
    async fetchAppointments(): Promise<void> {
      this.loading = true
      this.error = null

      try {
        this.appointments = await appointmentService.getAllAppointments()
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch appointments'
        console.error('Error fetching appointments:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single appointment by ID
     */
    async fetchAppointmentById(id: string): Promise<Appointment> {
      this.loading = true
      this.error = null

      try {
        this.currentAppointment = await appointmentService.getAppointmentById(id)
        return this.currentAppointment
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch appointment'
        console.error(`Error fetching appointment ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch appointments for a specific patient
     */
    async fetchAppointmentsByPatient(patientId: string): Promise<Appointment[]> {
      this.loading = true
      this.error = null

      try {
        const appointments = await appointmentService.getAppointmentsByPatient(patientId)

        // Merge with existing appointments, avoiding duplicates
        const existingIds = new Set(this.appointments.map(a => a.id))
        const newAppointments = appointments.filter(a => !existingIds.has(a.id))
        this.appointments.push(...newAppointments)

        return appointments
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch patient appointments'
        console.error(`Error fetching appointments for patient ${patientId}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new appointment
     */
    async createAppointment(appointmentData: Appointment): Promise<Appointment> {
      this.loading = true
      this.error = null

      try {
        const newAppointment = await appointmentService.createAppointment(appointmentData)
        this.appointments.push(newAppointment)
        return newAppointment
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to create appointment'
        console.error('Error creating appointment:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing appointment
     */
    async updateAppointment(id: string, appointmentData: Appointment): Promise<Appointment> {
      this.loading = true
      this.error = null

      try {
        const updatedAppointment = await appointmentService.updateAppointment(id, appointmentData)

        // Update in local state
        const index = this.appointments.findIndex((a) => a.id === id)
        if (index !== -1) {
          this.appointments[index] = updatedAppointment
        }

        if (this.currentAppointment?.id === id) {
          this.currentAppointment = updatedAppointment
        }

        return updatedAppointment
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to update appointment'
        console.error(`Error updating appointment ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete an appointment
     */
    async deleteAppointment(id: string): Promise<void> {
      this.loading = true
      this.error = null

      try {
        await appointmentService.deleteAppointment(id)

        // Remove from local state
        this.appointments = this.appointments.filter((a) => a.id !== id)

        if (this.currentAppointment?.id === id) {
          this.currentAppointment = null
        }
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to delete appointment'
        console.error(`Error deleting appointment ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Cancel an appointment
     */
    async cancelAppointment(id: string): Promise<Appointment> {
      this.loading = true
      this.error = null

      try {
        const updatedAppointment = await appointmentService.cancelAppointment(id)

        // Update in local state
        const index = this.appointments.findIndex((a) => a.id === id)
        if (index !== -1) {
          this.appointments[index] = updatedAppointment
        }

        if (this.currentAppointment?.id === id) {
          this.currentAppointment = updatedAppointment
        }

        return updatedAppointment
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to cancel appointment'
        console.error(`Error cancelling appointment ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Check-in an appointment
     */
    async checkInAppointment(id: string): Promise<Appointment> {
      this.loading = true
      this.error = null

      try {
        const updatedAppointment = await appointmentService.checkInAppointment(id)

        // Update in local state
        const index = this.appointments.findIndex((a) => a.id === id)
        if (index !== -1) {
          this.appointments[index] = updatedAppointment
        }

        if (this.currentAppointment?.id === id) {
          this.currentAppointment = updatedAppointment
        }

        return updatedAppointment
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to check-in appointment'
        console.error(`Error checking in appointment ${id}:`, error)
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
     * Clear current appointment
     */
    clearCurrentAppointment(): void {
      this.currentAppointment = null
    },
  },
})
