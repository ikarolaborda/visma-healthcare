<template>
  <div class="max-w-4xl mx-auto space-y-6 animate-fade-in">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Invoice Details</h1>
        <p class="mt-1 text-sm text-gray-500">View detailed invoice information</p>
      </div>
      <div class="flex items-center space-x-3">
        <router-link
          :to="`/billing/edit/${$route.params.id}`"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit
        </router-link>
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
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="glass rounded-2xl shadow-lg p-12 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading invoice details...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-danger-50 border-l-4 border-danger-500 rounded-xl p-4"
    >
      <div class="flex items-center">
        <svg class="h-5 w-5 text-danger-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="text-sm font-medium text-danger-700">{{ error }}</p>
      </div>
    </div>

    <!-- Invoice Details -->
    <div v-else-if="invoice" class="space-y-6">
      <!-- Invoice Header -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Invoice Information
          </h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p class="text-sm text-gray-500">Invoice ID</p>
            <p class="mt-1 text-sm font-mono text-gray-900">{{ invoice.id || 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Status</p>
            <span
              class="inline-flex mt-1 px-3 py-1 text-sm font-semibold rounded-full"
              :class="{
                'bg-gray-100 text-gray-700': invoice.status === 'draft',
                'bg-blue-100 text-blue-700': invoice.status === 'issued',
                'bg-success-100 text-success-700': invoice.status === 'balanced',
                'bg-danger-100 text-danger-700': invoice.status === 'cancelled'
              }"
            >
              {{ invoice.status }}
            </span>
          </div>
          <div>
            <p class="text-sm text-gray-500">Invoice Date</p>
            <p class="mt-1 text-gray-900">{{ formatDate(invoice.date) }}</p>
          </div>
          <div v-if="invoice.meta?.lastUpdated">
            <p class="text-sm text-gray-500">Last Updated</p>
            <p class="mt-1 text-gray-900">{{ formatDateTime(invoice.meta.lastUpdated) }}</p>
          </div>
        </div>
      </div>

      <!-- Patient Information -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Patient Information
          </h3>
        </div>
        <div>
          <p class="text-sm text-gray-500">Patient</p>
          <p class="mt-1 text-lg font-medium text-gray-900">{{ invoice.subject?.display || invoice.subject?.reference || 'N/A' }}</p>
        </div>
      </div>

      <!-- Line Items -->
      <div class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Line Items
          </h3>
        </div>

        <div v-if="invoice.lineItem && invoice.lineItem.length > 0" class="space-y-3">
          <div
            v-for="(item, index) in invoice.lineItem"
            :key="index"
            class="flex justify-between items-center p-4 bg-gray-50 rounded-lg"
          >
            <div>
              <p class="font-medium text-gray-900">{{ item.chargeItemCodeableConcept?.text || `Item ${index + 1}` }}</p>
            </div>
            <div class="text-right">
              <p class="text-lg font-semibold text-gray-900">
                ${{ formatAmount(item.priceComponent?.[0]?.amount?.value) }}
              </p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <p>No line items</p>
        </div>

        <!-- Total -->
        <div class="border-t border-gray-200 mt-6 pt-4">
          <div class="flex justify-between items-center">
            <div>
              <p class="text-sm text-gray-500">Subtotal</p>
              <p class="text-2xl font-bold text-gray-900">${{ formatAmount(invoice.totalNet?.value || invoice.totalGross?.value) }}</p>
            </div>
          </div>
          <div v-if="invoice.totalGross && invoice.totalNet && invoice.totalGross.value !== invoice.totalNet.value" class="flex justify-between items-center mt-3">
            <p class="text-sm text-gray-500">Total (Gross)</p>
            <p class="text-lg font-semibold text-gray-900">${{ formatAmount(invoice.totalGross.value) }}</p>
          </div>
        </div>
      </div>

      <!-- Payment Information -->
      <div v-if="invoice.totalPriceComponent && invoice.totalPriceComponent.length > 0" class="glass rounded-2xl shadow-lg p-6">
        <div class="border-b border-gray-200 pb-3 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="h-5 w-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Payment Details
          </h3>
        </div>
        <div class="space-y-3">
          <div v-for="(component, index) in invoice.totalPriceComponent" :key="index" class="flex justify-between">
            <p class="text-sm text-gray-600">{{ component.type }}</p>
            <p class="text-sm font-medium text-gray-900">${{ formatAmount(component.amount?.value) }}</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end space-x-4 pt-6">
        <button
          @click="handleDelete"
          :disabled="loading"
          class="px-6 py-3 text-sm font-medium text-white bg-danger-600 rounded-xl hover:bg-danger-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Delete Invoice
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInvoiceStore } from '../../stores/invoice'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()
const invoiceStore = useInvoiceStore()

const { loading, error, currentInvoice: invoice } = storeToRefs(invoiceStore)

onMounted(async () => {
  if (route.params.id) {
    try {
      await invoiceStore.fetchInvoiceById(route.params.id as string)
    } catch (err) {
      console.error('Failed to load invoice:', err)
    }
  }
})

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDateTime = (dateStr: string | undefined): string => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatAmount = (amount: number | undefined): string => {
  if (!amount) return '0.00'
  return amount.toFixed(2)
}

const handleDelete = async (): Promise<void> => {
  if (!route.params.id) return

  if (confirm('Are you sure you want to delete this invoice? This action cannot be undone.')) {
    try {
      await invoiceStore.deleteInvoice(route.params.id as string)
      router.push('/billing')
    } catch (err) {
      console.error('Failed to delete invoice:', err)
    }
  }
}
</script>
