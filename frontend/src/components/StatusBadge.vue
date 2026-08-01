<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status: string;
  showMockTag?: boolean;
}>();

const statusClass = computed(() => {
  if (props.status === "進站中") return "status-arriving";
  if (props.status.startsWith("約")) return "status-eta";
  if (props.status === "尚未發車") return "status-not-departed";
  return "status-text";
});
</script>

<template>
  <span class="status-wrap">
    <span :class="statusClass" class="status-text">{{ status }}</span>
    <span v-if="showMockTag" class="mock-tag">模擬資料</span>
  </span>
</template>

<style scoped>
.status-wrap {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}
</style>
