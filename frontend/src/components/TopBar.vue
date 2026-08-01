<script setup lang="ts">
import { useTheme } from "@/composables/useTheme";

defineProps<{ title: string }>();

const { theme, toggle } = useTheme();
</script>

<template>
  <header class="top-bar">
    <h1 class="page-title" style="margin: 0">{{ title }}</h1>
    <button class="theme-toggle" type="button" @click="toggle" aria-label="切換深色模式">
      {{ theme === "dark" ? "☀️" : "🌙" }}
    </button>
  </header>
</template>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.theme-toggle {
  min-width: 44px;
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: 18px;
  cursor: pointer;
}
</style>
