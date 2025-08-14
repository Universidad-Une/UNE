// @ts-check
import { defineConfig } from "astro/config";
import sitemap from '@astrojs/sitemap';
import path from "path";
import tailwindcss from "@tailwindcss/vite";

// https://astro.build/config
export default defineConfig({
  site: 'https://vivetuuniversidad.com', // 👈 Cambiar por tu dominio real
  integrations: [
    sitemap() // 👈 ESTO FALTABA - Agregar la integración aquí
  ],
  vite: {
    plugins: [tailwindcss()],
    build: {
      sourcemap: false,
    },
    security: {
      checkOrigin: true,
    },
    resolve: {
      alias: {
        "@": path.resolve("./src"),
        "@assets": path.resolve("./src/assets"),
        "@components": path.resolve("./src/components"),
        "@layouts": path.resolve("./src/layouts"),
        "@utils": path.resolve("./src/utils"),
        "@pages": path.resolve("./src/pages"),
        "@helpers": path.resolve("./src/helpers"),
        "@ui": path.resolve("./src/components/ui"),
        "@layout": path.resolve("./src/components/layout"),
        "@sections": path.resolve("./src/components/sections"),
        "@features": path.resolve("./src/components/features"),
        "@images": path.resolve("./src/assets/images"),
        "@logos": path.resolve("./src/assets/Logos"),
        "@icons": path.resolve("./src/assets/icons"),
        "@types": path.resolve("./src/types"),
      },
    },
  },
});