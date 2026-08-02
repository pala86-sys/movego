"""停車場相關的資料結構。"""
from pydantic import BaseModel


class ParkingLot(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float
    total_spaces: int | None = None
    available_spaces: int | None = None
    status: str  # 正常 / 已滿 / 無即時資料
    distance_meters: int | None = None
