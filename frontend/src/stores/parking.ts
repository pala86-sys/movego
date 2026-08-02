/** 附近停車場的狀態管理。 */
import { defineStore } from "pinia";

import { fetchNearbyParkingLots } from "@/api/parking";
import { ApiError } from "@/api/client";
import type { ParkingLot } from "@/types";

// 停車場查詢背後是獨立的一組 TDX 呼叫（基本資料+剩餘車位，共 2 次），
// 跟附近站牌各自節流、互不影響，但一樣要保護額度，所以自己也有 60 秒冷卻。
const MIN_INTERVAL_MS = 60000;

interface ParkingState {
  lots: ParkingLot[];
  loading: boolean;
  error: string | null;
  lastFetchAt: number | null;
}

export const useParkingStore = defineStore("parking", {
  state: (): ParkingState => ({
    lots: [],
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
        this.lots = await fetchNearbyParkingLots(lat, lng);
      } catch (err) {
        this.error = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.loading = false;
      }
    }
  }
});
