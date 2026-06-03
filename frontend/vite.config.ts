import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
  },
  preview: {
    host: "0.0.0.0",
    allowedHosts: [
      "seo-crawler-production-37d1.up.railway.app"
    ]
  }
});