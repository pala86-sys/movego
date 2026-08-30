"""公共自行車（YouBike）相關的資料結構。"""
from pydantic import BaseModel


class BikeStation(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float
    capacity: int | None = None
    # 可借車輛：總數，以及一般車／電輔車拆開顯示（YouBike 2.0 才有拆分，缺值時為 None）
    available_rent: int | None = None
    available_rent_general: int | None = None
    available_rent_electric: int | None = None
    # 可還空位
    available_return: int | None = None
    status: str  # 正常 / 暫停營運 / 停止營運 / 無即時資料
    distance_meters: int | None = None
