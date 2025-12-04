 <template>
  <div :class="['message-row', message.role]">
    <div :class="bubbleClass">
      <p>{{ message.text }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "MessageBubble",
  props: {
    message: { type: Object, required: true } // {role: 'user'|'assistant', text: '...'}
  },
  computed: {
    bubbleClass() {
      return this.message.role === 'user'
        ? 'bubble bubble-user'
        : 'bubble bubble-assistant';
    }
  }
}
</script>

<style scoped>
.message-row {
  display: flex;
  width: 100%;
  margin: 6px 0;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

/* Chat bubble style */
.bubble {
  max-width: 75%;
  padding: 12px 16px;
  font-size: 15px;
  line-height: 1.5;
  white-space: pre-wrap;
  border-radius: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* User bubble */
.bubble-user {
  background-color: #0b93f6;
  color: white;
  border-bottom-right-radius: 4px; /* subtle ChatGPT style */
}

/* Assistant bubble */
.bubble-assistant {
  background-color: #f9f9f9;
  color: #111;
  border: 1px solid #e6e6e6;
  border-bottom-left-radius: 4px; /* subtle tail effect */
}
</style>


