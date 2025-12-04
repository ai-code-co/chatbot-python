<template>
  <div class="flex flex-col h-full p-4 bg-white dark:bg-gray-800">
    <div ref="chatContainer" class="flex-1 overflow-y-auto mb-2">
      <MessageBubble v-for="(msg, i) in messages" :key="i" :message="msg"/>
      <TypingIndicator v-if="isTyping" :active="isTyping"/>
    </div>
    <div class="flex">
      <input v-model="inputText" @keyup.enter="sendMessage" placeholder="Type your message..."
        class="flex-1 p-2 border rounded-l-lg focus:outline-none"/>
      <button @click="sendMessage" class="bg-blue-500 text-white p-2 rounded-r-lg">Send</button>
    </div>
  </div>
</template>

<script>
import MessageBubble from './MessageBubble.vue'
import TypingIndicator from './TypingIndicator.vue'
import { v4 as uuidv4 } from 'uuid'

export default {
  components: { MessageBubble, TypingIndicator },
  data() {
    return {
      messages: [],
      inputText: '',
      ws: null,
      userId: uuidv4(),
      isTyping: false,
      buffer: ''
    }

  },
  mounted() {
    this.connectWebSocket();
  },
  methods: {
    connectWebSocket() {
      // const wsUrl = `ws://127.0.0.1:8000/ws/chat/${this.userId}/`
      const wsUrl = `ws://localhost:8000/ws/chat/123/
`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => console.log("WebSocket connected");

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if(data.type === 'stream') {
          this.buffer += data.delta
          this.isTyping = true
        } else if(data.type === 'final') {
          this.messages.push({role:'assistant', text:this.buffer + data.text})
          this.buffer = ''
          this.isTyping = false
          this.scrollToBottom()
        }
   
  else if (data.type === 'message') {
    this.messages.push({ role: 'assistant', text: data.message });
    this.scrollToBottom();
  }
        
        else if(data.type === 'system') {
          console.log("System message:", data.message)
        } else if(data.type === 'error') {
          console.error("Error:", data.message)
        }
      }

      this.ws.onclose = () => console.log("WebSocket disconnected")
    },
    sendMessage() {
      if(!this.inputText.trim()) return
      // push user message locally
      this.messages.push({role:'user', text:this.inputText})
      this.scrollToBottom()
      // send to backend
      this.ws.send(JSON.stringify({type:'message', message:this.inputText}))
      this.inputText = ''
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.chatContainer
        container.scrollTop = container.scrollHeight
      })
    }
  }
}
</script>

<style scoped>
</style>
