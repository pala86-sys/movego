# 大台北即時交通查詢 PWA

手機優先的大台北捷運／公車／站牌查詢工具，可安裝成 PWA（加入 Android／iPhone 主畫面）。
**第一版使用模擬到站資料，尚未串接 TDX 即時資料。**

## 專案資料夾架構

```
MoveGo/
├── README.md
├── .gitignore
├── scripts/
│   └── gen_icons.py          # 產生開發用 PWA 圖示（純 stdlib，不依賴 Pillow）
│
├── backend/                  # FastAPI 後端
│   ├── requirements.txt
│   ├── .env.example          # TDX 金鑰設定範例（實際 .env 不會被提交）
│   └── app/
│       ├── main.py           # FastAPI 進入點，組裝 CORS 與路由
│       ├── core/
│       │   └── config.py     # 讀取 .env 的唯一入口
│       ├── db/
│       │   ├── database.py   # SQLite 連線設定
│       │   ├── models.py     # SQLAlchemy 資料表
│       │   └── seed.py       # 將 app/data 的模擬資料匯入 SQLite
│       ├── data/              # 捷運／公車模擬資料來源（JSON，會在啟動時匯入 SQLite）
│       │   ├── metro_lines.json
│       │   ├── bus_routes.json
│       │   └── nearby_stops.json
│       ├── schemas/           # Pydantic 資料格式
│       ├── services/          # 商業邏輯（路線規劃、模擬到站狀態）
│       └── routers/           # API 路由（僅負責 HTTP 進出）
│
└── frontend/                  # Vue 3 + Vite + TypeScript PWA
    ├── index.html
    ├── vite.config.ts          # 含 PWA 設定（vite-plugin-pwa）
    ├── public/icons/           # PWA 圖示
    └── src/
        ├── main.ts
        ├── App.vue
        ├── router/             # 5 個頁籤路由
        ├── views/              # 頁面（僅負責畫面呈現）
        │   ├── HomeView.vue      首頁
        │   ├── MetroView.vue     捷運
        │   ├── BusView.vue       公車
        │   ├── NearbyView.vue    附近
        │   ├── FavoritesView.vue 收藏
        │   └── StopDetailView.vue
        ├── components/         # 可重用 UI 元件（BottomNav、StatusBadge…）
        ├── stores/             # Pinia 狀態管理（呼叫 API、loading/error 狀態）
        ├── api/                # 唯一與後端溝通的呼叫層，前端不含任何金鑰
        ├── composables/        # 深色模式、定位、防抖等邏輯
        ├── utils/              # localStorage 工具
        └── types/              # 前後端共用的資料型別
```

**UI 與邏輯分離的原則：**
- `views/*.vue` 只負責畫面呈現與使用者互動，不直接呼叫 `fetch`。
- `stores/*.ts` 負責狀態管理與呼叫 `api/*.ts`，並處理 loading／錯誤狀態。
- `api/*.ts` 是唯一與後端溝通的地方；前端完全不會接觸任何 API 金鑰。
- 後端 `routers/*.py` 只負責 HTTP 進出；商業邏輯（路線規劃、模擬到站狀態）都在 `services/*.py`。

## 技術架構

| 項目 | 技術 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router |
| PWA | vite-plugin-pwa（可加入 Android／iPhone 主畫面，支援離線） |
| 地圖 | Leaflet + OpenStreetMap |
| 後端 | Python FastAPI |
| 資料庫 | SQLite（透過 SQLAlchemy，啟動時自動由模擬資料 JSON 匯入） |
| 即時交通資料 | 預留 TDX API 串接位置（`USE_TDX=false`，第一版未啟用） |

## 第一版功能

- 首頁：搜尋框、附近站牌、常用收藏、最近查詢
- 捷運：輸入起訖站，顯示搭乘路線、轉乘站、經過站數、預估時間
- 公車：路線號碼搜尋、去程／返程／沿途站牌
- 站牌搜尋：顯示該站牌所有經過路線
- 到站狀態：模擬「進站中」「約 X 分鐘」「尚未發車」，並標示「模擬資料」
- 收藏：捷運站／公車路線／站牌，儲存於 localStorage
- 深色模式、手機定位（附近站牌為模擬資料）
- 可安裝為 PWA；離線時仍可開啟首頁與收藏內容
- 資料取得失敗時顯示「目前無法取得即時資料」，不會顯示錯誤或虛構的數字

## 在電腦上啟動（開發模式）

### 1. 啟動後端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

第一次啟動時會自動建立 `movego.db`（SQLite）並匯入模擬資料。
確認後端正常：瀏覽 http://127.0.0.1:8000/api/health 應回傳 `{"status":"ok","use_tdx":false}`。

若要之後接上真正的 TDX API，只需在 `backend/.env` 填入 `TDX_CLIENT_ID`／`TDX_CLIENT_SECRET` 並將 `USE_TDX` 改為 `true`（第一版程式碼尚未讀取此開關，僅預留欄位）。**`.env` 絕對不要提交到版本控制。**

### 2. 啟動前端

另開一個終端機：

```bash
cd frontend
npm install
npm run dev
```

瀏覽器開啟 http://localhost:5173 。開發模式下前端會透過 Vite proxy 將 `/api/*` 轉送到 `http://127.0.0.1:8000`，不需要另外設定 CORS。

## 在手機上測試

