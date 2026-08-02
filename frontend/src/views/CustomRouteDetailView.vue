<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import TopBar from "@/components/TopBar.vue";
import { useCustomRoutesStore } from "@/stores/customRoutes";

const props = defineProps<{ id: string }>();
const router = useRouter();
const customRoutesStore = useCustomRoutesStore();

const route = computed(() => customRoutesStore.byId(props.id));

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
