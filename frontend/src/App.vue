<template>
  <div class="min-h-screen flex flex-col">
    <!-- Modern Navigation -->
    <nav class="glass-dark sticky top-0 z-50 shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo and Brand -->
          <div class="flex items-center space-x-3 animate-fade-in">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-lg">
                <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <div class="flex flex-col">
              <span class="text-xl font-bold text-white">HealthCare</span>
              <span class="text-xs text-gray-300">Patient Management</span>
            </div>
          </div>

          <!-- Navigation Links -->
          <div class="hidden md:block">
            <div class="flex items-center space-x-2">
              <template v-if="isAuthenticated">
                <router-link
                  to="/"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path === '/'
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    <span>{{ $t('dashboard.dashboard') }}</span>
                  </span>
                </router-link>

                <router-link
                  to="/patients"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path.startsWith('/patient')
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span>{{ $t('nav.patients') }}</span>
                  </span>
                </router-link>

                <router-link
                  to="/appointments"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path.startsWith('/appointment')
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>{{ $t('nav.appointments') }}</span>
                  </span>
                </router-link>

                <router-link
                  to="/practitioners"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path.startsWith('/practitioner')
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{{ $t('nav.practitioners') }}</span>
                  </span>
                </router-link>

                <router-link
                  to="/prescriptions"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path.startsWith('/prescription')
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Prescriptions</span>
                  </span>
                </router-link>

                <router-link
                  to="/billing"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path.startsWith('/billing')
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span>Billing</span>
                  </span>
                </router-link>

                <router-link
                  to="/patient-history"
                  class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  :class="$route.path.startsWith('/patient-history')
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'"
                >
                  <span class="flex items-center space-x-2">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                    <span>History</span>
                  </span>
                </router-link>

                <!-- User Menu -->
                <div class="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-600">
                  <span class="text-sm text-gray-300">{{ userName }}</span>
                  <button
                    @click="handleLogout"
                    class="px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-all duration-200"
                  >
                    <span class="flex items-center space-x-2">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      <span>Logout</span>
                    </span>
                  </button>
                </div>
              </template>
              <template v-else>
                <router-link
                  to="/login"
                  class="px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-all duration-200"
                >
                  Login
                </router-link>
                <router-link
                  to="/register"
                  class="px-4 py-2 rounded-lg text-sm font-medium bg-primary-600 text-white shadow-lg hover:bg-primary-700 transition-all duration-200"
                >
                  Register
                </router-link>
              </template>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <div class="md:hidden">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="p-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  v-if="!mobileMenuOpen"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path
                  v-else
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div v-if="mobileMenuOpen" class="md:hidden bg-gray-900/50 backdrop-blur-md border-t border-gray-700">
        <div class="px-2 pt-2 pb-3 space-y-1">
          <template v-if="isAuthenticated">
            <div class="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              {{ userName }}
            </div>
            <router-link to="/" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path === '/' ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              {{ $t('dashboard.dashboard') }}
            </router-link>
            <router-link to="/patients" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path.startsWith('/patient') ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              {{ $t('nav.patients') }}
            </router-link>
            <router-link to="/appointments" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path.startsWith('/appointment') ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              {{ $t('nav.appointments') }}
            </router-link>
            <router-link to="/practitioners" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path.startsWith('/practitioner') ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              {{ $t('nav.practitioners') }}
            </router-link>
            <router-link to="/prescriptions" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path.startsWith('/prescription') ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              Prescriptions
            </router-link>
            <router-link to="/billing" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path.startsWith('/billing') ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              Billing
            </router-link>
            <router-link to="/patient-history" @click="mobileMenuOpen = false" class="block px-3 py-2 rounded-lg text-base font-medium transition-all" :class="$route.path.startsWith('/patient-history') ? 'bg-primary-600 text-white' : 'text-gray-300 hover:bg-white/10'">
              Patient History
            </router-link>

            <button
              @click="handleLogout(); mobileMenuOpen = false"
              class="w-full text-left px-3 py-2 rounded-lg text-base font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-all duration-200"
            >
              <span class="flex items-center space-x-2">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>Logout</span>
              </span>
            </button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              @click="mobileMenuOpen = false"
              class="block px-3 py-2 rounded-lg text-base font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-all duration-200"
            >
              Login
            </router-link>
            <router-link
              to="/register"
              @click="mobileMenuOpen = false"
              class="block px-3 py-2 rounded-lg text-base font-medium bg-primary-600 text-white hover:bg-primary-700 transition-all duration-200"
            >
              Register
            </router-link>
          </template>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Modern Footer -->
    <footer class="glass-dark mt-auto border-t border-gray-700/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <div class="flex items-center space-x-2 text-gray-300 text-sm">
            <svg class="h-5 w-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>FHIR R4 Compliant Healthcare System</span>
          </div>
          <div class="text-gray-400 text-sm">
            &copy; {{ new Date().getFullYear() }} Healthcare Patient Management. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userName = computed(() => authStore.userName || 'User')

onMounted(async () => {
  // Initialize auth store on app mount only if not already initialized
  if (authStore.accessToken && !authStore.user) {
    try {
      await authStore.initialize()
    } catch (error) {
      console.error('Failed to initialize auth on app mount:', error)
      // Errors are handled in the auth store
    }
  }
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
