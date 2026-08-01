"""SQLite 資料表定義：捷運站、公車路線與附近站牌的參考資料（來源資料見 app/data/*.json）。"""
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class MetroLineModel(Base):
    __tablename__ = "metro_lines"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    color: Mapped[str] = mapped_column(String)

    stations: Mapped[list["MetroStationModel"]] = relationship(
        back_populates="line", order_by="MetroStationModel.seq", cascade="all, delete-orphan"
    )


class MetroStationModel(Base):
    __tablename__ = "metro_stations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    line_id: Mapped[str] = mapped_column(ForeignKey("metro_lines.id"))
    station_code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    seq: Mapped[int] = mapped_column()

    line: Mapped[MetroLineModel] = relationship(back_populates="stations")


class BusRouteModel(Base):
    __tablename__ = "bus_routes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    operator: Mapped[str] = mapped_column(String)
    # 模擬資料沒有城市概念留空即可；TDX 同步進來的資料會填 Taipei/NewTaipei，
    # 查即時到站狀態時需要靠這個欄位決定要打哪個 City 的 TDX API。
    city: Mapped[str] = mapped_column(String, default="")

    stops: Mapped[list["BusRouteStopModel"]] = relationship(
        back_populates="route", order_by="BusRouteStopModel.seq", cascade="all, delete-orphan"
    )


class BusRouteStopModel(Base):
    __tablename__ = "bus_route_stops"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[str] = mapped_column(ForeignKey("bus_routes.id"))
    direction: Mapped[str] = mapped_column(String)  # outbound | inbound
    direction_label: Mapped[str] = mapped_column(String)  # 去程 | 返程
    from_name: Mapped[str] = mapped_column(String)
    to_name: Mapped[str] = mapped_column(String)
    seq: Mapped[int] = mapped_column()
    stop_name: Mapped[str] = mapped_column(String)
    # TDX 站牌唯一識別碼，只有 TDX 同步資料才有值，用來對應即時到站 API 的回傳
    stop_uid: Mapped[str] = mapped_column(String, default="")

    route: Mapped[BusRouteModel] = relationship(back_populates="stops")


class NearbyStopModel(Base):
    __tablename__ = "nearby_stops"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)  # metro | bus
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    lines_csv: Mapped[str] = mapped_column(String, default="")
    routes_csv: Mapped[str] = mapped_column(String, default="")
