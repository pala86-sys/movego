/** 站牌搜尋與附近站牌的狀態管理。 */
import { defineStore } from "pinia";

import { fetchNearbyStops, searchStops } from "@/api/stop";
import { ApiError } from "@/api/client";
import type { NearbyStop, StopSearchResult } from "@/types";

// 附近站牌背後會同時打台北市/新北市公車與捷運共 4 支 TDX 請求，
// TDX 免費方案每分鐘只有 5 次額度，所以無論從哪裡觸發（首頁、附近頁、定位按鈕），
// 15 秒內最多只實際打一次，避免短時間內重複觸發把額度用光。
const NEARBY_MIN_INTERVAL_MS = 15000;

interface StopState {
  searchResults: StopSearchResult[];
  nearbyStops: NearbyStop[];
  loading: boolean;
  error: string | null;
  lastNearbyFetchAt: number | null;
}

export const useStopStore = defineStore("stop", {
  state: (): StopState => ({
    searchResults: [],
    nearbyStops: [],
    loading: false,
    error: null,
    lastNearbyFetchAt: null
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
      const now = Date.now();
      if (this.lastNearbyFetchAt !== null && now - this.lastNearbyFetchAt < NEARBY_MIN_INTERVAL_MS) {
        return; // 15 秒節流：沿用現有資料，不重打 API
      }
      this.lastNearbyFetchAt = now;

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
