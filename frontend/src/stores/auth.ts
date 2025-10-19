/**
 * Authentication Store
 *
 * Manages user authentication state, JWT tokens, and auth-related operations.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import apiClient from '../services/api'
import type { User, AuthTokens, LoginCredentials, RegisterData } from '../types'

// Use relative URL for auth endpoints (proxied through nginx)
const API_URL = '/api/auth'

interface AuthStore {
  // State
  user: Ref<User | null>
  accessToken: Ref<string | null>
  refreshToken: Ref<string | null>
  loading: Ref<boolean>
  error: Ref<any>

  // Computed
  isAuthenticated: ComputedRef<boolean>
  userName: ComputedRef<string>

  // Actions
  register: (userData: RegisterData) => Promise<any>
  login: (credentials: LoginCredentials) => Promise<AuthTokens>
  logout: () => Promise<void>
  fetchProfile: () => Promise<User>
  refreshAccessToken: () => Promise<string>
  changePassword: (passwordData: { old_password: string; new_password: string }) => Promise<any>
  initialize: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = defineStore('auth', (): AuthStore => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('accessToken') || null)
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken') || null)
  const loading = ref<boolean>(false)
  const error = ref<any>(null)

  // Computed
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userName = computed(() =>
    user.value
      ? `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
      : ''
  )

  // Actions

  /**
   * Register a new user account
   */
  const register = async (userData: RegisterData): Promise<any> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post(`${API_URL}/register/`, userData)

      // Store tokens
      accessToken.value = response.data.tokens.access
      refreshToken.value = response.data.tokens.refresh
      localStorage.setItem('accessToken', response.data.tokens.access)
      localStorage.setItem('refreshToken', response.data.tokens.refresh)

      // Store user data
      user.value = response.data.user

      return response.data
    } catch (err: any) {
      error.value = err.response?.data || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Login with username and password
   */
  const login = async (credentials: LoginCredentials): Promise<AuthTokens> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post<AuthTokens>(`${API_URL}/login/`, credentials)

      // Store tokens
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      localStorage.setItem('accessToken', response.data.access)
      localStorage.setItem('refreshToken', response.data.refresh)

      // Fetch user profile
      await fetchProfile()

      return response.data
    } catch (err: any) {
      error.value = err.response?.data || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout and clear authentication state
   */
  const logout = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      // Try to blacklist the token on the server
      if (refreshToken.value) {
        await apiClient.post(`${API_URL}/logout/`, {
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

      loading.value = false
    }
  }

  /**
   * Fetch current user profile
   */
  const fetchProfile = async (): Promise<User> => {
    try {
      const response = await apiClient.get<User>(`${API_URL}/profile/`)
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
  const refreshAccessToken = async (): Promise<string> => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await apiClient.post<{ access: string }>(`${API_URL}/token/refresh/`, {
        refresh: refreshToken.value
      })

      accessToken.value = response.data.access
      localStorage.setItem('accessToken', response.data.access)

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
  const changePassword = async (passwordData: { old_password: string; new_password: string }): Promise<any> => {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.post(`${API_URL}/change-password/`, passwordData)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data || 'Password change failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Initialize auth state from localStorage
   */
  const initialize = async (): Promise<void> => {
    if (accessToken.value) {
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
  const clearError = (): void => {
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
