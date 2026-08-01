/** localStorage 讀寫工具，統一處理序列化與例外，避免各處重複 try/catch。 */

export function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function saveToStorage<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // 儲存空間不足或被封鎖時靜默略過，不影響主要功能
  }
}
