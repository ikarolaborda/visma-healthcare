<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900">
        User Profile
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        View and manage your account information
      </p>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="glass rounded-2xl shadow-lg p-12 text-center"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto" />
      <p class="text-gray-500 mt-4">
        Loading profile...
      </p>
    </div>

    <!-- Profile Information -->
    <div
      v-else-if="user"
      class="space-y-6"
    >
      <!-- Personal Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            Personal Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Username</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <svg
                class="h-5 w-5 text-gray-400 mr-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <span class="text-gray-900 font-medium">{{ user.username }}</span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Email Address</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <svg
                class="h-5 w-5 text-gray-400 mr-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <span class="text-gray-900">{{ user.email || 'Not provided' }}</span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">First Name</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <span class="text-gray-900">{{ user.first_name || 'Not provided' }}</span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Last Name</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <span class="text-gray-900">{{ user.last_name || 'Not provided' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Account Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Account Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Account Status</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  user.is_active ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'
                ]"
              >
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Staff Status</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  user.is_staff ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                ]"
              >
                {{ user.is_staff ? 'Staff Member' : 'Regular User' }}
              </span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Account Created</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <svg
                class="h-5 w-5 text-gray-400 mr-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span class="text-gray-900">{{ formatDate(user.date_joined) }}</span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-500 mb-1">Last Login</label>
            <div class="flex items-center px-4 py-3 bg-gray-50 rounded-xl border border-gray-200">
              <svg
                class="h-5 w-5 text-gray-400 mr-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span class="text-gray-900">{{ formatDate(user.last_login) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg
              class="h-5 w-5 mr-2 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
            Quick Actions
          </h3>
        </div>

        <div class="flex flex-wrap gap-4">
          <router-link
            to="/settings"
            class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
          >
            <svg
              class="h-5 w-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            Change Password
          </router-link>

          <router-link
            to="/"
            class="inline-flex items-center px-6 py-3 bg-white text-gray-700 font-medium rounded-xl border border-gray-300 shadow-sm hover:bg-gray-50 transition-all duration-200"
          >
            <svg
              class="h-5 w-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
            Back to Dashboard
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { user, loading } = storeToRefs(authStore)

onMounted(async () => {
  if (!user.value) {
    await authStore.fetchProfile()
  }
})

const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return 'Never'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
