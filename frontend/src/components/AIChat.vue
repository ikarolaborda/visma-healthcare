<template>
  <div class="fixed bottom-6 right-6 z-50">
    <!-- Chat Window -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="mb-4 w-96 glass rounded-2xl shadow-2xl overflow-hidden"
      >
        <!-- Chat Header -->
        <div class="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="h-10 w-10 rounded-lg bg-white/20 flex items-center justify-center">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg">AI Assistant</h3>
              <p class="text-white/80 text-xs">Ask me about your data</p>
            </div>
          </div>
          <button
            @click="isOpen = false"
            class="text-white/80 hover:text-white transition-colors"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Chat Messages -->
        <div class="p-6 h-96 overflow-y-auto bg-white/50 space-y-4">
          <div v-if="messages.length === 0" class="text-center text-gray-500 mt-16">
            <p class="text-sm">Select a question below to get started</p>
          </div>

          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="[
              'flex',
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-[80%] rounded-2xl px-4 py-3',
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white shadow-md text-gray-900'
              ]"
            >
              <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
            </div>
          </div>

          <div v-if="loading" class="flex justify-start">
            <div class="bg-white shadow-md rounded-2xl px-4 py-3">
              <div class="flex space-x-2">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Custom Prompt Input -->
        <div class="p-6 bg-white/70 border-t border-gray-200">
          <form @submit.prevent="handleCustomPrompt" class="flex gap-2">
            <input
              v-model="customPrompt"
              type="text"
              placeholder="Ask me anything about your healthcare data..."
              :disabled="loading"
              class="flex-1 px-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              :disabled="loading || !customPrompt.trim()"
              class="px-4 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </form>
        </div>

        <!-- Predefined Prompts -->
        <div class="px-6 pb-6 bg-white/70 space-y-2">
          <p class="text-xs font-medium text-gray-700 mb-3">Quick Questions:</p>
          <button
            v-for="(prompt, idx) in prompts"
            :key="idx"
            @click="sendMessage(prompt)"
            :disabled="loading"
            class="w-full text-left px-4 py-2.5 text-sm bg-white hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ prompt }}
          </button>
        </div>
      </div>
    </transition>

    <!-- Chat Toggle Button -->
    <button
      @click="isOpen = !isOpen"
      class="h-14 w-14 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
      :class="{ 'scale-95': isOpen }"
    >
      <svg v-if="!isOpen" class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
      <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const isOpen = ref(false)
const loading = ref(false)
const messages = ref<Message[]>([])
const customPrompt = ref('')

const prompts = [
  'How many appointments were made in the last 7 days?',
  'What was the most prescribed medication in the last 7 days?',
  'Who was the most demanded practitioner?',
  'What was the most demanded medical speciality?',
  'How many payments are still expected?'
]

const sendMessage = async (prompt: string) => {
  if (loading.value) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: prompt
  })

  loading.value = true

  try {
    const response = await api.post('/api/ai-chat/', {
      prompt
    })

    // Add assistant response
    messages.value.push({
      role: 'assistant',
      content: response.data.response
    })
  } catch (err: any) {
    console.error('AI Chat error:', err)
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error processing your request. Please try again.'
    })
  } finally {
    loading.value = false
  }
}

const handleCustomPrompt = async () => {
  const prompt = customPrompt.value.trim()
  if (!prompt || loading.value) return

  await sendMessage(prompt)
  customPrompt.value = ''
}
</script>
