<script setup lang="ts">
/**
 * 捷運路線圖選站元件：以「每條路線一個直式站牌圖」的方式呈現（可切換路線分頁），
 * 點擊任一站名可選擇設為起點或終點。分支線（支線）會附掛在主線分頁下方顯示。
 */
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import { useMetroStore } from "@/stores/metro";
import type { MetroLine } from "@/types";

const emit = defineEmits<{
  pick: [role: "from" | "to", name: string];
  close: [];
}>();

const metroStore = useMetroStore();
const router = useRouter();

interface LineGroup {
  groupId: string;
  label: string;
  color: string;
  main: MetroLine;
  branches: MetroLine[];
}

const GROUP_ORDER = ["R", "G", "BL", "O", "BR", "Y"];

const groups = computed<LineGroup[]>(() => {
  const byId = new Map(metroStore.lines.map((line) => [line.id, line]));
  return GROUP_ORDER.filter((id) => byId.has(id)).map((id) => {
    const main = byId.get(id)!;
    const branches = metroStore.lines.filter((line) => line.id.startsWith(id + "-"));
    return { groupId: id, label: main.name, color: main.color, main, branches };
  });
});

const activeGroupId = ref(GROUP_ORDER[0]);
const activeGroup = computed(() => groups.value.find((g) => g.groupId === activeGroupId.value) ?? groups.value[0]);

const actionSheetStation = ref<string | null>(null);

function openStation(name: string) {
  actionSheetStation.value = name;
}

function choose(role: "from" | "to") {
  if (!actionSheetStation.value) return;
  emit("pick", role, actionSheetStation.value);
  actionSheetStation.value = null;
}

function cancelAction() {
  actionSheetStation.value = null;
}

function viewLiveboard() {
  if (!actionSheetStation.value) return;
  const name = actionSheetStation.value;
  actionSheetStation.value = null;
  emit("close");
  router.push({ path: "/metro/station/" + encodeURIComponent(name) });
}
</script>

<template>
  <div class="picker-overlay" @click.self="emit('close')">
    <div class="picker-sheet">
      <div class="picker-header">
        <div class="picker-title">捷運路線圖選站</div>
        <button class="close-btn" type="button" aria-label="關閉" @click="emit('close')">✕</button>
      </div>

      <div class="group-tabs">
        <button
          v-for="group in groups"
          :key="group.groupId"
          class="group-tab"
          :class="{ active: activeGroupId === group.groupId }"
          :style="activeGroupId === group.groupId ? { borderColor: group.color, color: group.color } : {}"
          type="button"
          @click="activeGroupId = group.groupId"
        >
          {{ group.label }}
        </button>
      </div>

      <div v-if="activeGroup" class="line-body">
        <div class="line-diagram" :style="{ '--line-color': activeGroup.color }">
          <div v-for="station in activeGroup.main.stations" :key="station.id" class="station-row" @click="openStation(station.name)">
            <span class="station-dot"></span>
            <span class="station-name">{{ station.name }}</span>
          </div>
        </div>

        <template v-for="branch in activeGroup.branches" :key="branch.id">
          <div class="branch-title">支線：{{ branch.name.replace(activeGroup.main.name, "").replace(/[（）]/g, "") }}</div>
          <div class="line-diagram branch" :style="{ '--line-color': activeGroup.color }">
            <div v-for="station in branch.stations" :key="station.id" class="station-row" @click="openStation(station.name)">
              <span class="station-dot"></span>
              <span class="station-name">{{ station.name }}</span>
            </div>
          </div>
        </template>
      </div>

      <div v-else class="empty-hint">路線資料載入中…</div>
    </div>

    <div v-if="actionSheetStation" class="action-sheet-overlay" @click.self="cancelAction">
      <div class="action-sheet">
        <div class="action-sheet-title">{{ actionSheetStation }}</div>
        <button class="btn" style="width: 100%; margin-bottom: 8px" type="button" @click="choose('from')">設為起點</button>
        <button class="btn" style="width: 100%; margin-bottom: 8px" type="button" @click="choose('to')">設為終點</button>
        <button class="btn btn-outline" style="width: 100%; margin-bottom: 8px" type="button" @click="viewLiveboard">
          查看即時到站
        </button>
        <button class="btn btn-outline" style="width: 100%" type="button" @click="cancelAction">取消</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.picker-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

.picker-sheet {
  background: var(--color-bg);
  width: 100%;
  max-height: 82vh;
  border-radius: 18px 18px 0 0;
  display: flex;
  flex-direction: column;
  padding: 14px 16px calc(16px + var(--safe-bottom));
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.picker-title {
  font-size: 18px;
  font-weight: 800;
}

.close-btn {
  min-width: 44px;
  min-height: 44px;
  border: none;
  background: var(--color-surface);
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
}

.group-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 10px;
  margin-bottom: 6px;
}

.group-tab {
  flex-shrink: 0;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1.5px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
}

.line-body {
  overflow-y: auto;
  flex: 1;
}

.line-diagram {
  position: relative;
  padding-left: 22px;
  border-left: 4px solid var(--line-color);
  margin-left: 10px;
}

.line-diagram.branch {
  margin-bottom: 12px;
}

.branch-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-muted);
  margin: 14px 0 6px 10px;
}

.station-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  cursor: pointer;
  position: relative;
}

.station-dot {
  position: absolute;
  left: -28px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-surface);
  border: 3px solid var(--line-color);
}

.station-name {
  font-size: 16px;
  font-weight: 600;
}

.action-sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 110;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.action-sheet {
  background: var(--color-surface);
  width: 100%;
  padding: 18px 16px calc(18px + var(--safe-bottom));
  border-radius: 18px 18px 0 0;
}

.action-sheet-title {
  text-align: center;
  font-weight: 800;
  font-size: 17px;
  margin-bottom: 14px;
}
</style>
