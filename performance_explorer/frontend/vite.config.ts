import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({ plugins: [react()], server: { proxy: { "/api/v5": process.env.V5_API_TARGET ?? "http://127.0.0.1:8005" } }, preview: { proxy: { "/api/v5": process.env.V5_API_TARGET ?? "http://127.0.0.1:8005" } }, test: { environment: "jsdom", globals: true, setupFiles: "./src/test/setup.ts" } });
