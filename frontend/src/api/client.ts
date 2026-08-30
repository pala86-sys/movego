/** 統一的後端 API 呼叫層：前端只透過這層與後端溝通，不會接觸任何金鑰或第三方 API。
 *
 * 本機開發時走 Vite proxy（相對路徑 /api）；正式部署時後端是不同網域的獨立服務，
 * 需在建置時透過 VITE_API_BASE_URL 指定完整後端網址（例如 https://movego-backend.onrender.com/api）。
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  /** HTTP 狀態碼；網路或解析失敗時為 0。 */
  readonly status: number;

  constructor(message: string, status = 0) {
    super(message);
    this.status = status;
  }

  /** 後端明確回「查無此資源」（404），而不是暫時性的服務中斷。 */
  get isNotFound(): boolean {
    return this.status === 404;
  }
}

/** 請求被 AbortController 取消時丟出；呼叫端（多半是搜尋輸入）通常直接忽略即可。 */
export class RequestAbortedError extends ApiError {
  constructor() {
    super("已取消", 0);
  }
}

interface RequestOptions {
  /** 傳入 AbortSignal 可在下一次輸入時取消尚未完成的搜尋請求。 */
  signal?: AbortSignal;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { signal: options.signal });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new RequestAbortedError();
    }
    throw new ApiError("目前無法取得即時資料");
  }

  if (!response.ok) {
    const message = response.status === 404 ? "查無符合的資料" : "目前無法取得即時資料";
    throw new ApiError(message, response.status);
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError("目前無法取得即時資料");
  }
}

export const apiGet = request;
