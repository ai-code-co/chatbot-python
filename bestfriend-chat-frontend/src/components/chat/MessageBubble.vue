<template>
  <div :class="bubbleClass">
    <p class="break-words">{{ message.text }}</p>
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
</style>
