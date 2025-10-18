/**
 * Vue Router configuration with authentication guards
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import PatientList from '../views/PatientList.vue'
import PatientForm from '../views/PatientForm.vue'
import PatientDetail from '../views/PatientDetail.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

const routes = [
  // Authentication routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: 'Login',
      requiresGuest: true // Only accessible when not authenticated
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: 'Register',
      requiresGuest: true
    },
  },

  // Patient management routes (require authentication)
  {
    path: '/',
    name: 'PatientList',
    component: PatientList,
    meta: {
      title: 'Patients',
      requiresAuth: true
    },
  },
  {
    path: '/add',
    name: 'AddPatient',
    component: PatientForm,
    meta: {
      title: 'Add Patient',
      requiresAuth: true
    },
  },
  {
    path: '/patient/:id',
    name: 'PatientDetail',
    component: PatientDetail,
    meta: {
      title: 'Patient Details',
      requiresAuth: true
    },
  },
  {
    path: '/patient/:id/edit',
    name: 'EditPatient',
    component: PatientForm,
    meta: {
      title: 'Edit Patient',
      requiresAuth: true
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards for authentication
router.beforeEach(async (to, from, next) => {
  // Update page title
  document.title = `${to.meta.title || 'Healthcare'} - Patient Management`

  const authStore = useAuthStore()

  // Initialize auth store on first navigation if token exists
  if (authStore.accessToken && !authStore.user) {
    try {
      await authStore.initialize()
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      // Clear invalid tokens - initialization handles this
    }
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const isAuthenticated = authStore.isAuthenticated

  // Allow login/register pages explicitly to avoid redirect loops
  if (to.name === 'Login' || to.name === 'Register') {
    if (isAuthenticated) {
      // Only redirect authenticated users away from login/register
      next({ name: 'PatientList' })
    } else {
      // Allow access to login/register for non-authenticated users
      next()
    }
  } else if (requiresAuth && !isAuthenticated) {
    // Redirect to login if route requires authentication
    next({
      name: 'Login',
      query: { redirect: to.fullPath } // Save intended destination
    })
  } else {
    next()
  }
})

export default router
