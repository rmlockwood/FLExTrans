// Vite configuration for the FTtranslator front end.
//
// npm run build writes the page to dist, which "python -m fttranslator serve" serves. While working on the page, run the server and "npm run dev" side by side: the dev server reloads on every
// edit and passes /api requests on to the Python server, which must be on its default port (8765) - or set FTT_PORT to the port it is on.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiPort = process.env.FTT_PORT ?? "8765";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": `http://127.0.0.1:${apiPort}`,
    },
  },
});
