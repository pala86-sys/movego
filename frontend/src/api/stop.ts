import { apiGet } from "@/api/client";
import type { NearbyStop, StopSearchResult } from "@/types";

export function searchStops(keyword: string, signal?: AbortSignal): Promise<StopSearchResult[]> {
  return apiGet<StopSearchResult[]>(`/stop/search?keyword=${encodeURIComponent(keyword)}`, {
    signal
  });
}

export function fetchNearbyStops(lat?: number, lng?: number): Promise<NearbyStop[]> {
  const query = lat != null && lng != null ? `?lat=${lat}&lng=${lng}` : "";
  return apiGet<NearbyStop[]>(`/stop/nearby${query}`);
}
