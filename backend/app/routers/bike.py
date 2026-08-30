"""YouBike 相關 API 路由（僅負責 HTTP 進出，邏輯全部委派給 service 層）。"""
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.bike import BikeStation
from app.services import bike_service
from app.services.tdx_client import TDXError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bike", tags=["bike"])


@router.get("/nearby", response_model=list[BikeStation])
async def get_nearby(lat: float = Query(...), lng: float = Query(...)):
    try:
        stations = await bike_service.get_nearby_bike_stations(lat, lng)
    except TDXError as exc:
        logger.warning("TDX 附近 YouBike 查詢失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    if stations is None:
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    return stations
