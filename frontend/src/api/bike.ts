import { apiGet } from "@/api/client";
import type { BikeStation } from "@/types";

export function fetchNearbyBikeStations(lat: number, lng: number): Promise<BikeStation[]> {
  return apiGet<BikeStation[]>(`/bike/nearby?lat=${lat}&lng=${lng}`);
}
