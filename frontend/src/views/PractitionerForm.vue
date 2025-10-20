<template>
  <div class="space-y-6 animate-fade-in max-w-4xl mx-auto">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">
        {{ isEditMode ? $t('practitioner.editPractitioner') : $t('practitioner.addPractitioner') }}
      </h1>
    </div>

    <form
      class="space-y-6"
      @submit.prevent="handleSubmit"
    >
      <!-- Personal Info -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-lg font-semibold mb-6">
          {{ $t('practitioner.personalInfo') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.prefix') }}</label>
            <select
              v-model="formData.prefix"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">
                {{ $t('common.select') }}
              </option>
              <option value="Dr.">
                Dr.
              </option>
              <option value="Prof.">
                Prof.
              </option>
              <option value="Mr.">
                Mr.
              </option>
              <option value="Ms.">
                Ms.
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.givenName') }} *</label>
            <input
              v-model="formData.givenName"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.familyName') }} *</label>
            <input
              v-model="formData.familyName"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.gender') }} *</label>
            <select
              v-model="formData.gender"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="male">
                {{ $t('practitioner.male') }}
              </option>
              <option value="female">
                {{ $t('practitioner.female') }}
              </option>
              <option value="other">
                {{ $t('practitioner.other') }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Professional Info -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <h2 class="text-lg font-semibold mb-6">
          {{ $t('practitioner.professionalInfo') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.specialization') }} *</label>
            <input
              v-model="formData.specialization"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.qualification') }} *</label>
            <input
              v-model="formData.qualification"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.email') }} *</label>
            <input
              v-model="formData.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('practitioner.phone') }} *</label>
            <input
              v-model="formData.phone"
              type="tel"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-4">
        <button
          type="button"
          class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          @click="$router.push('/practitioners')"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="submit"
          :disabled="saving"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePractitionerStore } from '../stores/practitioner'
import { buildPractitioner, extractPractitionerFormData } from '../services/api'
import { useI18n } from 'vue-i18n'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const toast = useToast()
const practitionerStore = usePractitionerStore()
const isEditMode = computed(() => !!route.params.id)
const saving = ref<boolean>(false)

interface PractitionerFormData {
  prefix: string
  givenName: string
  familyName: string
  middleName: string
  gender: string
  birthDate: string
  npi: string
  licenseNumber: string
  specialization: string
  qualification: string
  yearsOfExperience: number
  addressLine: string
  city: string
  state: string
  postalCode: string
  country: string
  email: string
  phone: string
  active: boolean
}

const formData = ref<PractitionerFormData>({
  prefix: '',
  givenName: '',
  familyName: '',
  middleName: '',
  gender: 'male',
  birthDate: '',
  npi: '',
  licenseNumber: '',
  specialization: '',
  qualification: '',
  yearsOfExperience: 0,
  addressLine: '',
  city: '',
  state: '',
  postalCode: '',
  country: '',
  email: '',
  phone: '',
  active: true
})

onMounted(async () => {
  if (isEditMode.value) {
    const practitioner = await practitionerStore.fetchPractitionerById(route.params.id as string)
    Object.assign(formData.value, extractPractitionerFormData(practitioner))
  }
})

const handleSubmit = async (): Promise<void> => {
  saving.value = true
  try {
    const practitionerData = buildPractitioner(formData.value)
    if (isEditMode.value) {
      await practitionerStore.updatePractitioner(route.params.id as string, practitionerData)
      toast.success(t('practitioner.updateSuccess'))
    } else {
      await practitionerStore.createPractitioner(practitionerData)
      toast.success(t('practitioner.createSuccess'))
    }
    router.push('/practitioners')
  } catch (error) {
    toast.error(t('practitioner.saveError'))
  } finally {
    saving.value = false
  }
}
</script>
