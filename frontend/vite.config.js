import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  base: "/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      src: path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3030,
    host: true,
    open: process.env.VITE_OPEN_BROWSER !== "false",
    proxy: {
      "/v1": {
        target: process.env.VITE_PROXY_TARGET || "http://localhost:9090",
        changeOrigin: true,
      },
    },
  },
});
