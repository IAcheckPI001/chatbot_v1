<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)
const userInput = ref('')
const isLoading = ref(false)
const apiError = ref('')

const API_BASE_URL = 'http://localhost:5000/api'

// chat messages shown in widget
const messages = ref<Array<{text: string; from: 'user' | 'bot'}>>([
  { text: 'Xin chào! Tôi là trợ lý AI của UBND Phường.', from: 'bot' }
])

async function sendMessage() {
  if (!userInput.value.trim()) return
  const text = userInput.value.trim()
  // push user message
  messages.value.push({ text, from: 'user' })
  userInput.value = ''
  
  // clear table data
  responses.value = []
  
  // call backend API
  isLoading.value = true
  apiError.value = ''
  
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    const data = await response.json()
    
    // display bot response in chat
    if (data.replies && data.replies.length > 0) {
      let botReply = data.replies[0].text_content
      messages.value.push({ text: botReply, from: 'bot' })
    }
    
    // update table with all returned responses
    responses.value = data.replies || []
  } catch (error: any) {
    apiError.value = `Connection error: ${error.message}`
    messages.value.push({ text: 'Xin lỗi, có lỗi khi kết nối đến server.', from: 'bot' })
  } finally {
    isLoading.value = false
  }
}
const responses = ref<Array<{id: string; text_content: string; score: number}>>([])
</script>

<template>
  <div>
    <section class="data-table" :class="{ 'with-chat': isOpen }">
      <table>
        <thead>
          <tr>
            <th class="col-index">ID</th>
            <th class="col-content">Content</th>
            <th class="col-scope">Scope</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(item, idx) in responses" :key="idx">
            <td class="col-index">{{ idx + 1 }}</td>

            <td class="col-content">
              <div class="content-text">
                {{ item.text_content }}
              </div>
            </td>

            <td class="col-scope">
              <span class="badge">{{ item.score }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
    <!-- Floating Button -->
    <section class="chat-toggle" @click="isOpen = !isOpen">
      💬
    </section>

    <!-- Chat Window -->
    <div v-if="isOpen" class="chat-widget">
      <!-- Header -->
      <div class="chat-header">
        <div class="chat-title">
          <span class="dot"></span>
          Chatbot 1.0
        </div>
        <button class="close-btn" @click="isOpen = false">✕</button>
      </div>

      <!-- Messages -->
      <div class="chat-body">
        <div v-for="(msg, idx) in messages" :key="idx" :class="msg.from + '-message'">
          {{ msg.text }}
        </div>
      </div>

      <!-- Input -->
      <div class="chat-footer">
        <input
          v-model="userInput"
          placeholder="Nhập câu hỏi của bạn..."
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage" :disabled="isLoading">{{ isLoading ? '⏳' : '➤' }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 55px;
  height: 55px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #9333ea);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
  z-index: 1000;
}

.chat-widget {
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 380px;
  height: 520px;
  background: #f3f4f6;
  border-radius: 18px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000;
}

/* Header */
.chat-header {
  background: linear-gradient(135deg, #6366f1, #9333ea);
  color: white;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

/* Body */
.chat-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bot-message, .user-message {
  padding: 12px 14px;
  margin: 6px 0;
  border-radius: 14px;
  max-width: 80%;
  font-size: 1em;
  box-shadow: 0 3px 8px rgba(0,0,0,0.05);
}

.bot-message {
  background: white;
  align-self: flex-start;
}

.user-message {
  background: #e0e7ff;
  align-self: flex-end;
}

/* Footer */
.chat-footer {
  padding: 12px;
  background: white;
  display: flex;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
}

.chat-footer input {
  flex: 1;
  padding: 14px 12px;
  border-radius: 12px;
  border: 1px solid #d1d5db;
  outline: none;
  font-size: 0.95em;
}

.chat-footer input:focus {
  border-color: #6366f1;
}

.chat-footer button {
  width: 46px;
  border-radius: 100%;
  border: none;
  background: linear-gradient(135deg, #6366f1, #9333ea);
  color: white;
  cursor: pointer;
}

.chat-footer button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.data-table {
  margin-top: 2rem;
  background: white;
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.06);
  overflow: hidden;
}

.data-table table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

/* Header */
.data-table thead {
  background: #f9fafb;
}

.data-table th {
  text-align: center;
  padding: 14px 16px;
  font-size: 1em;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #e5e7eb;
}

/* Body */
.data-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 1em;
  color: #1f2937;
  vertical-align: top;
}

.data-table tr:hover {
  background: #f9fafb;
}

/* Column width control */
.col-index {
  width: 40px;
  text-align: center;
  font-weight: 600;
  color: #6b7280;
}

.col-content {
  width: 70%;
}

.col-scope {
  width: 80px;
  text-align: center;
}

/* when chat is open reserve space on right so table isn't covered */
.data-table.with-chat {
  margin-right: 380px; /* chat width 360px + 20px gap */
}

/* Content text */
.content-text {
  line-height: 1.5;
  word-break: break-word;
  /* allow full text to display */
  display: block;
  overflow: visible;
}

/* Scope badge */
.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 1em;
  font-weight: 500;
  background: #e0e7ff;
  color: #3730a3;
}

</style>