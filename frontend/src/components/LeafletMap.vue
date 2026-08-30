<script setup lang="ts">
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { onMounted, onUnmounted, ref, watch } from "vue";

import type { NearbyStop } from "@/types";

const props = defineProps<{
  stops: NearbyStop[];
  center: { lat: number; lng: number };
}>();

const emit = defineEmits<{ select: [id: string] }>();

const mapEl = ref<HTMLDivElement | null>(null);
let map: L.Map | null = null;
let markers: L.Marker[] = [];

function metroIcon() {
  return L.divIcon({ className: "map-pin metro", html: "🚇", iconSize: [28, 28] });
}
function busIcon() {
  return L.divIcon({ className: "map-pin bus", html: "🚌", iconSize: [28, 28] });
}

function renderMarkers() {
  if (!map) return;
  markers.forEach((m) => m.remove());
  markers = props.stops.map((stop) => {
    const marker = L.marker([stop.lat, stop.lng], {
      icon: stop.type === "metro" ? metroIcon() : busIcon()
    });
    marker.bindPopup(stop.name);
    marker.on("click", () => emit("select", stop.id));
    marker.addTo(map as L.Map);
    return marker;
  });
}

onMounted(() => {
  if (!mapEl.value) return;
  map = L.map(mapEl.value, { zoomControl: true }).setView([props.center.lat, props.center.lng], 15);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
    maxZoom: 19
  }).addTo(map);
  renderMarkers();
});

watch(
  () => props.stops,
  () => renderMarkers()
);

watch(
  () => props.center,
  (center) => {
    map?.setView([center.lat, center.lng]);
  }
);

onUnmounted(() => {
  map?.remove();
  map = null;
});
</script>

<template>
  <div ref="mapEl" class="leaflet-map"></div>
</template>

<style>
.leaflet-map {
  width: 100%;
  height: 260px;
  border-radius: 14px;
  overflow: hidden;
}

.map-pin {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
