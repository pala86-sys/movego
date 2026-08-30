/** 附近 YouBike 站點的狀態管理。 */
import { defineStore } from "pinia";

import { fetchNearbyBikeStations } from "@/api/bike";
import { ApiError } from "@/api/client";
import type { BikeStation } from "@/types";

// YouBike 查詢背後是獨立的一組 TDX 呼叫（站點+車況，北市/新北共 4 次），
// 跟附近站牌、附近停車場各自節流、互不影響，一樣要保護額度，所以自己也有 60 秒冷卻。
const MIN_INTERVAL_MS = 60000;

interface BikeState {
  stations: BikeStation[];
  loading: boolean;
  error: string | null;
  lastFetchAt: number | null;
}

export const useBikeStore = defineStore("bike", {
  state: (): BikeState => ({
    stations: [],
    loading: false,
    error: null,
    lastFetchAt: null
  }),
  actions: {
    async loadNearby(lat: number, lng: number) {
      const now = Date.now();
      if (this.lastFetchAt !== null && now - this.lastFetchAt < MIN_INTERVAL_MS) {
        return;
      }
      this.lastFetchAt = now;

      this.loading = true;
      this.error = null;
      try {
        this.stations = await fetchNearbyBikeStations(lat, lng);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
      }
    }
  }
});
