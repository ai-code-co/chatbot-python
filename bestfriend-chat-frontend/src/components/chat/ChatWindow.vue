<template>
  <div class="chat-wrapper">
    <div class="bot-header">
      <div class="bot-avatar">🤖</div>
      <div class="bot-info">
        <span>
                 <h4 >AIRA Bot</h4>
        </span>
 
        <span>AI Assistant</span>
      </div>
    </div>

    <div ref="chatContainer" class="messages">
      <MessageBubble 
        v-for="(msg, i) in messages" 
        :key="i" 
        :message="msg"
      />
      <TypingIndicator v-if="isTyping" :active="isTyping" :text="buffer" />
    </div>

    <div class="quick-actions">
      
      <button>Chat with a Live Agent</button>
    </div>
    <div class="input-area">
  <input 
    v-model="inputText"
    @keyup.enter="sendMessage"
    placeholder="Write your message…"
  />
  <button @click="sendMessage">
  <svg xmlns="http://www.w3.org/2000/svg" class="send-icon" fill="currentColor" viewBox="0 0 24 24">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
  </svg>
  </button>
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

const isProd = window.location.hostname !== "localhost" 
            && window.location.hostname !== "127.0.0.1";

console.log("Is production environment?", isProd);

const wsBase = "wss://friendly-chat-bot.onrender.com"

  console.log("WebSocket base URL:", wsBase);
      // const wsUrl = `${wsBase}/ws/chat/123/`;
    
      // const wsUrl = `ws://localhost:8000/ws/chat/123/`
      const wsUrl = `ws://127.0.0.1:8000/ws/chat/123/`;
      console.log("Connecting to WebSocket:", wsUrl)
      this.ws = new WebSocket(wsUrl)
      this.ws.onopen = () => console.log("WebSocket connected")
      
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
        } else if (data.type === 'message') {
          this.isTyping = false
          this.messages.push({ role: 'assistant', text: data.message });
          this.scrollToBottom();
        } else if(data.type === 'system') {
          console.log("System message:", data.message)
        } else if(data.type === 'error') {
          console.error("Error:", data.message)
        }
      }
      this.ws.onclose = () => console.log("WebSocket disconnected")
    },
    sendMessage() {
      this.isTyping = true
      if(!this.inputText.trim()) return
      this.messages.push({role:'user', text:this.inputText})
      this.scrollToBottom()
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
.chat-wrapper {
  width: 360px;
  max-width: 100%;
  height: 600px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.1);
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

.bot-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  background: #f9f9f9;
}

.bot-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #0b93f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 10px;
}

.bot-info h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}
.bot-info span {
  font-size: 12px;
  color: #666;
}

.messages {
  flex: 1;
  padding: 12px 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 16px;
  background: #f8f8f8;
}

.quick-actions button {
  padding: 8px 12px;
  border: 1px solid #0b93f6;
  border-radius: 12px;
  background: white;
  color: #0b93f6;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.quick-actions button:hover {
  background: #0b93f6;
  color: white;
}
.input-area {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 10px;
  background: #f5f5f7;
  border-top: 1px solid #e0e0e0;
}
.input-area {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 10px;
  background: #f5f5f7;
  border-top: 1px solid #e0e0e0;
}

.input-area input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 9999px; /* fully rounded like ChatGPT */
  border: none;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  font-size: 14px;
  color: #111;
  outline: none;
  transition: box-shadow 0.2s, background 0.2s;
}

.input-area input::placeholder {
  color: #aaa;
}

.input-area input:focus {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  background: #fff;
}

.input-area button {
  background: #0b93f6;
  padding: 10px 14px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.1s;
}

.input-area button:hover {
  background: #0a84e0;
  transform: scale(1.05);
}

.input-area .send-icon {
  width: 20px;
  height: 20px;
  stroke: #fff;
}
input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-size: 14px;
   color: #000;
}

button {
  padding: 10px 16px;
  border-radius: 16px;
  border: none;
  background: #0b93f6;
  color: white;
  cursor: pointer;
}
button:hover {
  background: #0a84e0;
}
</style>



