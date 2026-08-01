/** 深色模式邏輯：讀取/切換偏好並同步到 <html data-theme>，與 UI 元件完全分離。 */
import { ref } from "vue";

const STORAGE_KEY = "movego:theme";
export type ThemeMode = "light" | "dark";

const theme = ref<ThemeMode>("light");

function apply(mode: ThemeMode) {
  document.documentElement.setAttribute("data-theme", mode);
}

export function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  theme.value = saved ?? (prefersDark ? "dark" : "light");
  apply(theme.value);
}

export function useTheme() {
  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark";
    apply(theme.value);
    localStorage.setItem(STORAGE_KEY, theme.value);
  }

  return { theme, toggle };
}
