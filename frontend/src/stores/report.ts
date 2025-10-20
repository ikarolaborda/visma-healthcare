import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export interface Report {
  id: string
  user: number
  report_type: string
  format: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  filters: Record<string, any>
  file: string | null
  file_size: number | null
  title: string
  description: string
  record_count: number | null
  created_at: string
  updated_at: string
  completed_at: string | null
  error_message: string | null
}

export interface ReportCreateData {
  report_type: string
  format: string
  title: string
  description?: string
  filters?: Record<string, any>
}

export const useReportStore = defineStore('report', () => {
  const reports = ref<Report[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchReports = async (filters?: Record<string, any>) => {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, String(value))
        })
      }

      const url = `/api/reports/${params.toString() ? '?' + params.toString() : ''}`
      const response = await api.get(url)

      // Handle paginated response from DRF
      if (response.data && response.data.results) {
        reports.value = Array.isArray(response.data.results) ? response.data.results : []
      } else {
        reports.value = Array.isArray(response.data) ? response.data : []
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch reports'
      throw err
    } finally {
      loading.value = false
    }
  }

  const generateReport = async (data: ReportCreateData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/api/reports/', data)
      reports.value.unshift(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to generate report'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getReport = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/api/reports/${id}/`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch report'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteReport = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/api/reports/${id}/`)
      reports.value = reports.value.filter(r => r.id !== id)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete report'
      throw err
    } finally {
      loading.value = false
    }
  }

  const downloadReport = async (id: string) => {
    try {
      const response = await api.get(`/api/reports/${id}/download/`, {
        responseType: 'blob'
      })
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to download report'
      throw err
    }
  }

  return {
    reports,
    loading,
    error,
    fetchReports,
    generateReport,
    getReport,
    deleteReport,
    downloadReport
  }
})
