"""站牌相關 API 路由。"""
from fastapi import APIRouter, Query

from app.schemas.stop import NearbyStop, StopSearchResult
from app.services import stop_service

router = APIRouter(prefix="/api/stop", tags=["stop"])


@router.get("/search", response_model=list[StopSearchResult])
def search_stop(keyword: str = Query("", description="站牌名稱關鍵字")):
    return stop_service.search_stop(keyword)


@router.get("/nearby", response_model=list[NearbyStop])
def get_nearby(lat: float | None = None, lng: float | None = None):
    # 第一版使用模擬附近站牌清單，lat/lng 保留供未來接入真實距離計算
    return stop_service.get_nearby_stops()
