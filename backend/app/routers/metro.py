"""捷運相關 API 路由（僅負責 HTTP 進出，邏輯全部委派給 service 層）。"""
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.metro import MetroLine, MetroRoutePlan
from app.services import metro_service
from app.services.tdx_client import TDXError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/metro", tags=["metro"])


@router.get("/lines", response_model=list[MetroLine])
async def list_lines():
    try:
        return await metro_service.get_all_lines()
    except TDXError as exc:
        logger.warning("TDX 捷運路線清單失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")


@router.get("/stations/search")
async def search_stations(keyword: str = Query("", description="站名關鍵字")):
    try:
        return await metro_service.search_stations(keyword)
    except TDXError as exc:
        logger.warning("TDX 捷運站名搜尋失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")


@router.get("/route", response_model=MetroRoutePlan)
async def plan_route(
    from_station: str = Query(..., alias="from"),
    to_station: str = Query(..., alias="to"),
):
    try:
        plan = await metro_service.plan_route(from_station, to_station)
    except TDXError as exc:
        logger.warning("TDX 捷運路線規劃失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    if plan is None:
        raise HTTPException(status_code=404, detail="找不到路線，請確認起訖站名稱")
    return plan


@router.get("/liveboard")
async def get_liveboard(station: str = Query(..., description="捷運站名")):
    try:
        board = await metro_service.get_liveboard(station)
    except TDXError as exc:
        logger.warning("TDX 捷運即時看板失敗：%s", exc)
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    if board is None:
        raise HTTPException(status_code=503, detail="目前無法取得即時資料")
    return board
