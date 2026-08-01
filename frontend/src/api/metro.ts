import { apiGet } from "@/api/client";
import type { MetroLine, MetroRoutePlan, MetroStationSearchItem } from "@/types";

export function fetchMetroLines(): Promise<MetroLine[]> {
  return apiGet<MetroLine[]>("/metro/lines");
}

export function searchMetroStations(keyword: string): Promise<MetroStationSearchItem[]> {
  return apiGet<MetroStationSearchItem[]>(`/metro/stations/search?keyword=${encodeURIComponent(keyword)}`);
}

export function planMetroRoute(from: string, to: string): Promise<MetroRoutePlan> {
  return apiGet<MetroRoutePlan>(`/metro/route?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`);
}

export interface MetroLiveboardEntry {
  destination: string;
  status: string;
}

export function fetchMetroLiveboard(station: string): Promise<MetroLiveboardEntry[]> {
  return apiGet<MetroLiveboardEntry[]>(`/metro/liveboard?station=${encodeURIComponent(station)}`);
}
