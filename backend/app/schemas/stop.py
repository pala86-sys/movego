"""站牌搜尋相關的資料結構。"""
from pydantic import BaseModel


class RouteAtStop(BaseModel):
    route_id: str
    route_name: str
    direction: str
    status: str


class StopSearchResult(BaseModel):
    stop_name: str
    routes: list[RouteAtStop]


class NearbyStop(BaseModel):
    id: str
    name: str
    type: str  # metro | bus
    lat: float
    lng: float
    lines: list[str] = []
    routes: list[str] = []
    distance_meters: int | None = None
