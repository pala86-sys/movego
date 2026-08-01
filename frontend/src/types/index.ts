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
}
