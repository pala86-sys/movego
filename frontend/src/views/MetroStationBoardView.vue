<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";

import FavoriteStar from "@/components/FavoriteStar.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import TopBar from "@/components/TopBar.vue";
import { useMetroStore } from "@/stores/metro";

const props = defineProps<{ name: string }>();
const router = useRouter();
const metroStore = useMetroStore();

const entries = computed(() => metroStore.liveboard);
const loading = computed(() => metroStore.liveboardLoading);
const error = computed(() => metroStore.liveboardError);

onMounted(() => metroStore.loadLiveboard(props.name));
</script>

<template>
  <div class="page">
    <TopBar :title="`${name}｜即時到站看板`" />
    <button class="btn btn-outline back-btn" type="button" @click="router.back()">‹ 返回</button>

    <div class="card">
      <div class="board-header">
        <div class="board-title">{{ name }}</div>
        <FavoriteStar type="metro-station" :item-key="name" :label="name" />
      </div>

      <div v-if="loading" class="empty-hint">查詢中…</div>
      <div v-else-if="error" class="error-hint">{{ error }}</div>
      <div v-else-if="entries.length === 0" class="empty-hint">目前無列車進站資訊</div>
      <div v-else>
        <div v-for="(entry, index) in entries" :key="index" class="list-item">
          <span>往 {{ entry.destination }}</span>
          <StatusBadge :status="entry.status" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-btn {
  margin-bottom: 14px;
}

.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.board-title {
  font-size: 20px;
  font-weight: 800;
}
</style>
