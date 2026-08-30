/** 功能開關：使用者在「設定」頁勾選要顯示哪些功能，只存在 localStorage。
 *
 * 沒勾的功能：底部導覽分頁會消失、首頁對應的按鈕會隱藏、直接打網址進去也會被導回首頁
 * （見 router/index.ts 的 beforeEach）。
 */
import { defineStore } from "pinia";

import type { FeatureFlags } from "@/types";
import { loadFromStorage, saveToStorage } from "@/utils/storage";

const STORAGE_KEY = "movego:settings";

// 第一次使用（還沒動過設定）時的預設：原有功能全開，新加的 YouBike 預設關。
const DEFAULT_FLAGS: FeatureFlags = {
  metro: true,
  bus: true,
  nearby: true,
  favorites: true,
  customRoutes: true,
  nearbyParking: true,
  nearbyYoubike: false
};

function loadFlags(): FeatureFlags {
  // 用 spread 疊在預設上：之後新增的旗標，即使 localStorage 舊資料沒有，也會拿到預設值
  const saved = loadFromStorage<Partial<FeatureFlags>>(STORAGE_KEY, {});
  return { ...DEFAULT_FLAGS, ...saved };
}

export const useSettingsStore = defineStore("settings", {
  state: () => ({
    flags: loadFlags()
  }),
  actions: {
    set(key: keyof FeatureFlags, value: boolean) {
      this.flags[key] = value;
      saveToStorage(STORAGE_KEY, this.flags);
    },
    toggle(key: keyof FeatureFlags) {
      this.set(key, !this.flags[key]);
    }
  }
});
