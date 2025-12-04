<template>
  <div class="typing-wrap">
    <div class="dot" v-for="n in dots" :key="n"></div>
  </div>
</template>


<script>
export default {
  name: "TypingIndicator",
  props: {
    active: { type: Boolean, default: false }
  },
  data() {
    return { dots: 0, intervalId: null };
  },
  watch: {
    active(newVal) {
      if (newVal) this.startDots();
      else this.stopDots();
    }
  },
  methods: {
    startDots() {
      this.intervalId = setInterval(() => {
        this.dots = (this.dots + 1) % 4;
      }, 500);
    },
    stopDots() {
      clearInterval(this.intervalId);
      this.dots = 0;
    }
  },
  unmounted() {
    this.stopDots();
  }
}
</script>


<style scoped>
.typing-wrap {
  display: flex;
  gap: 5px;
  padding: 10px;
  background: #f2f2f2;
  width: fit-content;
  border-radius: 12px;
  border: 1px solid #e6e6e6;
  margin: 6px 0;
}

.dot {
  width: 8px;
  height: 8px;
  background: #c7c7c7;
  border-radius: 50%;
  animation: blink 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes blink {
  0%, 80%, 100% { opacity: .2; }
  40% { opacity: 1; }
}
</style>