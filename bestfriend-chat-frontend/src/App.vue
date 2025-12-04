<template>
  <div class="h-screen w-screen">
    <ChatWindow />
  </div>
</template>

<script>
import ChatWindow from './components/chat/ChatWindow.vue'

export default {
  components: { ChatWindow }
}
</script>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
