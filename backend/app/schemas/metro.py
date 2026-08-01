"""捷運相關的資料結構（API 輸入輸出格式）。"""
from pydantic import BaseModel


class MetroStation(BaseModel):
    id: str
    name: str


class MetroLine(BaseModel):
    id: str
    name: str
    color: str
    stations: list[MetroStation]


class MetroRouteLeg(BaseModel):
    line_id: str
    line_name: str
    line_color: str
    board_station: str
    alight_station: str
    stop_count: int


class MetroRoutePlan(BaseModel):
    from_station: str
    to_station: str
    legs: list[MetroRouteLeg]
    transfer_count: int
    total_stop_count: int
    estimated_minutes: int
