<script setup lang="ts">
import { computed } from "vue";

import { useSettingsStore } from "@/stores/settings";

interface NavItem {
  to: string;
  label: string;
  icon: string;
}

const settings = useSettingsStore();

// 首頁與設定一律顯示；其餘分頁看「設定」頁的勾選狀態
const items = computed<NavItem[]>(() => [
  { to: "/", label: "首頁", icon: "🏠" },
  ...(settings.flags.metro ? [{ to: "/metro", label: "捷運", icon: "🚇" }] : []),
  ...(settings.flags.bus ? [{ to: "/bus", label: "公車", icon: "🚌" }] : []),
  ...(settings.flags.nearby ? [{ to: "/nearby", label: "附近", icon: "📍" }] : []),
  ...(settings.flags.favorites ? [{ to: "/favorites", label: "收藏", icon: "⭐" }] : []),
  { to: "/settings", label: "設定", icon: "⚙️" }
]);
</script>

<template>
  <nav class="bottom-nav">
    <router-link
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="nav-item"
      active-class="nav-item-active"
      exact-active-class="nav-item-active"
    >
      <span class="nav-icon">{{ item.icon }}</span>
      <span class="nav-label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: calc(var(--nav-height) + var(--safe-bottom));
  padding-bottom: var(--safe-bottom);
  display: flex;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  z-index: 50;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--color-text-muted);
  min-height: 48px;
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
}

.nav-label {
  font-size: 12px;
  font-weight: 600;
}

.nav-item-active {
  color: var(--color-primary);
}
</style>
