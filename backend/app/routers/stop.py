"""站牌相關 API 路由（僅負責 HTTP 進出，邏輯全部委派給 service 層）。"""
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.stop import NearbyStop, StopSearchResult
from app.services import stop_service
from app.services.tdx_client import TDXError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stop", tags=["stop"])


@router.get("/search", response_model=list[StopSearchResult])
def search_stop(keyword: str = Query("", description="站牌名稱關鍵字")):
    return stop_service.search_stop(keyword)


@router.get("/nearby", response_model=list[NearbyStop])
async def get_nearby(lat: float | None = None, lng: float | None = None):
    try:
        return await stop_service.get_nearby_stops(lat, lng)
    except TDXError as exc:
        logger.warning("TDX 附近站牌查詢失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
