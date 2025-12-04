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


<!-- <template>
  <div :class="wrapperClass">
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
        ? 'bg-blue-500 text-white rounded-lg p-2 self-end max-w-[70%] my-1'
        : 'bg-gray-200 text-black rounded-lg p-2 self-start max-w-[70%] my-1';
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

/* ChatGPT style bubbles */
.bubble {
  max-width: 75%;
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.bubble-user {
  background-color: #0b93f6;
  color: white;
}

.bubble-assistant {
  background-color: #f2f2f2;
  color: #111;
  border: 1px solid #e6e6e6;
}
</style> -->