import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: true, // bind 0.0.0.0, not just localhost — required to be reachable from outside a container
    watch: {
      // Docker Desktop's bind-mounted filesystem doesn't reliably forward
      // native file-change events into the container (confirmed: edits
      // sat un-picked-up until a full container restart). Polling costs a
      // bit of CPU but actually works. Harmless outside Docker too.
      usePolling: true,
    },
  },
})
