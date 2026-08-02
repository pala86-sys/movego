/** 最近查詢紀錄：讓首頁在離線狀態下也能顯示過去查過的項目。 */
import { defineStore } from "pinia";

import type { FavoriteType, RecentQuery } from "@/types";
import { loadFromStorage, saveToStorage } from "@/utils/storage";

const STORAGE_KEY = "movego:recent-queries";
const MAX_ITEMS = 10;

export const useRecentQueriesStore = defineStore("recentQueries", {
  state: () => ({
    items: loadFromStorage<RecentQuery[]>(STORAGE_KEY, [])
  }),
  actions: {
    add(type: FavoriteType, key: string, label: string, fromKey?: string) {
      const filtered = this.items.filter((item) => !(item.type === type && item.key === key));
      filtered.unshift({ type, key, label, queriedAt: Date.now(), fromKey });
      this.items = filtered.slice(0, MAX_ITEMS);
      saveToStorage(STORAGE_KEY, this.items);
    },
    clear() {
      this.items = [];
      saveToStorage(STORAGE_KEY, this.items);
    }
  }
});
