<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Account Settings</h1>
      <p class="mt-1 text-sm text-gray-500">Manage your account security and preferences</p>
    </div>

    <!-- Success Alert -->
    <div
      v-if="successMessage"
      class="bg-success-50 border-l-4 border-success-500 rounded-xl p-4 animate-scale-in"
    >
      <div class="flex items-center">
        <svg class="h-5 w-5 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-success-700">{{ successMessage }}</p>
      </div>
    </div>

    <!-- Error Alert -->
    <div
      v-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4 animate-scale-in"
    >
      <div class="flex items-center">
        <svg class="h-5 w-5 text-danger-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-danger-700">{{ error }}</p>
      </div>
    </div>

    <!-- Change Password Section -->
    <div class="glass rounded-2xl shadow-lg p-6">
      <div class="border-b border-gray-200 pb-3 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 flex items-center">
          <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Change Password
        </h3>
        <p class="text-sm text-gray-500 mt-1">
          Update your password to keep your account secure
        </p>
      </div>

      <form @submit.prevent="handleChangePassword" class="space-y-6">
        <div class="space-y-4">
          <!-- Current Password -->
          <div>
            <label for="oldPassword" class="block text-sm font-medium text-gray-700 mb-1">
              Current Password <span class="text-danger-500">*</span>
            </label>
            <div class="relative">
              <input
                id="oldPassword"
                v-model="passwordData.old_password"
                :type="showOldPassword ? 'text' : 'password'"
                required
                class="block w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="Enter your current password"
              />
              <button
                type="button"
                @click="showOldPassword = !showOldPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <svg v-if="!showOldPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>

          <!-- New Password -->
          <div>
            <label for="newPassword" class="block text-sm font-medium text-gray-700 mb-1">
              New Password <span class="text-danger-500">*</span>
            </label>
            <div class="relative">
              <input
                id="newPassword"
                v-model="passwordData.new_password"
                :type="showNewPassword ? 'text' : 'password'"
                required
                minlength="8"
                class="block w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                placeholder="Enter your new password (min 8 characters)"
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <svg v-if="!showNewPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              Password must be at least 8 characters long
            </p>
          </div>

          <!-- Confirm New Password -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password <span class="text-danger-500">*</span>
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                minlength="8"
                class="block w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
                :class="{ 'border-danger-500': confirmPassword && confirmPassword !== passwordData.new_password }"
                placeholder="Confirm your new password"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <svg v-if="!showConfirmPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
            <p v-if="confirmPassword && confirmPassword !== passwordData.new_password" class="mt-1 text-xs text-danger-500">
              Passwords do not match
            </p>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-200">
          <router-link
            to="/profile"
            class="inline-flex items-center px-6 py-3 text-gray-700 font-medium bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-all"
          >
            <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Profile
          </router-link>

          <button
            type="submit"
            :disabled="loading || !isPasswordValid"
            class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ loading ? 'Changing Password...' : 'Change Password' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { loading } = storeToRefs(authStore)

const passwordData = ref({
  old_password: '',
  new_password: ''
})
const confirmPassword = ref('')
const successMessage = ref('')
const error = ref('')

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const isPasswordValid = computed(() => {
  return (
    passwordData.value.old_password.length >= 1 &&
    passwordData.value.new_password.length >= 8 &&
    passwordData.value.new_password === confirmPassword.value
  )
})

const handleChangePassword = async () => {
  error.value = ''
  successMessage.value = ''

  if (!isPasswordValid.value) {
    error.value = 'Please fill in all fields correctly'
    return
  }

  try {
    await authStore.changePassword(passwordData.value)
    successMessage.value = 'Password changed successfully!'

    // Clear form
    passwordData.value = {
      old_password: '',
      new_password: ''
    }
    confirmPassword.value = ''

    // Clear success message after 5 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.response?.data?.old_password?.[0] || 'Failed to change password. Please check your current password.'
  }
}
</script>
