/** 使用者自訂路線：手動排出來的多段轉乘組合，只存在 localStorage。 */
import { defineStore } from "pinia";

import type { CustomRoute, CustomRouteLeg } from "@/types";
import { loadFromStorage, saveToStorage } from "@/utils/storage";

const STORAGE_KEY = "movego:custom-routes";

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export const useCustomRoutesStore = defineStore("customRoutes", {
  state: () => ({
    items: loadFromStorage<CustomRoute[]>(STORAGE_KEY, [])
  }),
  getters: {
    byId: (state) => (id: string) => state.items.find((r) => r.id === id) ?? null
  },
  actions: {
    add(name: string, legs: CustomRouteLeg[]): CustomRoute {
      const route: CustomRoute = { id: makeId(), name, legs, createdAt: Date.now() };
      this.items.unshift(route);
      saveToStorage(STORAGE_KEY, this.items);
      return route;
    },
    update(id: string, name: string, legs: CustomRouteLeg[]) {
      const route = this.items.find((r) => r.id === id);
      if (!route) return;
      route.name = name;
      route.legs = legs;
      saveToStorage(STORAGE_KEY, this.items);
    },
    remove(id: string) {
      this.items = this.items.filter((r) => r.id !== id);
      saveToStorage(STORAGE_KEY, this.items);
    }
  }
});
