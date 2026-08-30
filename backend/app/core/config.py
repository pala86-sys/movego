"""集中管理環境變數與設定，是全專案唯一讀取 .env 的地方。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tdx_client_id: str = ""
    tdx_client_secret: str = ""
    use_tdx: bool = False

    database_url: str = "sqlite:///./movego.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def tdx_enabled() -> bool:
    """是否啟用真實 TDX 串接。所有 service 一律透過這個函式判斷，不要各自讀 settings。

    未啟用時各功能的行為（刻意不一致，取決於有沒有模擬資料可退）：
    - 捷運／公車路線、站牌搜尋、附近站牌：回退到內建模擬資料，功能照常可用。
    - 捷運即時看板、附近停車場：回傳 None，代表「此功能需要 TDX，現在沒有」。
    """
    return get_settings().use_tdx
