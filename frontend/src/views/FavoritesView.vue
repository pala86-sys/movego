<script setup lang="ts">
import { useRouter } from "vue-router";

import TopBar from "@/components/TopBar.vue";
import { useFavoritesStore } from "@/stores/favorites";
import type { FavoriteItem } from "@/types";

const favoritesStore = useFavoritesStore();
const router = useRouter();

function open(item: FavoriteItem) {
  if (item.type === "metro-station") router.push({ path: "/metro", query: { to: item.key } });
  else if (item.type === "bus-route") router.push("/bus");
  else router.push({ path: "/stop/" + encodeURIComponent(item.key) });
}

function remove(item: FavoriteItem, event: Event) {
  event.stopPropagation();
  favoritesStore.remove(item.type, item.key);
}

const groups: { type: FavoriteItem["type"]; label: string }[] = [
  { type: "metro-station", label: "捷運站" },
  { type: "bus-route", label: "公車路線" },
  { type: "stop", label: "站牌" }
];
</script>

<template>
  <div class="page">
    <TopBar title="我的收藏" />

    <template v-if="favoritesStore.items.length === 0">
      <div class="card"><div class="empty-hint">尚未收藏任何捷運站、公車路線或站牌</div></div>
    </template>

    <template v-else>
      <template v-for="group in groups" :key="group.type">
        <template v-if="favoritesStore.byType(group.type).length > 0">
          <div class="section-title">{{ group.label }}</div>
          <div class="card">
            <div v-for="item in favoritesStore.byType(group.type)" :key="item.key" class="list-item" @click="open(item)">
              <span>⭐ {{ item.label }}</span>
              <button class="remove-btn" type="button" @click="remove(item, $event)" aria-label="移除收藏">✕</button>
            </div>
          </div>
        </template>
      </template>
    </template>
  </div>
</template>

<style scoped>
.remove-btn {
  min-width: 44px;
  min-height: 44px;
  border: none;
  background: none;
  color: var(--color-text-muted);
  font-size: 16px;
  cursor: pointer;
}
</style>
