import { apiGet } from "@/api/client";
import type { NearbyStop, StopSearchResult } from "@/types";

export function searchStops(keyword: string): Promise<StopSearchResult[]> {
  return apiGet<StopSearchResult[]>(`/stop/search?keyword=${encodeURIComponent(keyword)}`);
}

export function fetchNearbyStops(lat?: number, lng?: number): Promise<NearbyStop[]> {
  const query = lat != null && lng != null ? `?lat=${lat}&lng=${lng}` : "";
  return apiGet<NearbyStop[]>(`/stop/nearby${query}`);
}
