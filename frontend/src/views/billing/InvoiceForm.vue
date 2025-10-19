<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ isEditMode ? 'Edit Invoice' : 'Create New Invoice' }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ isEditMode ? 'Update invoice information' : 'Create a new FHIR-compliant invoice' }}
        </p>
      </div>
      <router-link
        to="/billing"
        class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
      >
        <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to List
      </router-link>
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

    <!-- Invoice Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Information Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Invoice Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Status -->
          <div>
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">
              Status <span class="text-danger-500">*</span>
            </label>
            <select
              id="status"
              v-model="formData.status"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            >
              <option value="" disabled>Select status</option>
              <option value="draft">Draft</option>
              <option value="issued">Issued</option>
              <option value="balanced">Balanced (Paid)</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <!-- Invoice Date -->
          <div>
            <label for="date" class="block text-sm font-medium text-gray-700 mb-1">
              Invoice Date <span class="text-danger-500">*</span>
            </label>
            <input
              id="date"
              v-model="formData.date"
              type="date"
              required
              class="block w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            />
          </div>
        </div>
      </div>

      <!-- Patient Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Patient
          </h3>
        </div>

        <div>
          <label for="patientId" class="block text-sm font-medium text-gray-700 mb-1">
            Patient <span class="text-danger-500">*</span>
          </label>
          <SearchableSelect
            v-model="formData.patientId"
            :options="patientOptions"
            label-key="label"
            value-key="value"
            placeholder="Select patient..."
            required
          />
        </div>
      </div>

      <!-- Line Items Section -->
      <div class="glass rounded-2xl shadow-lg p-6 space-y-6">
        <div class="border-b border-gray-200 pb-3 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Line Items
          </h3>
          <button
            type="button"
            @click="addLineItem"
            class="inline-flex items-center px-3 py-2 text-sm font-medium text-primary-700 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Item
          </button>
        </div>

        <div class="space-y-4">
          <div
            v-for="(item, index) in formData.lineItems"
            :key="index"
            class="border border-gray-200 rounded-xl p-4 bg-white/30"
          >
            <div class="flex items-start justify-between mb-4">
              <h4 class="text-sm font-medium text-gray-700">Item {{ index + 1 }}</h4>
              <button
                type="button"
                @click="removeLineItem(index)"
                class="text-danger-600 hover:text-danger-800"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="md:col-span-2">
                <label :for="`item-description-${index}`" class="block text-sm font-medium text-gray-700 mb-1">
                  Description <span class="text-danger-500">*</span>
                </label>
                <input
                  :id="`item-description-${index}`"
                  v-model="item.description"
                  type="text"
                  required
                  class="block w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Service description"
                />
              </div>

              <div>
                <label :for="`item-amount-${index}`" class="block text-sm font-medium text-gray-700 mb-1">
                  Amount ($) <span class="text-danger-500">*</span>
                </label>
                <input
                  :id="`item-amount-${index}`"
                  v-model.number="item.amount"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="block w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>

          <div v-if="formData.lineItems.length === 0" class="text-center py-8 text-gray-500">
            <p>No items added. Click "Add Item" to begin.</p>
          </div>
        </div>

        <!-- Total -->
        <div class="border-t border-gray-200 pt-4">
          <div class="flex justify-between items-center">
            <span class="text-lg font-semibold text-gray-900">Total</span>
            <span class="text-2xl font-bold text-primary-600">${{ totalAmount.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <router-link
          to="/billing"
          class="px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          Cancel
        </router-link>
        <button
          type="submit"
          :disabled="loading"
          class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <svg
            v-if="loading"
            class="animate-spin h-5 w-5 mr-2 text-white"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ loading ? 'Saving...' : (isEditMode ? 'Update Invoice' : 'Create Invoice') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInvoiceStore } from '../../stores/invoice'
import { usePatientStore } from '../../stores/patient'
import { storeToRefs } from 'pinia'
import SearchableSelect from '../../components/SearchableSelect.vue'
import type { Invoice } from '../../types/fhir'

interface LineItem {
  description: string
  amount: number
}

const router = useRouter()
const route = useRoute()
const invoiceStore = useInvoiceStore()
const patientStore = usePatientStore()

const { loading, error } = storeToRefs(invoiceStore)

const isEditMode = computed(() => !!route.params.id)

const formData = ref({
  status: '',
  date: new Date().toISOString().split('T')[0],
  patientId: '',
  lineItems: [] as LineItem[]
})

const patientOptions = computed(() => {
  return patientStore.patients.map(p => ({
    label: `${p.name?.[0]?.given?.[0] || ''} ${p.name?.[0]?.family || ''}`.trim(),
    value: p.id || ''
  }))
})

const totalAmount = computed(() => {
  return formData.value.lineItems.reduce((sum, item) => sum + (item.amount || 0), 0)
})

const addLineItem = (): void => {
  formData.value.lineItems.push({
    description: '',
    amount: 0
  })
}

const removeLineItem = (index: number): void => {
  formData.value.lineItems.splice(index, 1)
}

onMounted(async () => {
  // Load patients for dropdown
  await patientStore.fetchPatients()

  if (isEditMode.value && route.params.id) {
    try {
      const invoice = await invoiceStore.fetchInvoiceById(route.params.id as string)

      // Extract form data from FHIR resource
      formData.value = {
        status: invoice.status,
        date: invoice.date || new Date().toISOString().split('T')[0],
        patientId: invoice.subject?.reference?.replace('Patient/', '') || '',
        lineItems: invoice.lineItem?.map(item => ({
          description: item.chargeItemCodeableConcept?.text || '',
          amount: item.priceComponent?.[0]?.amount?.value || 0
        })) || []
      }
    } catch (err) {
      console.error('Failed to load invoice:', err)
      router.push('/billing')
    }
  } else {
    // Add one empty line item for new invoices
    addLineItem()
  }
})

const handleSubmit = async (): Promise<void> => {
  try {
    // Build FHIR Invoice
    const invoice: Invoice = {
      resourceType: 'Invoice',
      status: formData.value.status as Invoice['status'],
      date: formData.value.date,
      subject: {
        reference: `Patient/${formData.value.patientId}`
      },
      lineItem: formData.value.lineItems.map(item => ({
        chargeItemCodeableConcept: {
          text: item.description
        },
        priceComponent: [{
          type: 'base',
          amount: {
            value: item.amount,
            currency: 'USD'
          }
        }]
      })),
      totalGross: {
        value: totalAmount.value,
        currency: 'USD'
      }
    }

    if (isEditMode.value && route.params.id) {
      await invoiceStore.updateInvoice(route.params.id as string, invoice)
    } else {
      await invoiceStore.createInvoice(invoice)
    }

    router.push('/billing')
  } catch (err) {
    console.error('Failed to save invoice:', err)
  }
}
</script>
