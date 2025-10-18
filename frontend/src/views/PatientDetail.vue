<template>
  <div class="patient-detail">
    <div v-if="loading" class="loading">Loading patient details...</div>

    <div v-else-if="error" class="error">
      {{ error }}
      <router-link to="/" class="btn btn-secondary">Back to List</router-link>
    </div>

    <div v-else-if="patient" class="card">
      <div class="card-header">
        <h2>Patient Details</h2>
        <div class="header-actions">
          <router-link
            :to="`/patient/${patient.id}/edit`"
            class="btn btn-primary"
          >
            Edit
          </router-link>
          <button @click="handleDelete" class="btn btn-danger">
            Delete
          </button>
        </div>
      </div>

      <div class="detail-section">
        <h3>Personal Information</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="label">Full Name:</span>
            <span class="value">{{ getPatientName() }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Gender:</span>
            <span class="value">{{ patient.gender }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Birth Date:</span>
            <span class="value">{{ patient.birthDate }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Status:</span>
            <span class="value">{{ patient.active ? 'Active' : 'Inactive' }}</span>
          </div>
        </div>
      </div>

      <div v-if="hasContactInfo" class="detail-section">
        <h3>Contact Information</h3>
        <div class="detail-grid">
          <div v-if="getEmail()" class="detail-item">
            <span class="label">Email:</span>
            <span class="value">{{ getEmail() }}</span>
          </div>
          <div v-if="getPhone()" class="detail-item">
            <span class="label">Phone:</span>
            <span class="value">{{ getPhone() }}</span>
          </div>
        </div>
      </div>

      <div v-if="hasAddress" class="detail-section">
        <h3>Address</h3>
        <div class="detail-item">
          <span class="value">{{ getAddress() }}</span>
        </div>
      </div>

      <div class="form-actions">
        <router-link to="/" class="btn btn-secondary">Back to List</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePatientStore } from '../stores/patient'
import { storeToRefs } from 'pinia'

export default {
  name: 'PatientDetail',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const patientStore = usePatientStore()
    const { loading, error } = storeToRefs(patientStore)

    const patient = ref(null)

    onMounted(async () => {
      try {
        patient.value = await patientStore.fetchPatientById(route.params.id)
      } catch (error) {
        // Error is handled by the store
      }
    })

    const getPatientName = () => {
      const name = patient.value?.name?.[0]
      if (!name) return 'N/A'
      const given = name.given?.join(' ') || ''
      return `${given} ${name.family || ''}`.trim()
    }

    const getEmail = () => {
      return patient.value?.telecom?.find(t => t.system === 'email')?.value || null
    }

    const getPhone = () => {
      return patient.value?.telecom?.find(t => t.system === 'phone')?.value || null
    }

    const getAddress = () => {
      const address = patient.value?.address?.[0]
      if (!address) return 'N/A'

      const parts = [
        address.line?.join(', '),
        address.city,
        address.state,
        address.postalCode,
        address.country,
      ].filter(Boolean)

      return parts.join(', ') || 'N/A'
    }

    const hasContactInfo = computed(() => getEmail() || getPhone())
    const hasAddress = computed(() => {
      const address = patient.value?.address?.[0]
      return address && (address.line || address.city || address.state || address.postalCode || address.country)
    })

    const handleDelete = async () => {
      if (confirm('Are you sure you want to delete this patient?')) {
        try {
          await patientStore.deletePatient(route.params.id)
          alert('Patient deleted successfully')
          router.push('/')
        } catch (error) {
          alert('Failed to delete patient')
        }
      }
    }

    return {
      patient,
      loading,
      error,
      getPatientName,
      getEmail,
      getPhone,
      getAddress,
      hasContactInfo,
      hasAddress,
      handleDelete,
    }
  },
}
</script>

<style scoped>
.patient-detail {
  max-width: 800px;
  margin: 0 auto;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.detail-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.detail-section:last-of-type {
  border-bottom: none;
}

.detail-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item .label {
  font-weight: 600;
  color: #7f8c8d;
  font-size: 0.875rem;
  text-transform: uppercase;
}

.detail-item .value {
  color: #2c3e50;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
