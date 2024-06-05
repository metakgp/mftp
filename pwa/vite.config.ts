import { VitePWA } from "vite-plugin-pwa";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react(),
        VitePWA({
            strategies: "injectManifest",
            srcDir: "src",
            filename: "sw.ts",
            registerType: "autoUpdate",
            injectRegister: false,

            pwaAssets: {
                disabled: false,
                config: true,
            },

            manifest: {
                name: "mftp-pwa",
                short_name: "mftp-pwa",
                description: "A PWA to make MFTP yet another app",
                theme_color: "#ffffff",
            },

            injectManifest: {
                globPatterns: ["**/*.{js,css,html,svg,png,ico}"],
            },

            devOptions: {
                enabled: false,
                navigateFallback: "index.html",
                suppressWarnings: true,
                type: "module",
            },
        }),
    ],
});
