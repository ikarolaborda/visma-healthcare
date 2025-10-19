/**
 * Application-wide type definitions
 */

// Authentication
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
}

// Form Data interfaces (simplified for forms)
export interface PatientFormData {
  id?: string
  familyName: string
  givenName: string
  middleName?: string
  gender: string
  birthDate: string
  addressLine?: string
  city?: string
  state?: string
  postalCode?: string
  country?: string
  email: string
  phone: string
  active?: boolean
}

export interface PractitionerFormData {
  id?: string
  prefix?: string
  familyName: string
  givenName: string
  middleName?: string
  gender: string
  birthDate?: string
  npi?: string
  licenseNumber?: string
  specialization: string
  qualification: string
  yearsOfExperience?: number
  addressLine?: string
  city?: string
  state?: string
  postalCode?: string
  country?: string
  email: string
  phone: string
  active?: boolean
}

export interface AppointmentFormData {
  id?: string
  status?: string
  description?: string
  start: string
  end: string
  minutesDuration?: number
  comment?: string
  patientId: string
  patientName?: string
  practitionerId: string
  practitionerName?: string
  serviceType?: string
  reason?: string
}

export interface PrescriptionFormData {
  id?: string
  status?: string
  intent?: string
  medicationName: string
  patientId: string
  patientName?: string
  practitionerId: string
  practitionerName?: string
  dosageText: string
  dosagePeriodStart?: string
  dosagePeriodEnd?: string
  note?: string
}

export interface ClinicalRecordFormData {
  id?: string
  status?: string
  category?: string
  code: string
  codeDisplay: string
  patientId: string
  patientName?: string
  practitionerId?: string
  practitionerName?: string
  effectiveDateTime: string
  valueString?: string
  valueQuantity?: number
  valueUnit?: string
  note?: string
}

export interface InvoiceFormData {
  id?: string
  status?: string
  type?: string
  patientId: string
  patientName?: string
  date: string
  lineItems: InvoiceLineItemFormData[]
  paymentTerms?: string
  note?: string
}

export interface InvoiceLineItemFormData {
  sequence?: number
  description: string
  amount: number
  currency?: string
  quantity?: number
}

// API Response types
export interface APIError {
  message: string
  code?: string
  details?: any
}

// DataTable types
export interface DataTableColumn {
  key: string
  label: string
  sortable?: boolean
}

// Select Option
export interface SelectOption {
  label: string
  value: string | number
}

// Status types
export type AppointmentStatus = 'proposed' | 'pending' | 'booked' | 'arrived' | 'fulfilled' | 'cancelled' | 'noshow' | 'checked-in' | 'waitlist'
export type PrescriptionStatus = 'active' | 'on-hold' | 'cancelled' | 'completed' | 'entered-in-error' | 'stopped' | 'draft' | 'unknown'
export type InvoiceStatus = 'draft' | 'issued' | 'balanced' | 'cancelled' | 'entered-in-error'
export type ObservationStatus = 'registered' | 'preliminary' | 'final' | 'amended' | 'corrected' | 'cancelled' | 'entered-in-error' | 'unknown'

// Chart data types
export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label?: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  borderWidth?: number
  tension?: number
  fill?: boolean
}

export interface ChartOptions {
  responsive: boolean
  maintainAspectRatio: boolean
  plugins?: {
    legend?: {
      position?: 'top' | 'bottom' | 'left' | 'right'
      display?: boolean
    }
  }
  scales?: {
    y?: {
      beginAtZero?: boolean
      ticks?: {
        precision?: number
      }
    }
  }
}
