<template>
 
  <div class="app-background h-screen w-screen">
    <ChatWindow class="chat-window-fixed" />
  </div>
</template>

<script>
import ChatWindow from './components/chat/ChatWindow.vue'

export default {
  components: { ChatWindow }
}
</script>
<style scoped>
.app-background {
  /* Fullscreen background */
  background-image: url('https://wp.sfdcdigital.com/en-us/wp-content/uploads/sites/4/2025/03/marquee-agentforce-ai-chatbot.png');
  background-size: cover;        /* Cover entire div */
  background-position: center;   /* Center the image */
  background-repeat: no-repeat;  /* Do not repeat */
  display: flex;                 /* For ChatWindow centering if needed */
  justify-content: center;
  align-items: center;
}
/* Fix ChatWindow in bottom-right */
.chat-window-fixed {
  position: fixed;     /* Stay fixed on screen */
  bottom: 2rem;        /* 32px space from bottom */
  right: 2rem;         /* 32px space from right */
  max-width: 400px;    /* Optional: control width */
  width: 100%;
  z-index: 50;         /* Stay above background */
}
</style>

