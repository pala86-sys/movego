import { createRouter, createWebHistory } from "vue-router";

import { useSettingsStore } from "@/stores/settings";
import type { FeatureFlags } from "@/types";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "home", component: () => import("@/views/HomeView.vue") },
    { path: "/metro", name: "metro", component: () => import("@/views/MetroView.vue") },
    { path: "/bus", name: "bus", component: () => import("@/views/BusView.vue") },
    { path: "/nearby", name: "nearby", component: () => import("@/views/NearbyView.vue") },
    { path: "/favorites", name: "favorites", component: () => import("@/views/FavoritesView.vue") },
    { path: "/settings", name: "settings", component: () => import("@/views/SettingsView.vue") },
    {
      path: "/stop/:name",
      name: "stop-detail",
      component: () => import("@/views/StopDetailView.vue"),
      props: true
    },
    {
      path: "/metro/station/:name",
      name: "metro-station-board",
      component: () => import("@/views/MetroStationBoardView.vue"),
      props: true
    },
    {
      path: "/custom-routes/new",
      name: "custom-route-new",
      component: () => import("@/views/CustomRouteEditorView.vue")
    },
    {
      path: "/custom-routes/:id/edit",
      name: "custom-route-edit",
      component: () => import("@/views/CustomRouteEditorView.vue"),
      props: true
    },
    {
      path: "/custom-routes/:id",
      name: "custom-route-detail",
      component: () => import("@/views/CustomRouteDetailView.vue"),
      props: true
    }
  ]
});

// 被關掉的功能，即使直接打網址也不讓進，導回首頁
const FEATURE_BY_PATH: { prefix: string; flag: keyof FeatureFlags }[] = [
  { prefix: "/metro", flag: "metro" },
  { prefix: "/bus", flag: "bus" },
  { prefix: "/stop", flag: "bus" },
  { prefix: "/nearby", flag: "nearby" },
  { prefix: "/favorites", flag: "favorites" },
  { prefix: "/custom-routes", flag: "customRoutes" }
];

router.beforeEach((to) => {
  const { flags } = useSettingsStore();
  const match = FEATURE_BY_PATH.find(
    (m) => to.path === m.prefix || to.path.startsWith(m.prefix + "/")
  );
  if (match && !flags[match.flag]) return { path: "/" };
  return true;
});

export default router;
