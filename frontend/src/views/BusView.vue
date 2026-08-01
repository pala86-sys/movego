<script setup lang="ts">
import { ref } from "vue";

import FavoriteStar from "@/components/FavoriteStar.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import TopBar from "@/components/TopBar.vue";
import { useBusStore } from "@/stores/bus";
import { useRecentQueriesStore } from "@/stores/recentQueries";

const busStore = useBusStore();
const recentStore = useRecentQueriesStore();

const keyword = ref("");
const direction = ref<"outbound" | "inbound">("outbound");
const hasSearched = ref(false);

// 改成手動送出才查詢（按 Enter 或搜尋按鈕），而不是打字就搜，
// 避免打「611」的過程中「6」「61」「611」各自觸發一次 TDX 呼叫，浪費免費額度。
function onSearch() {
  if (!keyword.value.trim()) return;
  hasSearched.value = true;
  busStore.search(keyword.value);
}

async function openRoute(routeId: string) {
  await busStore.loadRoute(routeId);
  direction.value = "outbound";
  if (busStore.currentRoute) {
    recentStore.add("bus-route", busStore.currentRoute.id, `${busStore.currentRoute.name} 公車`);
  }
}

function back() {
  busStore.clearRoute();
}
</script>

<template>
  <div class="page">
    <TopBar title="公車路線查詢" />

    <template v-if="!busStore.currentRoute">
      <form class="search-row" @submit.prevent="onSearch">
        <input
          v-model="keyword"
          class="input"
          type="search"
          inputmode="search"
          placeholder="輸入公車號碼，例如 0100，按 Enter 搜尋"
        />
        <button class="btn" type="submit" :disabled="!keyword.trim()">搜尋</button>
      </form>

      <div v-if="busStore.loading" class="card" style="margin-top: 16px">
        <div class="empty-hint">查詢中…</div>
      </div>
      <div v-else-if="busStore.error" class="error-hint" style="margin-top: 16px">{{ busStore.error }}</div>
      <div v-else-if="!hasSearched" class="card" style="margin-top: 16px">
        <div class="empty-hint">輸入公車號碼後按 Enter 或搜尋按鈕開始查詢</div>
      </div>
      <div v-else-if="busStore.searchResults.length === 0" class="card" style="margin-top: 16px">
        <div class="empty-hint">找不到符合的公車路線</div>
      </div>
      <div v-else class="card" style="margin-top: 16px">
        <div v-for="route in busStore.searchResults" :key="route.id" class="list-item route-item" @click="openRoute(route.id)">
          <div>
            <div class="route-name">{{ route.name }}</div>
            <div class="route-sub">{{ route.from_ }} → {{ route.to }} ‧ {{ route.operator }}</div>
          </div>
          <span class="arrow">›</span>
        </div>
      </div>
    </template>

    <template v-else>
      <button class="btn btn-outline back-btn" type="button" @click="back">‹ 返回搜尋</button>

      <div class="card">
        <div class="route-header">
          <div>
            <div class="route-name-lg">{{ busStore.currentRoute.name }}</div>
            <div class="route-sub">{{ busStore.currentRoute.operator }}</div>
          </div>
          <FavoriteStar type="bus-route" :item-key="busStore.currentRoute.id" :label="busStore.currentRoute.name + ' 公車'" />
        </div>

        <div class="direction-tabs">
          <button
            class="direction-tab"
            :class="{ active: direction === 'outbound' }"
            type="button"
            @click="direction = 'outbound'"
          >
            去程 {{ busStore.currentRoute.outbound.from_ }} → {{ busStore.currentRoute.outbound.to }}
          </button>
          <button
            class="direction-tab"
            :class="{ active: direction === 'inbound' }"
            type="button"
            @click="direction = 'inbound'"
          >
            返程 {{ busStore.currentRoute.inbound.from_ }} → {{ busStore.currentRoute.inbound.to }}
          </button>
        </div>

        <div class="stop-list">
          <div
            v-for="stop in (direction === 'outbound' ? busStore.currentRoute.outbound : busStore.currentRoute.inbound).stops"
            :key="stop.stop_name"
            class="list-item"
          >
            <span>{{ stop.stop_name }}</span>
            <StatusBadge :status="stop.status" :show-mock-tag="stop.is_mock" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.search-row {
  display: flex;
  gap: 8px;
}

.search-row .input {
  flex: 1;
}

.search-row .btn {
  flex-shrink: 0;
  padding: 0 20px;
}

.route-item {
  cursor: pointer;
}

.route-name {
  font-weight: 700;
  font-size: 16px;
}

.route-name-lg {
  font-weight: 800;
  font-size: 22px;
}

.route-sub {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.arrow {
  color: var(--color-text-muted);
}

.back-btn {
  margin-bottom: 14px;
}

.route-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 14px;
}

.direction-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.direction-tab {
  flex: 1;
  min-height: 48px;
  border-radius: 12px;
  border: 1.5px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 13px;
  font-weight: 600;
  padding: 6px 8px;
  cursor: pointer;
}

.direction-tab.active {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
}

.stop-list {
  border-top: 1px solid var(--color-border);
  padding-top: 4px;
}
</style>
