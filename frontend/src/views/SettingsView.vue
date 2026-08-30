<script setup lang="ts">
import { computed } from "vue";

import TopBar from "@/components/TopBar.vue";
import { useSettingsStore } from "@/stores/settings";
import type { FeatureFlags } from "@/types";

const settings = useSettingsStore();

interface Row {
  key: keyof FeatureFlags;
  label: string;
  desc: string;
  /** 只有在某個父旗標開啟時才有意義（例如「附近停車場」要「附近」開著才顯示） */
  requires?: keyof FeatureFlags;
}

const tabRows: Row[] = [
  { key: "metro", label: "捷運", desc: "捷運路線查詢、路線圖選站" },
  { key: "bus", label: "公車", desc: "公車路線號碼搜尋、沿途站牌" },
  { key: "nearby", label: "附近", desc: "用定位查詢附近的站牌" },
  { key: "favorites", label: "收藏", desc: "收藏的捷運站、公車路線、站牌" }
];

const nearbyRows: Row[] = [
  { key: "nearbyParking", label: "附近停車場", desc: "路外停車場即時剩餘車位", requires: "nearby" },
  {
    key: "nearbyYoubike",
    label: "附近 YouBike",
    desc: "YouBike 站點即時可借／可還",
    requires: "nearby"
  }
];

const otherRows: Row[] = [
  { key: "customRoutes", label: "自訂路線安排", desc: "手動排出自己知道的轉乘走法並存起來" }
];

function isDisabled(row: Row): boolean {
  return row.requires ? !settings.flags[row.requires] : false;
}

const nearbyOff = computed(() => !settings.flags.nearby);
</script>

<template>
  <div class="page">
    <TopBar title="設定" />

    <p class="intro">勾選要顯示的功能。沒勾的功能，相關按鈕與分頁都會隱藏，隨時可以再打開。</p>

    <div class="section-title" style="margin-top: 0">主要分頁</div>
    <div class="card">
      <label v-for="row in tabRows" :key="row.key" class="toggle-row">
        <span class="toggle-text">
          <span class="toggle-label">{{ row.label }}</span>
          <span class="toggle-desc">{{ row.desc }}</span>
        </span>
        <input
          type="checkbox"
          class="toggle-input"
          :checked="settings.flags[row.key]"
          @change="settings.set(row.key, ($event.target as HTMLInputElement).checked)"
        />
      </label>
    </div>

    <div class="section-title">附近頁的內容</div>
    <div class="card">
      <p v-if="nearbyOff" class="sub-hint">「附近」分頁關閉時，以下選項不會生效。</p>
      <label
        v-for="row in nearbyRows"
        :key="row.key"
        class="toggle-row"
        :class="{ 'toggle-row-disabled': isDisabled(row) }"
      >
        <span class="toggle-text">
          <span class="toggle-label">{{ row.label }}</span>
          <span class="toggle-desc">{{ row.desc }}</span>
        </span>
        <input
          type="checkbox"
          class="toggle-input"
          :disabled="isDisabled(row)"
          :checked="settings.flags[row.key]"
          @change="settings.set(row.key, ($event.target as HTMLInputElement).checked)"
        />
      </label>
    </div>

    <div class="section-title">其他</div>
    <div class="card">
      <label v-for="row in otherRows" :key="row.key" class="toggle-row">
        <span class="toggle-text">
          <span class="toggle-label">{{ row.label }}</span>
          <span class="toggle-desc">{{ row.desc }}</span>
        </span>
        <input
          type="checkbox"
          class="toggle-input"
          :checked="settings.flags[row.key]"
          @change="settings.set(row.key, ($event.target as HTMLInputElement).checked)"
        />
      </label>
    </div>
  </div>
</template>

<style scoped>
.intro {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 12px;
  line-height: 1.5;
}

.sub-hint {
  font-size: 13px;
  color: var(--color-warning);
  margin: 0 0 4px;
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  min-height: 44px;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
}

.toggle-row:last-child {
  border-bottom: none;
}

.toggle-row-disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.toggle-text {
  flex: 1;
  min-width: 0;
}

.toggle-label {
  display: block;
  font-weight: 700;
  font-size: 15px;
}

.toggle-desc {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.toggle-input {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  accent-color: var(--color-primary);
  cursor: inherit;
}
</style>
