import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("three/examples/jsm")) return "spatial-effects";
          if (id.includes("node_modules/three")) return "three-runtime";
          if (id.includes("node_modules/@tanstack")) return "query-runtime";
          if (id.includes("node_modules/react")) return "react-runtime";
          return undefined;
        }
      }
    }
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8090",
      "/auth": "http://127.0.0.1:8090",
      "/display/overview": "http://127.0.0.1:8090"
    }
  }
});
