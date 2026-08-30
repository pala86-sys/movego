<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import FavoriteStar from "@/components/FavoriteStar.vue";
import MetroMapPicker from "@/components/MetroMapPicker.vue";
import TopBar from "@/components/TopBar.vue";
import { debounce } from "@/utils/debounce";
import { computeCustomRouteStats } from "@/composables/useCustomRouteStats";
import { useCustomRoutesStore } from "@/stores/customRoutes";
import { useMetroStore } from "@/stores/metro";
import { useRecentQueriesStore } from "@/stores/recentQueries";
import { useSettingsStore } from "@/stores/settings";
import type { MetroStationSearchItem } from "@/types";

const route = useRoute();
const metroStore = useMetroStore();
const recentStore = useRecentQueriesStore();
const customRoutesStore = useCustomRoutesStore();
const settings = useSettingsStore();

const fromInput = ref("");
const toInput = ref("");
const fromStation = ref("");
const toStation = ref("");
const activeField = ref<"from" | "to" | null>(null);
const suggestions = ref<MetroStationSearchItem[]>([]);
const showMapPicker = ref(false);

// 查詢成功後，如果剛好有存過同一組起訖點的自訂路線，讓使用者選要看系統算的還是自訂的
const selectedView = ref<"system" | string>("system");
const matchingCustomRoutes = computed(() =>
  settings.flags.customRoutes
    ? customRoutesStore.items.filter(
        (r) =>
          r.legs.length > 0 &&
          r.legs[0].from === fromStation.value &&
          r.legs[r.legs.length - 1].to === toStation.value
      )
    : []
);
const selectedCustomRoute = computed(
  () => matchingCustomRoutes.value.find((r) => r.id === selectedView.value) ?? null
);
const selectedCustomRouteStats = computed(() =>
  selectedCustomRoute.value
    ? computeCustomRouteStats(selectedCustomRoute.value.legs, metroStore.lines)
    : null
);

function setStation(role: "from" | "to", name: string) {
  if (role === "from") {
    fromInput.value = name;
    fromStation.value = name;
  } else {
    toInput.value = name;
    toStation.value = name;
  }
  showMapPicker.value = false;
}

// 起點/終點各自獨立呼叫 API，避免共用同一份搜尋狀態造成兩個欄位互相覆蓋建議清單
let requestSeq = 0;
const runSuggest = debounce(async (value: string, field: "from" | "to") => {
  if (!value.trim()) {
    if (activeField.value === field) suggestions.value = [];
    return;
  }
  const seq = ++requestSeq;
  const result = await metroStore.fetchStationSuggestions(value);
  if (seq === requestSeq && activeField.value === field) {
    suggestions.value = result;
  }
}, 250);

function onFocus(field: "from" | "to") {
  activeField.value = field;
  suggestions.value = [];
}

function onInputChange(field: "from" | "to") {
  const value = field === "from" ? fromInput.value : toInput.value;
  runSuggest(value, field);
}

function pickSuggestion(name: string) {
  if (activeField.value === "from") {
    fromInput.value = name;
    fromStation.value = name;
  } else if (activeField.value === "to") {
    toInput.value = name;
    toStation.value = name;
  }
  suggestions.value = [];
  activeField.value = null;
}

async function search() {
  if (!fromStation.value || !toStation.value) return;
  selectedView.value = "system";
  await metroStore.planRoute(fromStation.value, toStation.value);
  if (metroStore.routePlan) {
    recentStore.add(
      "metro-station",
      toStation.value,
      `${fromStation.value} → ${toStation.value}`,
      fromStation.value
    );
  }
}

onMounted(() => {
  metroStore.loadLines();
  const prefillFrom = route.query.from as string | undefined;
  const prefillTo = route.query.to as string | undefined;
  if (prefillFrom) {
    fromInput.value = prefillFrom;
    fromStation.value = prefillFrom;
  }
  if (prefillTo) {
    toInput.value = prefillTo;
    toStation.value = prefillTo;
  }
});
</script>

