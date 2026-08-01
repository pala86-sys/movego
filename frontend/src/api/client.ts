/** 統一的後端 API 呼叫層：前端只透過這層與後端溝通，不會接觸任何金鑰或第三方 API。
 *
 * 本機開發時走 Vite proxy（相對路徑 /api）；正式部署時後端是不同網域的獨立服務，
 * 需在建置時透過 VITE_API_BASE_URL 指定完整後端網址（例如 https://movego-backend.onrender.com/api）。
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {}

async function request<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`);
  } catch {
    throw new ApiError("目前無法取得即時資料");
  }

  if (!response.ok) {
    throw new ApiError("目前無法取得即時資料");
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError("目前無法取得即時資料");
  }
}

export const apiGet = request;
