export interface MetroStation {
  id: string;
  name: string;
}

export interface MetroLine {
  id: string;
  name: string;
  color: string;
  stations: MetroStation[];
}

export interface MetroStationSearchItem {
  name: string;
  line_ids: string[];
}

export interface MetroRouteLeg {
  line_id: string;
  line_name: string;
  line_color: string;
  board_station: string;
  alight_station: string;
  stop_count: number;
}

export interface MetroRoutePlan {
  from_station: string;
  to_station: string;
  legs: MetroRouteLeg[];
  transfer_count: number;
  total_stop_count: number;
  estimated_minutes: number;
}

export interface MetroLiveboardEntry {
  destination: string;
  status: string;
}

export interface BusStopArrival {
  stop_name: string;
  status: string;
  is_mock: boolean;
}

export interface BusDirection {
  direction: string;
  from_: string;
  to: string;
  stops: BusStopArrival[];
}

export interface BusRoute {
  id: string;
  name: string;
  operator: string;
  outbound: BusDirection;
  inbound: BusDirection;
}

export interface BusRouteSummary {
  id: string;
  name: string;
  operator: string;
  from_: string;
  to: string;
}

export interface RouteAtStop {
  route_id: string;
  route_name: string;
  direction: string;
  status: string;
}

export interface StopSearchResult {
  stop_name: string;
  routes: RouteAtStop[];
}

export interface NearbyStop {
  id: string;
  name: string;
  type: "metro" | "bus";
  lat: number;
  lng: number;
  lines: string[];
  routes: string[];
  distance_meters: number | null;
}

export interface ParkingLot {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  total_spaces: number | null;
  available_spaces: number | null;
  status: string;
  distance_meters: number | null;
}

export interface BikeStation {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  capacity: number | null;
  available_rent: number | null;
  available_rent_general: number | null;
  available_rent_electric: number | null;
  available_return: number | null;
  status: string;
  distance_meters: number | null;
}

/** 使用者在「設定」頁勾選要不要顯示的功能。未勾選的功能，相關按鈕與分頁都會隱藏。 */
export interface FeatureFlags {
  metro: boolean;
  bus: boolean;
  nearby: boolean;
  favorites: boolean;
  customRoutes: boolean;
  nearbyParking: boolean;
  nearbyYoubike: boolean;
}

export type FavoriteType = "metro-station" | "bus-route" | "stop";

export interface FavoriteItem {
  type: FavoriteType;
  key: string;
  label: string;
  addedAt: number;
}

export interface RecentQuery {
  type: FavoriteType;
  key: string;
  label: string;
  queriedAt: number;
  /** 捷運路線查詢時的起點站名；只有 type 為 metro-station 且來自完整路線查詢時才會有值 */
  fromKey?: string;
}

/** 使用者手動排出來的一段路（例如自己知道的抄近路轉乘方式），不是系統算出來的。 */
export interface CustomRouteLeg {
  lineId: string;
  lineName: string;
  lineColor: string;
  from: string;
  to: string;
}

export interface CustomRoute {
  id: string;
  name: string;
  legs: CustomRouteLeg[];
  createdAt: number;
}
