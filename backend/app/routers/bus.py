"""公車相關 API 路由（僅負責 HTTP 進出，邏輯全部委派給 service 層）。"""
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.bus import BusRoute, BusRouteSummary
from app.services import bus_service
from app.services.tdx_client import TDXError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bus", tags=["bus"])


@router.get("/search", response_model=list[BusRouteSummary])
def search_routes(keyword: str = Query("", description="公車路線號碼關鍵字")):
    # 純讀本機資料庫，不會打 TDX，不需要特別處理 TDXError
    return bus_service.search_routes(keyword)


@router.get("/{route_id:path}", response_model=BusRoute)
async def get_route(route_id: str):
    try:
        route = await bus_service.get_route_detail(route_id)
    except TDXError as exc:
        logger.warning("TDX 公車路線詳情失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    if route is None:
        raise HTTPException(status_code=404, detail="找不到此公車路線")
    return route
