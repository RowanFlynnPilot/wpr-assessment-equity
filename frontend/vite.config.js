import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { readdirSync, copyFileSync, mkdirSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const OUTPUT_DIR = fileURLToPath(new URL("../output", import.meta.url));

// Serve/copy ONLY the JSON feeds from output/. The findings memos (*.md) in the
// same directory are internal editor documents, not publications — Vite's
// publicDir would have copied them to the public site wholesale.
function feedsOnly() {
  const isFeed = (name) => /^(index|findings-\d{4}|crosscheck-\d{4})\.json$/.test(name);
  return {
    name: "wpr-feeds-only",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const name = (req.url || "").split("?")[0].replace(server.config.base, "");
        const file = join(OUTPUT_DIR, name);
        if (isFeed(name) && existsSync(file)) {
          res.setHeader("Content-Type", "application/json");
          res.end(readFileSync(file));
          return;
        }
        next();
      });
    },
    closeBundle() {
      const dist = fileURLToPath(new URL("./dist", import.meta.url));
      mkdirSync(dist, { recursive: true });
      const copied = readdirSync(OUTPUT_DIR).filter(isFeed);
      for (const name of copied) copyFileSync(join(OUTPUT_DIR, name), join(dist, name));
      console.log(`feeds copied to dist: ${copied.join(", ")}`);
    },
  };
}

export default defineConfig({
  plugins: [react(), feedsOnly()],
  base: "/wpr-assessment-equity/",
  publicDir: false,
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return;
          if (/[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/.test(id))
            return "react";
          return "charts"; // recharts + its d3/lodash deps
        },
      },
    },
  },
});
