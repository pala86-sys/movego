"""停車場相關 API 路由（僅負責 HTTP 進出，邏輯全部委派給 service 層）。"""
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.parking import ParkingLot
from app.services import parking_service
from app.services.tdx_client import TDXError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/parking", tags=["parking"])


@router.get("/nearby", response_model=list[ParkingLot])
async def get_nearby(lat: float = Query(...), lng: float = Query(...)):
    try:
        lots = await parking_service.get_nearby_parking_lots(lat, lng)
    except TDXError as exc:
        logger.warning("TDX 附近停車場查詢失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    if lots is None:
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    return lots
