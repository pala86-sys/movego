<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import TopBar from "@/components/TopBar.vue";
import { debounce } from "@/composables/useDebouncedRef";
import { useMetroStore } from "@/stores/metro";
import { useStopStore } from "@/stores/stop";
import { useFavoritesStore } from "@/stores/favorites";
import { useRecentQueriesStore } from "@/stores/recentQueries";

const router = useRouter();
const metroStore = useMetroStore();
const stopStore = useStopStore();
const favoritesStore = useFavoritesStore();
const recentStore = useRecentQueriesStore();

const keyword = ref("");
const searched = ref(false);

const runSearch = debounce(async (value: string) => {
  if (!value.trim()) {
    searched.value = false;
    return;
  }
  searched.value = true;
  await Promise.all([metroStore.searchStations(value), stopStore.search(value)]);
}, 300);

function onInput() {
  runSearch(keyword.value);
}

function goToStation(name: string) {
  recentStore.add("metro-station", name, name);
  router.push({ path: "/metro", query: { to: name } });
}

function goToStop(name: string) {
  recentStore.add("stop", name, name);
  router.push({ path: "/stop/" + encodeURIComponent(name) });
}

const favoritePreview = computed(() => favoritesStore.items.slice(0, 6));
const recentPreview = computed(() => recentStore.items.slice(0, 6));

function openRecent(item: (typeof recentStore.items)[number]) {
  if (item.type === "metro-station") goToStation(item.key);
  else if (item.type === "stop") goToStop(item.key);
  else router.push("/bus");
}
</script>

<template>
  <div class="page">
    <TopBar title="大台北即時交通查詢" />

    <div class="search-box">
      <input
        v-model="keyword"
        class="input"
        type="search"
        inputmode="search"
        placeholder="搜尋捷運站、站牌名稱"
        @input="onInput"
      />
    </div>

    <div class="quick-tabs">
      <router-link to="/metro" class="quick-tab">🚇 捷運路線</router-link>
      <router-link to="/bus" class="quick-tab">🚌 公車號碼</router-link>
      <router-link to="/nearby" class="quick-tab">📍 附近站牌</router-link>
    </div>

    <template v-if="searched">
      <div class="section-title">搜尋結果</div>
      <div class="card" v-if="metroStore.stationResults.length === 0 && stopStore.searchResults.length === 0">
        <div class="empty-hint">找不到符合的捷運站或站牌</div>
      </div>
      <div class="card" v-else>
        <div
          v-for="item in metroStore.stationResults"
          :key="'m-' + item.name"
          class="list-item result-item"
          @click="goToStation(item.name)"
        >
          <span>🚇 {{ item.name }}</span>
          <span class="arrow">›</span>
        </div>
        <div
          v-for="item in stopStore.searchResults"
          :key="'s-' + item.stop_name"
          class="list-item result-item"
          @click="goToStop(item.stop_name)"
        >
          <span>🚌 {{ item.stop_name }}</span>
          <span class="arrow">›</span>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="section-title">附近站牌</div>
      <div class="card">
        <router-link to="/nearby" class="see-more" style="padding: 4px 0">📍 查看附近站牌 ›</router-link>
      </div>

      <div class="section-title">常用收藏</div>
      <div class="card">
        <div v-if="favoritePreview.length === 0" class="empty-hint">尚未收藏任何路線或站牌</div>
        <div v-for="item in favoritePreview" :key="item.type + item.key" class="list-item">
          <span>⭐ {{ item.label }}</span>
        </div>
        <router-link v-if="favoritePreview.length > 0" to="/favorites" class="see-more">查看全部收藏 ›</router-link>
      </div>

      <div class="section-title">最近查詢</div>
      <div class="card">
        <div v-if="recentPreview.length === 0" class="empty-hint">尚無查詢紀錄</div>
        <div v-for="item in recentPreview" :key="item.type + item.key" class="list-item" @click="openRecent(item)">
          <span>{{ item.label }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.quick-tabs {
  display: flex;
  gap: 10px;
  margin: 16px 0 6px;
}

.quick-tab {
  flex: 1;
  min-height: 48px;
  border-radius: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  text-align: center;
  padding: 0 6px;
}

.result-item {
  cursor: pointer;
}

.arrow {
  color: var(--color-text-muted);
}

.see-more {
  display: block;
  text-align: center;
  padding: 10px 0 2px;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 14px;
}
</style>
