<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import LeafletMap from "@/components/LeafletMap.vue";
import TopBar from "@/components/TopBar.vue";
import { useGeolocation } from "@/composables/useGeolocation";
import { useParkingStore } from "@/stores/parking";
import { useStopStore } from "@/stores/stop";

const COOLDOWN_MS = 60000;

const stopStore = useStopStore();
const parkingStore = useParkingStore();
const router = useRouter();
const { coords, status, request } = useGeolocation();

const TAIPEI_STATION = { lat: 25.0478, lng: 121.517 };
const center = computed(() => coords.value ?? TAIPEI_STATION);
const isRealData = computed(() => stopStore.nearbyStops.some((s) => s.distance_meters !== null));

// 每秒更新一次，讓「冷卻中」的秒數顯示會跳動；只是給使用者看的倒數，實際節流邏輯在 store 裡
const nowTick = ref(Date.now());
let tickTimer: ReturnType<typeof setInterval> | undefined;

const cooldownRemainingSec = computed(() => {
  if (stopStore.lastNearbyFetchAt === null) return 0;
  const remaining = COOLDOWN_MS - (nowTick.value - stopStore.lastNearbyFetchAt);
  return remaining > 0 ? Math.ceil(remaining / 1000) : 0;
});

const parkingCooldownRemainingSec = computed(() => {
  if (parkingStore.lastFetchAt === null) return 0;
  const remaining = COOLDOWN_MS - (nowTick.value - parkingStore.lastFetchAt);
  return remaining > 0 ? Math.ceil(remaining / 1000) : 0;
});

onMounted(() => {
  // 不在這裡自動抓取：附近站牌／附近停車場都只在使用者按按鈕時才會打 API，避免一進頁面就消耗 TDX 額度
  tickTimer = setInterval(() => (nowTick.value = Date.now()), 1000);
});

onUnmounted(() => {
  if (tickTimer) clearInterval(tickTimer);
});

function onLocate() {
  if (cooldownRemainingSec.value > 0) return;
  request();
}

watch(coords, (value) => {
  if (value) stopStore.loadNearby(value.lat, value.lng);
});

function onSearchParking() {
  if (parkingCooldownRemainingSec.value > 0) return;
  parkingStore.loadNearby(center.value.lat, center.value.lng);
}

function openStop(id: string) {
  const stop = stopStore.nearbyStops.find((s) => s.id === id);
  if (!stop) return;
  if (stop.type === "metro") router.push({ path: "/metro", query: { to: stop.name } });
  else router.push({ path: "/stop/" + encodeURIComponent(stop.name) });
}

function spacesLabel(availableSpaces: number | null, totalSpaces: number | null): string {
  if (availableSpaces === null || totalSpaces === null) return "無即時資料";
  return `剩 ${availableSpaces} / ${totalSpaces} 位`;
}

function spacesClass(availableSpaces: number | null): string {
  if (availableSpaces === null) return "spaces-unknown";
  if (availableSpaces === 0) return "spaces-full";
  if (availableSpaces <= 10) return "spaces-low";
  return "spaces-ok";
}
</script>

<template>
  <div class="page">
    <TopBar title="附近站牌" />

    <button class="btn locate-btn" type="button" :disabled="cooldownRemainingSec > 0" @click="onLocate">
      📍
      {{
        status === "loading"
          ? "定位中…"
          : cooldownRemainingSec > 0
            ? `請稍候 ${cooldownRemainingSec} 秒再更新`
            : "使用目前位置"
      }}
    </button>
    <div v-if="status === 'denied'" class="hint-text">無法取得定位權限，顯示台北車站周邊做為預設位置</div>
    <div v-else-if="status === 'unsupported'" class="hint-text">此裝置不支援定位，顯示台北車站周邊做為預設位置</div>
    <div v-else-if="cooldownRemainingSec > 0" class="hint-text">為了不超過即時資料查詢限制，更新頻率限制在 60 秒一次</div>

    <div class="map-wrap">
      <LeafletMap :stops="stopStore.nearbyStops" :center="center" @select="openStop" />
    </div>

    <div class="section-title">附近站牌清單{{ isRealData ? "" : stopStore.lastNearbyFetchAt ? "（模擬資料）" : "" }}</div>
    <div v-if="stopStore.error" class="error-hint">{{ stopStore.error }}</div>
    <div v-else class="card">
      <div v-if="stopStore.lastNearbyFetchAt === null" class="empty-hint">按上方「使用目前位置」開始查詢附近站牌</div>
      <div v-else-if="stopStore.nearbyStops.length === 0" class="empty-hint">附近沒有找到站牌</div>
      <div v-for="stop in stopStore.nearbyStops" :key="stop.id" class="list-item" @click="openStop(stop.id)">
        <span>{{ stop.type === "metro" ? "🚇" : "🚌" }} {{ stop.name }}</span>
        <span v-if="stop.distance_meters !== null" class="distance">{{ stop.distance_meters }} 公尺</span>
        <span v-else class="arrow">›</span>
      </div>
    </div>

    <div class="section-title">附近停車場</div>
    <button
      class="btn btn-outline locate-btn"
      type="button"
      :disabled="parkingCooldownRemainingSec > 0"
      @click="onSearchParking"
    >
      🅿️
      {{
        parkingStore.loading
          ? "查詢中…"
          : parkingCooldownRemainingSec > 0
            ? `請稍候 ${parkingCooldownRemainingSec} 秒再更新`
            : "查詢附近停車場"
      }}
    </button>
    <div v-if="parkingCooldownRemainingSec > 0" class="hint-text">為了不超過即時資料查詢限制，更新頻率限制在 60 秒一次</div>

    <div v-if="parkingStore.error" class="error-hint">{{ parkingStore.error }}</div>
    <div v-else class="card">
      <div v-if="parkingStore.lastFetchAt === null" class="empty-hint">按上方按鈕查詢附近停車場剩餘車位</div>
      <div v-else-if="parkingStore.lots.length === 0" class="empty-hint">附近沒有找到停車場</div>
      <div v-for="lot in parkingStore.lots" :key="lot.id" class="list-item parking-item">
        <div class="parking-info">
          <div class="parking-name">{{ lot.name }}</div>
          <div class="parking-address">{{ lot.address }}</div>
        </div>
        <div class="parking-meta">
          <span class="spaces" :class="spacesClass(lot.available_spaces)">
            {{ spacesLabel(lot.available_spaces, lot.total_spaces) }}
          </span>
          <span v-if="lot.distance_meters !== null" class="distance">{{ lot.distance_meters }} 公尺</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.locate-btn {
  width: 100%;
  margin-bottom: 8px;
}

.hint-text {
  font-size: 13px;
  color: var(--color-text-muted);
  text-align: center;
  margin-bottom: 10px;
}

.map-wrap {
  margin-bottom: 6px;
}

.distance {
  color: var(--color-primary);
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
}

.arrow {
  color: var(--color-text-muted);
}

.parking-item {
  align-items: flex-start;
  cursor: default;
}

.parking-info {
  flex: 1;
  min-width: 0;
}

.parking-name {
  font-weight: 700;
  font-size: 15px;
}

.parking-address {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.parking-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.spaces {
  font-size: 14px;
  font-weight: 800;
  white-space: nowrap;
}

.spaces-ok {
  color: var(--color-success);
}

.spaces-low {
  color: var(--color-warning);
}

.spaces-full {
  color: var(--color-danger);
}

.spaces-unknown {
  color: var(--color-text-muted);
  font-weight: 600;
}
</style>
