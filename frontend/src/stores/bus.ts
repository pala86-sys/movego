/** 公車頁籤的狀態管理。 */
import { defineStore } from "pinia";

import { fetchBusRoute, searchBusRoutes } from "@/api/bus";
import { ApiError } from "@/api/client";
import type { BusRoute, BusRouteSummary } from "@/types";

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
      this.loading = true;
      this.error = null;
      try {
        this.searchResults = await searchBusRoutes(keyword);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
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
