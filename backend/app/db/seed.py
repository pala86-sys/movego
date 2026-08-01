"""將 app/data 下的模擬 JSON 資料匯入 SQLite（僅在資料表為空時執行一次）。"""
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import BusRouteModel, BusRouteStopModel, MetroLineModel, MetroStationModel, NearbyStopModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str):
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def seed_if_empty(db: Session) -> None:
    if db.query(MetroLineModel).first() is None:
        for line in _load_json("metro_lines.json"):
            line_model = MetroLineModel(id=line["id"], name=line["name"], color=line["color"])
            for seq, station in enumerate(line["stations"]):
                line_model.stations.append(
                    MetroStationModel(station_code=station["id"], name=station["name"], seq=seq)
                )
            db.add(line_model)

    if db.query(BusRouteModel).first() is None:
        for route in _load_json("bus_routes.json"):
            route_model = BusRouteModel(id=route["id"], name=route["name"], operator=route["operator"])
            for direction_key, direction_label in (("outbound", "去程"), ("inbound", "返程")):
                direction = route[direction_key]
                for seq, stop_name in enumerate(direction["stops"]):
                    route_model.stops.append(
                        BusRouteStopModel(
                            direction=direction_key,
                            direction_label=direction_label,
                            from_name=direction["from"],
                            to_name=direction["to"],
                            seq=seq,
                            stop_name=stop_name,
                        )
                    )
            db.add(route_model)

    if db.query(NearbyStopModel).first() is None:
        for stop in _load_json("nearby_stops.json"):
            db.add(
                NearbyStopModel(
                    id=stop["id"],
                    name=stop["name"],
                    type=stop["type"],
                    lat=stop["lat"],
                    lng=stop["lng"],
                    lines_csv=",".join(stop.get("lines", [])),
                    routes_csv=",".join(stop.get("routes", [])),
                )
            )

    db.commit()
