<template>
  <div class="space-y-6 animate-fade-in max-w-4xl mx-auto">
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    </div>

    <template v-else-if="practitioner">
      <!-- Header -->
      <div class="glass rounded-2xl shadow-lg p-8">
        <div class="flex items-start justify-between">
          <div class="flex items-center space-x-6">
            <div class="h-24 w-24 rounded-2xl bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center shadow-lg">
              <span class="text-white font-bold text-3xl">{{ getInitials(practitioner) }}</span>
            </div>
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ getPractitionerName(practitioner) }}</h1>
              <p class="text-lg text-gray-600 mt-1">{{ practitioner.specialization }}</p>
              <span :class="['inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-2', practitioner.active ? 'bg-success-100 text-success-700' : 'bg-gray-100 text-gray-700']">
                {{ practitioner.active ? $t('common.active') : $t('common.inactive') }}
              </span>
            </div>
          </div>
          <div class="flex gap-2">
            <router-link :to="`/practitioners/${practitioner.id}/edit`" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">{{ $t('common.edit') }}</router-link>
            <button @click="handleDelete" class="px-4 py-2 bg-danger-600 text-white rounded-lg hover:bg-danger-700">{{ $t('common.delete') }}</button>
          </div>
        </div>
      </div>

      <!-- Details -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="glass rounded-2xl shadow-lg p-8">
          <h2 class="text-lg font-semibold mb-4">{{ $t('practitioner.professionalInfo') }}</h2>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm text-gray-500">{{ $t('practitioner.qualification') }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ practitioner.qualification }}</dd>
            </div>
            <div v-if="practitioner.npi">
              <dt class="text-sm text-gray-500">{{ $t('practitioner.npi') }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ practitioner.npi }}</dd>
            </div>
            <div v-if="practitioner.years_of_experience">
              <dt class="text-sm text-gray-500">{{ $t('practitioner.yearsOfExperience') }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ practitioner.years_of_experience }} {{ $t('practitioner.years') }}</dd>
            </div>
          </dl>
        </div>

        <div class="glass rounded-2xl shadow-lg p-8">
          <h2 class="text-lg font-semibold mb-4">{{ $t('practitioner.contactInfo') }}</h2>
          <dl class="space-y-3">
            <div>
              <dt class="text-sm text-gray-500">{{ $t('practitioner.email') }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ practitioner.email }}</dd>
            </div>
            <div>
              <dt class="text-sm text-gray-500">{{ $t('practitioner.phone') }}</dt>
              <dd class="text-sm font-medium text-gray-900">{{ practitioner.phone }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePractitionerStore } from '../stores/practitioner'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const practitionerStore = usePractitionerStore()
const practitioner = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    practitioner.value = await practitionerStore.fetchPractitionerById(route.params.id)
  } finally {
    loading.value = false
  }
})

const getPractitionerName = (p) => {
  const prefix = p.prefix ? `${p.prefix} ` : ''
  return `${prefix}${p.given_name} ${p.family_name}`.trim()
}

const getInitials = (p) => {
  return `${p.given_name[0]}${p.family_name[0]}`.toUpperCase()
}

const handleDelete = async () => {
  if (confirm(t('practitioner.confirmDelete', { name: getPractitionerName(practitioner.value) }))) {
    await practitionerStore.deletePractitioner(practitioner.value.id)
    router.push('/practitioners')
  }
}
</script>
