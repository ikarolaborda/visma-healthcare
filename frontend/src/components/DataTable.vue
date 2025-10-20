<template>
  <div class="glass rounded-2xl shadow-lg overflow-hidden animate-fade-in">
    <!-- Table Header with Search and Actions -->
    <div class="p-6 border-b border-gray-200">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex-1">
          <div
            v-if="searchable"
            class="relative"
          >
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg
                class="h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="$t('table.filterBy')"
              class="block w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
            >
          </div>
        </div>
        <div class="flex items-center gap-2">
          <slot name="actions" />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50/50 backdrop-blur-sm">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100/50 transition-colors"
              @click="sort(column.key)"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <span
                  v-if="sortKey === column.key"
                  class="text-primary-600"
                >
                  <svg
                    v-if="sortOrder === 'asc'"
                    class="h-4 w-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                      clip-rule="evenodd"
                      fill-rule="evenodd"
                    />
                  </svg>
                  <svg
                    v-else
                    class="h-4 w-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z"
                      clip-rule="evenodd"
                      fill-rule="evenodd"
                    />
                  </svg>
                </span>
              </div>
            </th>
            <th
              v-if="$slots.actions"
              class="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider"
            >
              {{ $t('common.actions') }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(row, index) in paginatedData"
            :key="getRowKey(row, index)"
            class="hover:bg-gray-50/50 transition-colors"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
            >
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :value="getValue(row, column.key)"
              >
                {{ getValue(row, column.key) }}
              </slot>
            </td>
            <td
              v-if="$slots.actions"
              class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
            >
              <slot
                name="actions"
                :row="row"
              />
            </td>
          </tr>
          <tr v-if="paginatedData.length === 0">
            <td
              :colspan="columns.length + ($slots.actions ? 1 : 0)"
              class="px-6 py-12 text-center text-gray-500"
            >
              <div class="flex flex-col items-center justify-center space-y-3">
                <svg
                  class="h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                  />
                </svg>
                <p class="text-sm font-medium">
                  {{ $t('table.noData') }}
                </p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="paginate && filteredData.length > 0"
      class="px-6 py-4 border-t border-gray-200 bg-gray-50/30"
    >
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="text-sm text-gray-700">
          {{ $t('common.showing') }} 
          <span class="font-medium">{{ startRow }}</span>
          {{ $t('common.of') }}
          <span class="font-medium">{{ endRow }}</span>
          {{ $t('common.of') }}
          <span class="font-medium">{{ filteredData.length }}</span>
          {{ $t('common.results') }}
        </div>
        <div class="flex items-center gap-2">
          <button
            :disabled="currentPage === 1"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            @click="previousPage"
          >
            {{ $t('table.previous') }}
          </button>
          <span class="text-sm text-gray-700">
            {{ $t('table.page') }} {{ currentPage }} {{ $t('common.of') }} {{ totalPages }}
          </span>
          <button
            :disabled="currentPage === totalPages"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            @click="nextPage"
          >
            {{ $t('table.next') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

export interface TableColumn {
  key: string
  label: string
}

export interface DataTableProps {
  data: any[]
  columns: TableColumn[]
  searchable?: boolean
  paginate?: boolean
  perPage?: number
  rowKey?: string
}

const props = withDefaults(defineProps<DataTableProps>(), {
  searchable: true,
  paginate: true,
  perPage: 10,
  rowKey: 'id'
})

const searchQuery = ref<string>('')
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')
const currentPage = ref<number>(1)

const filteredData = computed<any[]>(() => {
  let filtered = [...props.data]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((row: any) => {
      return props.columns.some((column: TableColumn) => {
        const value = getValue(row, column.key)
        return String(value).toLowerCase().includes(query)
      })
    })
  }

  // Sorting
  if (sortKey.value) {
    filtered.sort((a: any, b: any) => {
      const aVal = getValue(a, sortKey.value)
      const bVal = getValue(b, sortKey.value)

      if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
      return 0
    })
  }

  return filtered
})

const totalPages = computed<number>(() => {
  if (!props.paginate) return 1
  return Math.ceil(filteredData.value.length / props.perPage)
})

const paginatedData = computed<any[]>(() => {
  if (!props.paginate) return filteredData.value

  const start = (currentPage.value - 1) * props.perPage
  const end = start + props.perPage
  return filteredData.value.slice(start, end)
})

const startRow = computed<number>(() => {
  return (currentPage.value - 1) * props.perPage + 1
})

const endRow = computed<number>(() => {
  return Math.min(currentPage.value * props.perPage, filteredData.value.length)
})

const sort = (key: string): void => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const previousPage = (): void => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = (): void => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const getValue = (row: any, key: string): any => {
  return key.split('.').reduce((obj, k) => obj?.[k], row) ?? 'N/A'
}

const getRowKey = (row: any, index: number): string | number => {
  return row[props.rowKey] ?? index
}

// Reset to page 1 when search changes
watch(searchQuery, () => {
  currentPage.value = 1
})
</script>
