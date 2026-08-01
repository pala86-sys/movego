<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";

import FavoriteStar from "@/components/FavoriteStar.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import TopBar from "@/components/TopBar.vue";
import { useStopStore } from "@/stores/stop";

const props = defineProps<{ name: string }>();
const router = useRouter();
const stopStore = useStopStore();

onMounted(() => {
  stopStore.search(props.name);
});

const result = () => stopStore.searchResults.find((r) => r.stop_name === props.name);
</script>

<template>
  <div class="page">
    <TopBar :title="name" />
    <button class="btn btn-outline back-btn" type="button" @click="router.back()">‹ 返回</button>

    <div v-if="stopStore.loading" class="card"><div class="empty-hint">查詢中…</div></div>
    <div v-else-if="stopStore.error" class="error-hint">{{ stopStore.error }}</div>
    <div v-else-if="!result()" class="card"><div class="empty-hint">找不到這個站牌的資料</div></div>

    <div v-else class="card">
      <div class="stop-header">
        <div class="stop-name">{{ name }}</div>
        <FavoriteStar type="stop" :item-key="name" :label="name" />
      </div>
      <div class="section-title" style="margin-top: 0">經過路線</div>
      <div v-for="route in result()!.routes" :key="route.route_id + route.direction" class="list-item">
        <span>{{ route.route_name }}（{{ route.direction }}）</span>
        <StatusBadge :status="route.status" show-mock-tag />
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-btn {
  margin-bottom: 14px;
}

.stop-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stop-name {
  font-size: 20px;
  font-weight: 800;
}
</style>
