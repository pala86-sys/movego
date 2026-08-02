<script setup lang="ts">
/** 自訂路線編輯器：手動選「路線 → 上車站 → 下車站」逐段加入，組成一條完整的自訂轉乘路線。 */
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import TopBar from "@/components/TopBar.vue";
import { useCustomRoutesStore } from "@/stores/customRoutes";
import { useMetroStore } from "@/stores/metro";
import type { CustomRouteLeg } from "@/types";

const props = defineProps<{ id?: string }>();
const router = useRouter();
const metroStore = useMetroStore();
const customRoutesStore = useCustomRoutesStore();

const routeName = ref("");
const legs = ref<CustomRouteLeg[]>([]);

const selectedLineId = ref("");
const boardStation = ref("");
const alightStation = ref("");

const selectedLine = computed(() => metroStore.lines.find((l) => l.id === selectedLineId.value) ?? null);

onMounted(() => {
  metroStore.loadLines();
  if (props.id) {
    const existing = customRoutesStore.byId(props.id);
    if (existing) {
      routeName.value = existing.name;
      legs.value = [...existing.legs];
    }
  }
});

function addLeg() {
  if (!selectedLine.value || !boardStation.value || !alightStation.value) return;
  if (boardStation.value === alightStation.value) return;
  legs.value.push({
    lineId: selectedLine.value.id,
    lineName: selectedLine.value.name,
    lineColor: selectedLine.value.color,
    from: boardStation.value,
    to: alightStation.value
  });
  boardStation.value = "";
  alightStation.value = "";
}

function removeLeg(index: number) {
  legs.value.splice(index, 1);
}

function save() {
  if (!routeName.value.trim() || legs.value.length === 0) return;
  if (props.id) {
    customRoutesStore.update(props.id, routeName.value.trim(), legs.value);
  } else {
    customRoutesStore.add(routeName.value.trim(), legs.value);
  }
  router.push("/favorites");
}

const canSave = computed(() => routeName.value.trim().length > 0 && legs.value.length > 0);
const canAddLeg = computed(() => !!selectedLine.value && !!boardStation.value && !!alightStation.value && boardStation.value !== alightStation.value);
</script>

<template>
  <div class="page">
    <TopBar :title="id ? '編輯自訂路線' : '新增自訂路線'" />
    <button class="btn btn-outline back-btn" type="button" @click="router.push('/favorites')">‹ 返回收藏</button>

    <div class="card">
      <label class="field-label">路線名稱</label>
      <input v-model="routeName" class="input" placeholder="例如：六張犁到三重（走東門轉乘）" />
    </div>

    <div class="section-title">已加入的段路</div>
    <div class="card">
      <div v-if="legs.length === 0" class="empty-hint">還沒有加入任何一段</div>
      <div v-for="(leg, index) in legs" :key="index" class="leg-row">
        <div class="leg-line" :style="{ background: leg.lineColor }">{{ leg.lineName }}</div>
        <div class="leg-text">{{ leg.from }} → {{ leg.to }}</div>
        <button class="remove-btn" type="button" aria-label="移除這一段" @click="removeLeg(index)">✕</button>
      </div>
    </div>

    <div class="section-title">加入一段</div>
    <div class="card">
      <label class="field-label">路線</label>
      <select v-model="selectedLineId" class="input" @change="boardStation = ''; alightStation = ''">
        <option value="" disabled>請選擇路線</option>
        <option v-for="line in metroStore.lines" :key="line.id" :value="line.id">{{ line.name }}</option>
      </select>

      <template v-if="selectedLine">
        <label class="field-label" style="margin-top: 12px">上車站</label>
        <select v-model="boardStation" class="input">
          <option value="" disabled>請選擇上車站</option>
          <option v-for="s in selectedLine.stations" :key="s.id" :value="s.name">{{ s.name }}</option>
        </select>

        <label class="field-label" style="margin-top: 12px">下車／轉乘站</label>
        <select v-model="alightStation" class="input">
          <option value="" disabled>請選擇下車站</option>
          <option v-for="s in selectedLine.stations" :key="s.id" :value="s.name">{{ s.name }}</option>
        </select>
      </template>

      <button class="btn" style="width: 100%; margin-top: 12px" type="button" :disabled="!canAddLeg" @click="addLeg">
        ＋ 加入這一段
      </button>
    </div>

    <button class="btn" style="width: 100%; margin-top: 16px" type="button" :disabled="!canSave" @click="save">
      儲存路線
    </button>
  </div>
</template>

<style scoped>
.back-btn {
  margin-bottom: 14px;
}

.field-label {
  display: block;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 6px;
  font-weight: 600;
}

.leg-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.leg-row:last-child {
  border-bottom: none;
}

.leg-line {
  flex-shrink: 0;
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 8px;
}

.leg-text {
  flex: 1;
  font-size: 15px;
}

.remove-btn {
  min-width: 44px;
  min-height: 44px;
  border: none;
  background: none;
  color: var(--color-text-muted);
  font-size: 16px;
  cursor: pointer;
}
</style>
