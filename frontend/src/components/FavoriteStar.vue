<script setup lang="ts">
import { computed } from "vue";

import { useFavoritesStore } from "@/stores/favorites";
import type { FavoriteType } from "@/types";

const props = defineProps<{
  type: FavoriteType;
  itemKey: string;
  label: string;
}>();

const favorites = useFavoritesStore();
const active = computed(() => favorites.isFavorite(props.type, props.itemKey));

function onToggle() {
  favorites.toggle(props.type, props.itemKey, props.label);
}
</script>

<template>
  <button
    class="star-btn"
    :class="{ active }"
    type="button"
    :aria-label="active ? '取消收藏' : '加入收藏'"
    @click="onToggle"
  >
    {{ active ? "★" : "☆" }}
  </button>
</template>
