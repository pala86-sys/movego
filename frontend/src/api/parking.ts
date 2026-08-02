import { apiGet } from "@/api/client";
import type { ParkingLot } from "@/types";

export function fetchNearbyParkingLots(lat: number, lng: number): Promise<ParkingLot[]> {
  return apiGet<ParkingLot[]>(`/parking/nearby?lat=${lat}&lng=${lng}`);
}
