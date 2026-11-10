import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { Plugin } from "vite";

function v6ReplayAssets(): Plugin {
  const reports = resolve(__dirname, "../../v6_driver_in_loop/reports");
  const indexText = readFileSync(resolve(reports, "index.json"), "utf8");
  const index = JSON.parse(indexText) as { runs: Array<{ file: string }> };
  const assets = new Map<string, string>([["index.json", indexText]]);
  for (const run of index.runs) {
    if (!/^replays\/[\w.+-]+\.json$/.test(run.file)) throw new Error(`Unexpected V6 replay path: ${run.file}`);
    assets.set(run.file, readFileSync(resolve(reports, run.file), "utf8"));
  }
  return {
    name: "performance-explorer-v6-replay-assets",
    configureServer(server) {
      server.middlewares.use("/v6/replays", (request, response, next) => {
        let path: string;
        try { path = decodeURIComponent(new URL(request.url ?? "/", "http://localhost").pathname).replace(/^\/+/, ""); }
        catch { next(); return; }
        const content = assets.get(path);
        if (content === undefined) { next(); return; }
        response.statusCode = 200;
        response.setHeader("Content-Type", "application/json; charset=utf-8");
        response.setHeader("Cache-Control", "no-cache");
        response.end(content);
      });
    },
    generateBundle() {
      for (const [path, source] of assets) this.emitFile({ type: "asset", fileName: `v6/replays/${path}`, source });
    },
  };
}

export default defineConfig({ plugins: [react(), v6ReplayAssets()], server: { proxy: { "/api/v5": process.env.V5_API_TARGET ?? "http://127.0.0.1:8005" } }, preview: { proxy: { "/api/v5": process.env.V5_API_TARGET ?? "http://127.0.0.1:8005" } }, test: { environment: "jsdom", globals: true, setupFiles: "./src/test/setup.ts" } });
