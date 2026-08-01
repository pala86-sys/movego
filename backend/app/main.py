"""FastAPI 進入點：組裝設定、CORS 與路由，不含任何商業邏輯。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed_if_empty
from app.routers import bus, metro, stop

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_if_empty(db)
    yield


app = FastAPI(
    title="大台北即時交通查詢 API",
    description="捷運、公車、站牌查詢服務（第一版使用模擬到站資料，尚未串接 TDX）",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metro.router)
app.include_router(bus.router)
app.include_router(stop.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "use_tdx": settings.use_tdx}
