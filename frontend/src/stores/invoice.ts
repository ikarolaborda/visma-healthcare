/**
 * Invoice Store
 * Manages billing/invoice state using Pinia
 */
import { defineStore } from 'pinia'
import { invoiceService } from '../services/api'
import type { Invoice } from '../types/fhir'

interface InvoiceState {
  invoices: Invoice[]
  currentInvoice: Invoice | null
  loading: boolean
  error: string | null
}

export const useInvoiceStore = defineStore('invoice', {
  state: (): InvoiceState => ({
    invoices: [],
    currentInvoice: null,
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Get invoices sorted by date (most recent first)
     */
    sortedInvoices: (state): Invoice[] => {
      return [...state.invoices].sort((a, b) => {
        const dateA = new Date(a.date || a.meta?.lastUpdated || 0).getTime()
        const dateB = new Date(b.date || b.meta?.lastUpdated || 0).getTime()
        return dateB - dateA
      })
    },

    /**
     * Get invoice by ID
     */
    getInvoiceById: (state) => {
      return (id: string): Invoice | undefined =>
        state.invoices.find(i => i.id === id)
    },

    /**
     * Get invoices by patient ID
     */
    getInvoicesByPatient: (state) => {
      return (patientId: string): Invoice[] =>
        state.invoices.filter(i => i.subject?.reference === `Patient/${patientId}`)
    },

    /**
     * Get invoices by status
     */
    getInvoicesByStatus: (state) => {
      return (status: Invoice['status']): Invoice[] =>
        state.invoices.filter(i => i.status === status)
    },

    /**
     * Get pending invoices (issued but not balanced)
     */
    pendingInvoices: (state): Invoice[] => {
      return state.invoices.filter(i => i.status === 'issued')
    },

    /**
     * Get paid invoices (balanced)
     */
    paidInvoices: (state): Invoice[] => {
      return state.invoices.filter(i => i.status === 'balanced')
    },

    /**
     * Calculate total revenue from paid invoices
     */
    totalRevenue: (state): number => {
      return state.invoices
        .filter(i => i.status === 'balanced')
        .reduce((sum, i) => sum + (i.totalGross?.value || 0), 0)
    },

    /**
     * Check if invoices are loaded
     */
    hasInvoices: (state): boolean => state.invoices.length > 0
  },

  actions: {
    /**
     * Fetch all invoices
     */
    async fetchInvoices(): Promise<void> {
      this.loading = true
      this.error = null
      try {
        this.invoices = await invoiceService.getAllInvoices()
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch invoices'
        console.error('Error fetching invoices:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch a single invoice by ID
     */
    async fetchInvoiceById(id: string): Promise<Invoice> {
      this.loading = true
      this.error = null
      try {
        const invoice = await invoiceService.getInvoiceById(id)
        this.currentInvoice = invoice

        // Update in invoices array if it exists
        const index = this.invoices.findIndex(i => i.id === id)
        if (index !== -1) {
          this.invoices[index] = invoice
        } else {
          this.invoices.push(invoice)
        }

        return invoice
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to fetch invoice'
        console.error(`Error fetching invoice ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Create a new invoice
     */
    async createInvoice(data: Invoice): Promise<Invoice> {
      this.loading = true
      this.error = null
      try {
        const invoice = await invoiceService.createInvoice(data)
        this.invoices.push(invoice)
        return invoice
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to create invoice'
        console.error('Error creating invoice:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update an existing invoice
     */
    async updateInvoice(id: string, data: Invoice): Promise<Invoice> {
      this.loading = true
      this.error = null
      try {
        const invoice = await invoiceService.updateInvoice(id, data)

        // Update in invoices array
        const index = this.invoices.findIndex(i => i.id === id)
        if (index !== -1) {
          this.invoices[index] = invoice
        }

        // Update current invoice if it's the same one
        if (this.currentInvoice?.id === id) {
          this.currentInvoice = invoice
        }

        return invoice
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update invoice'
        console.error(`Error updating invoice ${id}:`, error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete an invoice
     */
    async deleteInvoice(id: string): Promise<void> {
      this.loading = true
      this.error = null
      try {
        await invoiceService.deleteInvoice(id)

        // Remove from invoices array
        this.invoices = this.invoices.filter(i => i.id !== id)

        // Clear current invoice if it's the same one
        if (this.currentInvoice?.id === id) {
          this.currentInvoice = null
        }
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to delete invoice'
        console.error(`Error deleting invoice ${id}:`, error)
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
     * Clear current invoice
     */
    clearCurrentInvoice(): void {
      this.currentInvoice = null
    }
  }
})
