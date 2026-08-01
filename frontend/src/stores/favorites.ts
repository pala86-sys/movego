/** 收藏管理：捷運站、公車路線、站牌，第一版資料只存在 localStorage。 */
import { defineStore } from "pinia";

import type { FavoriteItem, FavoriteType } from "@/types";
import { loadFromStorage, saveToStorage } from "@/utils/storage";

const STORAGE_KEY = "movego:favorites";

function keyOf(type: FavoriteType, key: string): string {
  return `${type}:${key}`;
}

export const useFavoritesStore = defineStore("favorites", {
  state: () => ({
    items: loadFromStorage<FavoriteItem[]>(STORAGE_KEY, [])
  }),
  getters: {
    isFavorite: (state) => (type: FavoriteType, key: string) =>
      state.items.some((item) => keyOf(item.type, item.key) === keyOf(type, key)),
    byType: (state) => (type: FavoriteType) =>
      state.items.filter((item) => item.type === type).sort((a, b) => b.addedAt - a.addedAt)
  },
  actions: {
    toggle(type: FavoriteType, key: string, label: string) {
      const exists = this.items.find((item) => keyOf(item.type, item.key) === keyOf(type, key));
      if (exists) {
        this.items = this.items.filter((item) => item !== exists);
      } else {
        this.items.push({ type, key, label, addedAt: Date.now() });
      }
      saveToStorage(STORAGE_KEY, this.items);
    },
    remove(type: FavoriteType, key: string) {
      this.items = this.items.filter((item) => keyOf(item.type, item.key) !== keyOf(type, key));
      saveToStorage(STORAGE_KEY, this.items);
    }
  }
});
