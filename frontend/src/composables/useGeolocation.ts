/** 手機定位邏輯：僅取得座標供未來距離排序使用，第一版附近站牌內容仍為模擬資料。 */
import { ref } from "vue";

export function useGeolocation() {
  const coords = ref<{ lat: number; lng: number } | null>(null);
  const status = ref<"idle" | "loading" | "granted" | "denied" | "unsupported">("idle");

  function request() {
    if (!("geolocation" in navigator)) {
      status.value = "unsupported";
      return;
    }
    status.value = "loading";
    navigator.geolocation.getCurrentPosition(
      (position) => {
        coords.value = { lat: position.coords.latitude, lng: position.coords.longitude };
        status.value = "granted";
      },
      () => {
        status.value = "denied";
      },
      { timeout: 8000 }
    );
  }

  return { coords, status, request };
}
