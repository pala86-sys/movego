/** 簡易防抖工具：搜尋輸入時延遲觸發，避免每個按鍵都打 API。 */
export function debounce<Args extends unknown[]>(fn: (...args: Args) => void, delayMs = 300) {
  let timer: ReturnType<typeof setTimeout> | undefined;
  return (...args: Args) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delayMs);
  };
}
