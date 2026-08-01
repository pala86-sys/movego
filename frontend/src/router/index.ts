import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "home", component: () => import("@/views/HomeView.vue") },
    { path: "/metro", name: "metro", component: () => import("@/views/MetroView.vue") },
    { path: "/bus", name: "bus", component: () => import("@/views/BusView.vue") },
    { path: "/nearby", name: "nearby", component: () => import("@/views/NearbyView.vue") },
    { path: "/favorites", name: "favorites", component: () => import("@/views/FavoritesView.vue") },
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
    }
  ]
});

export default router;
