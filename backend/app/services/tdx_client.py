"""TDX（運輸資料流通服務）API 用戶端：處理 OAuth2 認證與快取，並提供通用 GET 方法。

金鑰只會從 app.core.config（也就是後端 .env）讀取，前端完全不會接觸到。
"""
import time

import httpx

from app.core.config import get_settings

AUTH_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
API_BASE = "https://tdx.transportdata.tw/api/basic"


class TDXError(Exception):
    """TDX 認證或 API 呼叫失敗時拋出，由呼叫端轉換成「目前無法取得即時資料」。"""


# 單一共用的 AsyncClient：重用連線池與 TLS 連線，避免每次呼叫都重新握手。
# 由 app.main 的 lifespan 在關閉時呼叫 close_client() 收掉。
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=10)
    return _client


async def close_client() -> None:
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None


class _TokenCache:
    access_token: str | None = None
    expires_at: float = 0.0


_token_cache = _TokenCache()


async def _get_access_token() -> str:
    settings = get_settings()
    if not settings.tdx_client_id or not settings.tdx_client_secret:
        raise TDXError("尚未設定 TDX_CLIENT_ID / TDX_CLIENT_SECRET")

    now = time.time()
    if _token_cache.access_token and now < _token_cache.expires_at:
        return _token_cache.access_token

    try:
        response = await _get_client().post(
            AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.tdx_client_id,
                "client_secret": settings.tdx_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise TDXError(f"TDX 認證失敗：{exc}") from exc

    token = payload.get("access_token")
    expires_in = payload.get("expires_in", 3600)
    if not token:
        raise TDXError("TDX 認證回應缺少 access_token")

    _token_cache.access_token = token
    # 提前 60 秒視為過期，避免臨界時間送出即將失效的 token
    _token_cache.expires_at = now + max(expires_in - 60, 60)
    return token


async def tdx_get(path: str, params: dict | None = None) -> list | dict:
    """呼叫 TDX Basic API，例如 path='/v2/Bus/Route/City/Taipei'。回傳已解析的 JSON。"""
    token = await _get_access_token()
    query = dict(params or {})
    query.setdefault("$format", "JSON")

    try:
        response = await _get_client().get(
            f"{API_BASE}{path}",
            params=query,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        raise TDXError(f"TDX API 呼叫失敗：{path} ({exc})") from exc
