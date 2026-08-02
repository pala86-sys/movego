<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";

import TopBar from "@/components/TopBar.vue";
import { computeCustomRouteStats } from "@/composables/useCustomRouteStats";
import { useCustomRoutesStore } from "@/stores/customRoutes";
import { useMetroStore } from "@/stores/metro";

const props = defineProps<{ id: string }>();
const router = useRouter();
const customRoutesStore = useCustomRoutesStore();
const metroStore = useMetroStore();

const route = computed(() => customRoutesStore.byId(props.id));
const stats = computed(() => (route.value ? computeCustomRouteStats(route.value.legs, metroStore.lines) : null));

onMounted(() => {
  metroStore.loadLines();
});

function remove() {
  customRoutesStore.remove(props.id);
  router.push("/favorites");
}
</script>

<template>
  <div class="page">
    <TopBar :title="route?.name || '自訂路線'" />
    <button class="btn btn-outline back-btn" type="button" @click="router.push('/favorites')">‹ 返回收藏</button>

    <div v-if="!route" class="card"><div class="empty-hint">找不到這條自訂路線</div></div>

    <div v-else class="card">
      <div v-if="stats" class="summary-row">
        <div class="summary-item">
          <div class="summary-value">{{ stats.estimatedMinutes }} 分</div>
          <div class="summary-label">預估時間</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ stats.transferCount }} 次</div>
          <div class="summary-label">轉乘</div>
        </div>
        <div class="summary-item">
          <div class="summary-value">{{ stats.totalStopCount }} 站</div>
          <div class="summary-label">共經過</div>
        </div>
      </div>

      <div v-for="(leg, index) in route.legs" :key="index" class="leg">
        <div class="leg-line" :style="{ background: leg.lineColor }">{{ leg.lineName }}</div>
        <div class="leg-body">{{ leg.from }} → {{ leg.to }}</div>
      </div>

      <div class="action-row">
        <button class="btn btn-outline" style="flex: 1" type="button" @click="router.push('/custom-routes/' + id + '/edit')">
          編輯
        </button>
        <button class="btn btn-outline danger" style="flex: 1" type="button" @click="remove">刪除</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-btn {
  margin-bottom: 14px;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 4px;
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
  border-bottom: 1px solid var(--color-border);
}

.leg:last-of-type {
  border-bottom: none;
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

.leg-body {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.action-row {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.danger {
  color: var(--color-danger);
  border-color: var(--color-danger);
}
</style>
