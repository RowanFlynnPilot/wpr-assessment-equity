import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

// Same shape as the wpr-property-transactions widget. publicDir points at the
// repo's output/ so the committed findings feed (the single artifact the study
// writes) is served at `${BASE_URL}findings.json` — exactly what App.jsx
// fetches. base matches the would-be GitHub Pages path; publishing remains an
// editorial decision (see CLAUDE.md).
export default defineConfig({
  plugins: [react()],
  base: "/wpr-assessment-equity/",
  publicDir: fileURLToPath(new URL("../output", import.meta.url)),
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
