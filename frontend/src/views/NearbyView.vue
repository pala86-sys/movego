<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import LeafletMap from "@/components/LeafletMap.vue";
import TopBar from "@/components/TopBar.vue";
import { useGeolocation } from "@/composables/useGeolocation";
import { useStopStore } from "@/stores/stop";

const NEARBY_COOLDOWN_MS = 15000;

const stopStore = useStopStore();
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
  const remaining = NEARBY_COOLDOWN_MS - (nowTick.value - stopStore.lastNearbyFetchAt);
  return remaining > 0 ? Math.ceil(remaining / 1000) : 0;
});

onMounted(() => {
  if (stopStore.nearbyStops.length === 0) stopStore.loadNearby();
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

function openStop(id: string) {
  const stop = stopStore.nearbyStops.find((s) => s.id === id);
  if (!stop) return;
  if (stop.type === "metro") router.push({ path: "/metro", query: { to: stop.name } });
  else router.push({ path: "/stop/" + encodeURIComponent(stop.name) });
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
    <div v-else-if="cooldownRemainingSec > 0" class="hint-text">為了不超過即時資料查詢限制，更新頻率限制在 15 秒一次</div>

    <div class="map-wrap">
      <LeafletMap :stops="stopStore.nearbyStops" :center="center" @select="openStop" />
    </div>

    <div class="section-title">附近站牌清單{{ isRealData ? "" : "（模擬資料）" }}</div>
    <div v-if="stopStore.error" class="error-hint">{{ stopStore.error }}</div>
    <div v-else class="card">
      <div v-if="stopStore.nearbyStops.length === 0" class="empty-hint">目前無法取得即時資料</div>
      <div v-for="stop in stopStore.nearbyStops" :key="stop.id" class="list-item" @click="openStop(stop.id)">
        <span>{{ stop.type === "metro" ? "🚇" : "🚌" }} {{ stop.name }}</span>
        <span v-if="stop.distance_meters !== null" class="distance">{{ stop.distance_meters }} 公尺</span>
        <span v-else class="arrow">›</span>
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
</style>