<template>
  <div class="page">
    <TopBar title="捷運路線查詢" />

    <div class="card station-picker">
      <div class="field">
        <label class="field-label">起點</label>
        <input
          v-model="fromInput"
          class="input"
          placeholder="輸入起點站名"
          @focus="onFocus('from')"
          @input="onInputChange('from')"
        />
      </div>
      <div class="field">
        <label class="field-label">終點</label>
        <input
          v-model="toInput"
          class="input"
          placeholder="輸入終點站名"
          @focus="onFocus('to')"
          @input="onInputChange('to')"
        />
      </div>

      <ul v-if="activeField && suggestions.length > 0" class="suggestion-list">
        <li v-for="item in suggestions" :key="item.name" @click="pickSuggestion(item.name)">
          {{ item.name }}
        </li>
      </ul>

      <button
        class="btn btn-outline"
        style="width: 100%; margin-top: 6px"
        type="button"
        @click="showMapPicker = true"
      >
        🗺️ 用路線圖選站
      </button>
      <button
        class="btn"
        style="width: 100%; margin-top: 8px"
        :disabled="!fromStation || !toStation"
        @click="search"
      >
        查詢路線
      </button>
    </div>

    <div v-if="metroStore.loading" class="card" style="margin-top: 16px">
      <div class="empty-hint">查詢中…</div>
    </div>

    <div v-else-if="metroStore.error" class="error-hint" style="margin-top: 16px">
      {{ metroStore.error }}
    </div>

    <template v-else-if="metroStore.routePlan">
      <div v-if="matchingCustomRoutes.length > 0" class="view-tabs">
        <button
          class="view-tab"
          :class="{ active: selectedView === 'system' }"
          type="button"
          @click="selectedView = 'system'"
        >
          系統安排
        </button>
        <button
          v-for="(r, i) in matchingCustomRoutes"
          :key="r.id"
          class="view-tab"
          :class="{ active: selectedView === r.id }"
          type="button"
          @click="selectedView = r.id"
        >
          🧭 自訂安排{{ matchingCustomRoutes.length > 1 ? i + 1 : "" }}
        </button>
      </div>

      <div v-if="selectedView === 'system'" class="card result-card">
        <div class="summary-row">
          <div class="summary-item">
            <div class="summary-value">{{ metroStore.routePlan.estimated_minutes }} 分</div>
            <div class="summary-label">預估時間</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ metroStore.routePlan.transfer_count }} 次</div>
            <div class="summary-label">轉乘</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ metroStore.routePlan.total_stop_count }} 站</div>
            <div class="summary-label">共經過</div>
          </div>
          <FavoriteStar
            type="metro-station"
            :item-key="metroStore.routePlan.to_station"
            :label="metroStore.routePlan.to_station"
          />
        </div>

        <div v-for="(leg, index) in metroStore.routePlan.legs" :key="index" class="leg">
          <div class="leg-line" :style="{ background: leg.line_color }">{{ leg.line_name }}</div>
          <div class="leg-body">
            <div>{{ leg.board_station }} → {{ leg.alight_station }}</div>
            <div class="leg-meta">經過 {{ leg.stop_count }} 站</div>
          </div>
        </div>
      </div>

      <div v-else-if="selectedCustomRoute && selectedCustomRouteStats" class="card result-card">
        <div class="summary-row">
          <div class="summary-item">
            <div class="summary-value">{{ selectedCustomRouteStats.estimatedMinutes }} 分</div>
            <div class="summary-label">預估時間</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ selectedCustomRouteStats.transferCount }} 次</div>
            <div class="summary-label">轉乘</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ selectedCustomRouteStats.totalStopCount }} 站</div>
            <div class="summary-label">共經過</div>
          </div>
        </div>
        <div class="custom-route-hint">
          🧭 {{ selectedCustomRoute.name }}（自訂路線，時間為推估值）
        </div>
        <div v-for="(leg, index) in selectedCustomRoute.legs" :key="index" class="leg">
          <div class="leg-line" :style="{ background: leg.lineColor }">{{ leg.lineName }}</div>
          <div class="leg-body">
            <div>{{ leg.from }} → {{ leg.to }}</div>
          </div>
        </div>
      </div>
    </template>

    <MetroMapPicker
      v-if="showMapPicker"
      @pick="(role, name) => setStation(role, name)"
      @close="showMapPicker = false"
    />
  </div>
</template>

<style scoped>
.field {
  margin-bottom: 10px;
}

.field-label {
  display: block;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 6px;
  font-weight: 600;
}

.suggestion-list {
  list-style: none;
  margin: 0 0 10px;
  padding: 4px 0;
  max-height: 220px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.suggestion-list li {
  padding: 12px 14px;
  min-height: 44px;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
}

.suggestion-list li:last-child {
  border-bottom: none;
}

.view-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  flex-shrink: 0;
  margin-top: 16px;
  padding-bottom: 4px;
}

.view-tab {
  flex-shrink: 0;
  min-height: 44px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1.5px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}

.view-tab.active {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
}

.custom-route-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}

.result-card {
  margin-top: 10px;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 12px;
}

.summary-item {
  text-align: center;
}

.summary-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-primary);
}

.summary-label {
  font-size: 12px;
  color: var(--color-text-muted);
}

.leg {
  display: flex;
  gap: 12px;
  padding: 10px 0;
}

.leg-line {
  flex-shrink: 0;
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 10px;
  height: fit-content;
}

.leg-meta {
  color: var(--color-text-muted);
  font-size: 13px;
  margin-top: 2px;
}
</style>
