/** 站牌搜尋與附近站牌的狀態管理。 */
import { defineStore } from "pinia";

import { fetchNearbyStops, searchStops } from "@/api/stop";
import { ApiError } from "@/api/client";
import type { NearbyStop, StopSearchResult } from "@/types";

interface StopState {
  searchResults: StopSearchResult[];
  nearbyStops: NearbyStop[];
  loading: boolean;
  error: string | null;
}

export const useStopStore = defineStore("stop", {
  state: (): StopState => ({
    searchResults: [],
    nearbyStops: [],
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
        this.searchResults = await searchStops(keyword);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
      }
    },
    async loadNearby(lat?: number, lng?: number) {
      this.loading = true;
      this.error = null;
      try {
        this.nearbyStops = await fetchNearbyStops(lat, lng);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
      }
    }
  }
});
