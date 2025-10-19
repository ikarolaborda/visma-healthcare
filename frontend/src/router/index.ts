/**
 * Vue Router configuration with authentication guards
 */
import { createRouter, createWebHistory, type RouteRecordRaw, type NavigationGuardNext, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Dashboard from '../views/Dashboard.vue'
import PatientList from '../views/PatientList.vue'
import PatientForm from '../views/PatientForm.vue'
import PatientDetail from '../views/PatientDetail.vue'
import AppointmentList from '../views/AppointmentList.vue'
import AppointmentForm from '../views/AppointmentForm.vue'
import AppointmentDetail from '../views/AppointmentDetail.vue'
import PractitionerList from '../views/PractitionerList.vue'
import PractitionerForm from '../views/PractitionerForm.vue'
import PractitionerDetail from '../views/PractitionerDetail.vue'
import PrescriptionList from '../views/PrescriptionList.vue'
import PrescriptionForm from '../views/prescriptions/PrescriptionForm.vue'
import PrescriptionDetail from '../views/prescriptions/PrescriptionDetail.vue'
import InvoiceList from '../views/InvoiceList.vue'
import InvoiceForm from '../views/billing/InvoiceForm.vue'
import InvoiceDetail from '../views/billing/InvoiceDetail.vue'
import ClinicalRecordList from '../views/ClinicalRecordList.vue'
import ClinicalRecordForm from '../views/patient-history/ClinicalRecordForm.vue'
import ClinicalRecordDetail from '../views/patient-history/ClinicalRecordDetail.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    requiresGuest?: boolean
  }
}

const routes: RouteRecordRaw[] = [
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

  // Dashboard (default home)
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard',
      requiresAuth: true
    },
  },

  // Patient management routes (require authentication)
  {
    path: '/patients',
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

  // Appointment management routes (require authentication)
  {
    path: '/appointments',
    name: 'AppointmentList',
    component: AppointmentList,
    meta: {
      title: 'Appointments',
      requiresAuth: true
    },
  },
  {
    path: '/appointments/add',
    name: 'AddAppointment',
    component: AppointmentForm,
    meta: {
      title: 'Schedule Appointment',
      requiresAuth: true
    },
  },
  {
    path: '/appointments/:id',
    name: 'AppointmentDetail',
    component: AppointmentDetail,
    meta: {
      title: 'Appointment Details',
      requiresAuth: true
    },
  },
  {
    path: '/appointments/:id/edit',
    name: 'EditAppointment',
    component: AppointmentForm,
    meta: {
      title: 'Edit Appointment',
      requiresAuth: true
    },
  },

  // Practitioner management routes (require authentication)
  {
    path: '/practitioners',
    name: 'PractitionerList',
    component: PractitionerList,
    meta: {
      title: 'Practitioners',
      requiresAuth: true
    },
  },
  {
    path: '/practitioners/add',
    name: 'AddPractitioner',
    component: PractitionerForm,
    meta: {
      title: 'Add Practitioner',
      requiresAuth: true
    },
  },
  {
    path: '/practitioners/:id',
    name: 'PractitionerDetail',
    component: PractitionerDetail,
    meta: {
      title: 'Practitioner Details',
      requiresAuth: true
    },
  },
  {
    path: '/practitioners/:id/edit',
    name: 'EditPractitioner',
    component: PractitionerForm,
    meta: {
      title: 'Edit Practitioner',
      requiresAuth: true
    },
  },

  // Prescription management routes
  {
    path: '/prescriptions',
    name: 'PrescriptionList',
    component: PrescriptionList,
    meta: {
      title: 'Prescriptions',
      requiresAuth: true
    },
  },
  {
    path: '/prescriptions/add',
    name: 'AddPrescription',
    component: PrescriptionForm,
    meta: {
      title: 'Add Prescription',
      requiresAuth: true
    },
  },
  {
    path: '/prescriptions/:id',
    name: 'PrescriptionDetail',
    component: PrescriptionDetail,
    meta: {
      title: 'Prescription Details',
      requiresAuth: true
    },
  },
  {
    path: '/prescriptions/:id/edit',
    name: 'EditPrescription',
    component: PrescriptionForm,
    meta: {
      title: 'Edit Prescription',
      requiresAuth: true
    },
  },

  // Billing management routes
  {
    path: '/billing',
    name: 'InvoiceList',
    component: InvoiceList,
    meta: {
      title: 'Billing & Invoices',
      requiresAuth: true
    },
  },
  {
    path: '/billing/add',
    name: 'AddInvoice',
    component: InvoiceForm,
    meta: {
      title: 'Create Invoice',
      requiresAuth: true
    },
  },
  {
    path: '/billing/:id',
    name: 'InvoiceDetail',
    component: InvoiceDetail,
    meta: {
      title: 'Invoice Details',
      requiresAuth: true
    },
  },
  {
    path: '/billing/:id/edit',
    name: 'EditInvoice',
    component: InvoiceForm,
    meta: {
      title: 'Edit Invoice',
      requiresAuth: true
    },
  },

  // Patient History/Clinical Records routes
  {
    path: '/patient-history',
    name: 'ClinicalRecordList',
    component: ClinicalRecordList,
    meta: {
      title: 'Patient History',
      requiresAuth: true
    },
  },
  {
    path: '/patient-history/add',
    name: 'AddClinicalRecord',
    component: ClinicalRecordForm,
    meta: {
      title: 'Add Clinical Record',
      requiresAuth: true
    },
  },
  {
    path: '/patient-history/:id',
    name: 'ClinicalRecordDetail',
    component: ClinicalRecordDetail,
    meta: {
      title: 'Clinical Record Details',
      requiresAuth: true
    },
  },
  {
    path: '/patient-history/:id/edit',
    name: 'EditClinicalRecord',
    component: ClinicalRecordForm,
    meta: {
      title: 'Edit Clinical Record',
      requiresAuth: true
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards for authentication
router.beforeEach(async (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
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
      next({ name: 'Dashboard' })
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