1. 確認電腦與手機連在**同一個 Wi‑Fi**。
2. 在電腦上查詢區網 IP（Windows 可執行 `ipconfig`，找 IPv4 位址，例如 `192.168.1.23`）。
3. 後端已用 `--host 0.0.0.0` 啟動，前端 `vite.config.ts` 也已設定 `server.host: true`，所以兩者都會對外開放。
4. 在手機瀏覽器（iPhone 用 Safari、Android 用 Chrome）輸入：

   ```
   http://192.168.1.23:5173
   ```

   （把 IP 換成你電腦的實際區網 IP）
5. 若手機打不開，檢查 Windows 防火牆是否封鎖了 5173／8000 連接埠，或暫時允許私人網路存取。

### 安裝成 PWA

- **Android（Chrome）**：開啟網址後，右上角選單 →「加入主畫面」或畫面下方會自動跳出安裝提示。
- **iPhone（Safari）**：開啟網址後，點分享圖示 → 「加入主畫面」。

安裝後即可像原生 App 一樣從主畫面啟動，首頁與收藏內容在離線時仍可查看。

## 執行正式建置（build）

```bash
cd frontend
npm run build
npm run preview -- --host
```

`npm run build` 會產生含 Service Worker 的 `dist/`，可用 `npm run preview` 在區網測試離線快取行為，或部署到任何靜態主機（後端 API 需另外部署並設定正確的 CORS）。

## 執行後端測試

```bash
cd backend
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

測試只涵蓋純邏輯（捷運 Dijkstra 路線規劃、TDX 回傳資料轉換），不會連資料庫或打 TDX。

## TDX 即時資料串接

專案已串接 TDX 公車與捷運 API（`USE_TDX=true` 時生效），細節：

- **公車路線／站牌是一次性批次同步進 SQLite**，不是每次搜尋都即時打 TDX：後端啟動時會用 4 次 TDX 呼叫（台北市＋新北市，路線清單＋去回程站牌各 2 次）把全部路線（近千條）同步進本機資料庫，之後搜尋、瀏覽路線一律讀本機、完全不消耗 TDX 額度。只有**查看路線詳情時的到站狀態**才會即時打 TDX（1 次，含去回程），而且有 60 秒快取。已同步過（資料庫內路線數 ≥ 50）就不會重複同步，避免開發時 `--reload` 重複消耗額度。
- 捷運：路線與站點資料（含環狀線）在記憶體中快取，`/api/metro/liveboard` 即時到站看板每次呼叫 TDX 並快取 60 秒
- 附近站牌：座標查詢無法預先同步，維持即時呼叫 TDX（前端有 60 秒節流保護）
- API 呼叫失敗時（額度用完、網路問題）一律回傳「目前無法取得即時資料」，不會退回模擬資料；但公車批次同步若在啟動時失敗，會自動保留模擬資料當備援，不會讓公車功能整個掛掉
- 憑證只存在 `backend/.env`（`TDX_CLIENT_ID`／`TDX_CLIENT_SECRET`），前端完全不會接觸

若在 Windows 上啟動後端時出現 `CERTIFICATE_VERIFY_FAILED`（常見於有防毒軟體／公司網路做 SSL 檢查的環境），在虛擬環境安裝 `pip-system-certs` 讓 Python 改用系統憑證庫即可解決：

```bash
cd backend
.venv\Scripts\activate
python -m pip install pip-system-certs
```

安裝後需要重新啟動 `uvicorn`（新套件透過 Python 啟動時的 hook 生效，單純程式碼變更觸發的 `--reload` 不會套用）。

## 部署到雲端（GitHub + Render）

專案根目錄的 [render.yaml](render.yaml) 是 Render 的 Blueprint 設定檔，會一次部署兩個服務：`movego-backend`（FastAPI）與 `movego-frontend`（前端靜態網站建置後的產物）。

### 1. 推上 GitHub

```bash
git add -A
git commit -m "Initial commit"
git remote add origin https://github.com/<你的帳號>/<repo名稱>.git
git push -u origin main
```

（`.env` 已經被 `.gitignore` 排除，金鑰不會被提交。）

### 2. 在 Render 建立 Blueprint

1. 到 [Render 儀表板](https://dashboard.render.com/) → 「New +」→「Blueprint」
2. 選擇剛剛推上去的 GitHub repo，Render 會自動讀到 `render.yaml` 並建立兩個服務
3. 部署完成後，到 **movego-backend** 服務的「Environment」分頁，手動填入：
   - `TDX_CLIENT_ID`
   - `TDX_CLIENT_SECRET`
   （這兩個刻意不寫在 `render.yaml` 裡，必須手動在 Render 後台輸入）
4. 確認兩個服務實際分配到的網址是否跟 `render.yaml` 裡預設的
   `movego-backend.onrender.com` / `movego-frontend.onrender.com` 一致——如果服務名稱被別人佔用，Render 會自動改名，這時要回來更新：
   - `movego-backend` 服務的 `CORS_ORIGINS` 環境變數，改成實際的前端網址
   - `movego-frontend` 服務的 `VITE_API_BASE_URL` 環境變數，改成實際的後端網址（記得結尾要有 `/api`）
   - 改完任一個環境變數後，要手動觸發該服務的 "Manual Deploy" 重新部署一次

### 3. 手機直接連公開網址

部署完成後，手機直接開 `https://movego-frontend.onrender.com`（換成你實際的網址）即可，不再受區網限制，也可以直接安裝成 PWA。

Render 免費方案的服務在閒置一段時間後會休眠，下次有人連入時第一次請求會慢個十幾秒喚醒，屬正常現象。

## 尚未包含（刻意留給後續版本）

- 帳號系統與跨裝置收藏同步
- 真實距離排序的附近站牌（目前為固定模擬清單）
- 站牌搜尋（首頁／附近頁）目前仍使用內建模擬公車站牌資料，尚未改接 TDX 全量站牌
