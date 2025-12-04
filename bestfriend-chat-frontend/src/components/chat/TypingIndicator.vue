<template>
  <div class="typing-indicator self-start text-gray-500 text-sm">
    Aira is typing<span v-for="n in dots" :key="n">.</span>
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
