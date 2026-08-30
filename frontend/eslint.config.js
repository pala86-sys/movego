import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript";
import pluginVue from "eslint-plugin-vue";
import skipFormatting from "@vue/eslint-config-prettier/skip-formatting";

export default defineConfigWithVueTs(
  {
    name: "app/files-to-lint",
    files: ["**/*.{ts,mts,tsx,vue}"]
  },
  {
    name: "app/files-to-ignore",
    ignores: ["dist/**", "dev-dist/**", "coverage/**"]
  },

  pluginVue.configs["flat/essential"],
  vueTsConfigs.recommended,
  skipFormatting,

  {
    // 型別宣告墊片（例如 *.vue 的 shim）本來就得用 any/{}，不套一般規則
    name: "app/declaration-shims",
    files: ["**/*.d.ts"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-empty-object-type": "off"
    }
  },

  {
    // README 的分層約定：views 只呈現畫面 → stores 管狀態並呼叫 api → api 是唯一碰後端的地方。
    // 這條規則把「view 直接 import @/api」擋在 lint 階段。
    name: "app/layering-rules",
    files: ["src/views/**/*.vue"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/api", "@/api/*"],
              message: "views 不直接呼叫 API 層，請改用 stores/*.ts 的 action。"
            }
          ]
        }
      ]
    }
  }
);
