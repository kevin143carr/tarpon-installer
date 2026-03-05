<script setup lang="ts">
import iniContent from '../../../example-ini-files/extensive_functionality_test_gui.ini?raw'
</script>

<template>
  <div class="ini-scroll-panel">
    <pre>{{ iniContent }}</pre>
  </div>
</template>

<style scoped>
.ini-scroll-panel {
  height: 45vh;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0.7rem 0.85rem;
  border-radius: 1rem;
  border: 1px solid rgba(148, 184, 207, 0.22);
  background: rgba(7, 17, 28, 0.96);
  box-shadow: 0 16px 36px rgba(4, 10, 18, 0.28);
  overscroll-behavior: contain;
}

.ini-scroll-panel pre {
  margin: 0;
  color: #edf4ff;
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.58rem;
  line-height: 1.34;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
