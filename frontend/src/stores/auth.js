/**
 * Authentication Store
 *
 * Manages user authentication state, JWT tokens, and auth-related operations.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// Use relative URL for auth endpoints (proxied through nginx)
const API_URL = '/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const refreshToken = ref(localStorage.getItem('refreshToken') || null)
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userName = computed(() => user.value ? `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username : '')

  // Actions

  /**
   * Register a new user account
   */
  const register = async (userData) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post(`${API_URL}/register/`, userData)

      // Store tokens
      accessToken.value = response.data.tokens.access
      refreshToken.value = response.data.tokens.refresh
      localStorage.setItem('accessToken', response.data.tokens.access)
      localStorage.setItem('refreshToken', response.data.tokens.refresh)

      // Store user data
      user.value = response.data.user

      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`

      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Login with username and password
   */
  const login = async (credentials) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post(`${API_URL}/login/`, credentials)

      // Store tokens
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      localStorage.setItem('accessToken', response.data.access)
      localStorage.setItem('refreshToken', response.data.refresh)

      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`

      // Fetch user profile
      await fetchProfile()

      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout and clear authentication state
   */
  const logout = async () => {
    loading.value = true
    error.value = null

    try {
      // Try to blacklist the token on the server
      if (refreshToken.value) {
        await axios.post(`${API_URL}/logout/`, {
          refresh: refreshToken.value
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
      // Continue with local logout even if server request fails
    } finally {
      // Clear local state
      accessToken.value = null
      refreshToken.value = null
      user.value = null

      // Clear localStorage
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')

      // Remove authorization header
      delete axios.defaults.headers.common['Authorization']

      loading.value = false
    }
  }

  /**
   * Fetch current user profile
   */
  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/profile/`)
      user.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      // If profile fetch fails, logout
      await logout()
      throw err
    }
  }

  /**
   * Refresh the access token
   */
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await axios.post(`${API_URL}/token/refresh/`, {
        refresh: refreshToken.value
      })

      accessToken.value = response.data.access
      localStorage.setItem('accessToken', response.data.access)
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`

      return response.data.access
    } catch (err) {
      // If refresh fails, logout
      await logout()
      throw err
    }
  }

  /**
   * Change user password
   */
  const changePassword = async (passwordData) => {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post(`${API_URL}/change-password/`, passwordData)
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Password change failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Initialize auth state from localStorage
   */
  const initialize = async () => {
    if (accessToken.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`

      try {
        await fetchProfile()
      } catch (err) {
        console.error('Failed to initialize auth:', err)
        // Clear invalid tokens
        await logout()
      }
    }
  }

  /**
   * Clear error message
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,

    // Computed
    isAuthenticated,
    userName,

    // Actions
    register,
    login,
    logout,
    fetchProfile,
    refreshAccessToken,
    changePassword,
    initialize,
    clearError
  }
})
