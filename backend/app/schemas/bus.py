"""公車相關的資料結構。"""
from pydantic import BaseModel


class BusStopArrival(BaseModel):
    stop_name: str
    status: str  # 進站中 / 約 X 分鐘 / 尚未發車 / 目前無法取得即時資料
    is_mock: bool = True


class BusDirection(BaseModel):
    direction: str
    from_: str
    to: str
    stops: list[BusStopArrival]

    class Config:
        populate_by_name = True


class BusRoute(BaseModel):
    id: str
    name: str
    operator: str
    outbound: BusDirection
    inbound: BusDirection


class BusRouteSummary(BaseModel):
    id: str
    name: str
    operator: str
    from_: str
    to: str
