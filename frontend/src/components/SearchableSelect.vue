<template>
  <div class="relative" ref="dropdownRef">
    <!-- Input Field -->
    <div class="relative">
      <input
        type="text"
        v-model="searchQuery"
        @focus="isOpen = true"
        @input="handleSearch"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="block w-full px-3 py-3 pr-10 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white/50 backdrop-blur-sm transition-all"
        :class="{ 'cursor-not-allowed opacity-60': disabled }"
      />
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- Dropdown Options -->
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-show="isOpen && filteredOptions.length > 0"
        class="absolute z-50 mt-1 w-full bg-white rounded-xl shadow-lg max-h-60 overflow-auto border border-gray-200"
      >
        <ul class="py-1">
          <li
            v-for="option in filteredOptions"
            :key="option[valueKey]"
            @click="selectOption(option)"
            class="px-4 py-2 hover:bg-primary-50 cursor-pointer transition-colors"
            :class="{
              'bg-primary-100 text-primary-900': modelValue === option[valueKey],
              'text-gray-900': modelValue !== option[valueKey]
            }"
          >
            {{ option[labelKey] }}
          </li>
        </ul>
      </div>
    </transition>

    <!-- No Results Message -->
    <div
      v-show="isOpen && searchQuery && filteredOptions.length === 0"
      class="absolute z-50 mt-1 w-full bg-white rounded-xl shadow-lg border border-gray-200 px-4 py-3"
    >
      <p class="text-sm text-gray-500 text-center">No results found</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

export interface SearchableSelectOption {
  [key: string]: any
}

export interface SearchableSelectProps {
  modelValue: string | number
  options: SearchableSelectOption[]
  labelKey?: string
  valueKey?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<SearchableSelectProps>(), {
  modelValue: '',
  labelKey: 'label',
  valueKey: 'value',
  placeholder: 'Select an option...',
  required: false,
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const searchQuery = ref<string>('')
const isOpen = ref<boolean>(false)
const dropdownRef = ref<HTMLDivElement | null>(null)

// Initialize search query with selected option label
const initializeSearchQuery = (): void => {
  if (props.modelValue) {
    const selectedOption = props.options.find(
      (opt: SearchableSelectOption) => opt[props.valueKey] === props.modelValue
    )
    if (selectedOption) {
      searchQuery.value = selectedOption[props.labelKey]
    }
  }
}

onMounted(() => {
  initializeSearchQuery()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Watch for external changes to modelValue
watch(() => props.modelValue, () => {
  initializeSearchQuery()
})

// Watch for changes to options (e.g., when data loads)
watch(() => props.options, () => {
  initializeSearchQuery()
}, { deep: true })

const filteredOptions = computed<SearchableSelectOption[]>(() => {
  if (!searchQuery.value) {
    return props.options
  }

  const query = searchQuery.value.toLowerCase()
  return props.options.filter((option: SearchableSelectOption) =>
    option[props.labelKey].toLowerCase().includes(query)
  )
})

const selectOption = (option: SearchableSelectOption): void => {
  searchQuery.value = option[props.labelKey]
  emit('update:modelValue', option[props.valueKey])
  isOpen.value = false
}

const handleSearch = (): void => {
  isOpen.value = true
  // If user clears the input, clear the selection
  if (!searchQuery.value) {
    emit('update:modelValue', '')
  }
}

const handleClickOutside = (event: MouseEvent): void => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
    // Restore the selected option label if user clicked outside
    initializeSearchQuery()
  }
}
</script>
