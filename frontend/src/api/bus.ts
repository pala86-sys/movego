import { apiGet } from "@/api/client";
import type { BusRoute, BusRouteSummary } from "@/types";

export function searchBusRoutes(keyword: string, signal?: AbortSignal): Promise<BusRouteSummary[]> {
  return apiGet<BusRouteSummary[]>(`/bus/search?keyword=${encodeURIComponent(keyword)}`, {
    signal
  });
}

export function fetchBusRoute(routeId: string): Promise<BusRoute> {
  return apiGet<BusRoute>(`/bus/${encodeURIComponent(routeId)}`);
}
