/** 公車頁籤的狀態管理。 */
import { defineStore } from "pinia";

import { fetchBusRoute, searchBusRoutes } from "@/api/bus";
import { ApiError, RequestAbortedError } from "@/api/client";
import type { BusRoute, BusRouteSummary } from "@/types";

// 只保留最後一次搜尋：新輸入進來就取消還沒回來的舊請求
let searchAbort: AbortController | null = null;

interface BusState {
  searchResults: BusRouteSummary[];
  currentRoute: BusRoute | null;
  loading: boolean;
  error: string | null;
}

export const useBusStore = defineStore("bus", {
  state: (): BusState => ({
    searchResults: [],
    currentRoute: null,
    loading: false,
    error: null
  }),
  actions: {
    async search(keyword: string) {
      if (!keyword.trim()) {
        this.searchResults = [];
        return;
      }
      searchAbort?.abort();
      const controller = new AbortController();
      searchAbort = controller;
      this.loading = true;
      this.error = null;
      try {
        this.searchResults = await searchBusRoutes(keyword, controller.signal);
      } catch (err) {
        if (err instanceof RequestAbortedError) return;
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        // 只有「最新那次」搜尋能收掉 loading；被取代的舊請求不要動它
        if (searchAbort === controller) this.loading = false;
      }
    },
    async loadRoute(routeId: string) {
      this.loading = true;
      this.error = null;
      this.currentRoute = null;
      try {
        this.currentRoute = await fetchBusRoute(routeId);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
      }
    },
    clearRoute() {
      this.currentRoute = null;
      this.error = null;
    }
  }
});
