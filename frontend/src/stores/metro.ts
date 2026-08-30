/** 捷運頁籤的狀態管理：呼叫 API 層、管理載入/錯誤狀態，UI 元件只讀取這裡的狀態。 */
import { defineStore } from "pinia";

import {
  fetchMetroLines,
  fetchMetroLiveboard,
  planMetroRoute,
  searchMetroStations
} from "@/api/metro";
import { ApiError, RequestAbortedError } from "@/api/client";
import type {
  MetroLine,
  MetroLiveboardEntry,
  MetroRoutePlan,
  MetroStationSearchItem
} from "@/types";

// 搜尋輸入會連續觸發，只保留最後一次請求：新的一次進來就取消還沒回來的舊請求。
let stationSearchAbort: AbortController | null = null;
let suggestAbort: AbortController | null = null;

interface MetroState {
  lines: MetroLine[];
  stationResults: MetroStationSearchItem[];
  routePlan: MetroRoutePlan | null;
  loading: boolean;
  error: string | null;
  liveboard: MetroLiveboardEntry[];
  liveboardLoading: boolean;
  liveboardError: string | null;
}

export const useMetroStore = defineStore("metro", {
  state: (): MetroState => ({
    lines: [],
    stationResults: [],
    routePlan: null,
    loading: false,
    error: null,
    liveboard: [],
    liveboardLoading: false,
    liveboardError: null
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
      stationSearchAbort?.abort();
      stationSearchAbort = new AbortController();
      try {
        this.stationResults = await searchMetroStations(keyword, stationSearchAbort.signal);
      } catch (err) {
        if (err instanceof RequestAbortedError) return;
        this.stationResults = [];
        this.error = "目前無法取得即時資料";
      }
    },
    /** 給需要「每個輸入欄各自一份建議清單」的畫面用：只回資料，不動共用狀態。 */
    async fetchStationSuggestions(keyword: string): Promise<MetroStationSearchItem[]> {
      if (!keyword.trim()) return [];
      suggestAbort?.abort();
      suggestAbort = new AbortController();
      try {
        return await searchMetroStations(keyword, suggestAbort.signal);
      } catch {
        // 被取消或查詢失敗都當作「沒有建議」，不影響使用者輸入
        return [];
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
    },
    async loadLiveboard(station: string) {
      this.liveboardLoading = true;
      this.liveboardError = null;
      this.liveboard = [];
      try {
        this.liveboard = await fetchMetroLiveboard(station);
      } catch (err) {
        this.liveboardError = err instanceof ApiError ? err.message : "目前無法取得即時資料";
      } finally {
        this.liveboardLoading = false;
      }
    }
  }
});
