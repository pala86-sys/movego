/** 捷運頁籤的狀態管理：呼叫 API 層、管理載入/錯誤狀態，UI 元件只讀取這裡的狀態。 */
import { defineStore } from "pinia";

import { fetchMetroLines, planMetroRoute, searchMetroStations } from "@/api/metro";
import { ApiError } from "@/api/client";
import type { MetroLine, MetroRoutePlan, MetroStationSearchItem } from "@/types";

interface MetroState {
  lines: MetroLine[];
  stationResults: MetroStationSearchItem[];
  routePlan: MetroRoutePlan | null;
  loading: boolean;
  error: string | null;
}

export const useMetroStore = defineStore("metro", {
  state: (): MetroState => ({
    lines: [],
    stationResults: [],
    routePlan: null,
    loading: false,
    error: null
  }),
  actions: {
    async loadLines() {
      if (this.lines.length > 0) return;
      try {
        this.lines = await fetchMetroLines();
      } catch {
        this.error = "目前無法取得即時資料";
      }
    },
    async searchStations(keyword: string) {
      if (!keyword.trim()) {
        this.stationResults = [];
        return;
      }
      try {
        this.stationResults = await searchMetroStations(keyword);
      } catch {
        this.stationResults = [];
        this.error = "目前無法取得即時資料";
      }
    },
    async planRoute(from: string, to: string) {
      this.loading = true;
      this.error = null;
      this.routePlan = null;
      try {
        this.routePlan = await planMetroRoute(from, to);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
      }
    },
    clearRoute() {
      this.routePlan = null;
      this.error = null;
    }
  }
});
