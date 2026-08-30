"""FastAPI 進入點：組裝設定、CORS 與路由，不含任何商業邏輯。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed_if_empty
from app.routers import bus, metro, parking, stop
from app.services.tdx_bus_sync import sync_bus_routes_if_needed
from app.services.tdx_client import close_client

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
        if settings.use_tdx:
            await sync_bus_routes_if_needed(db)
    yield
    await close_client()


app = FastAPI(
    title="大台北即時交通查詢 API",
    description="捷運、公車、站牌與到站查詢服務；即時資料由 TDX 提供（USE_TDX=true 時），"
    "否則回傳內建模擬資料。",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # 前端只用不帶 cookie 的 fetch，不需要 credentials
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(metro.router)
app.include_router(bus.router)
app.include_router(stop.router)
app.include_router(parking.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "use_tdx": settings.use_tdx}
