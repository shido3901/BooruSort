import { defineConfig } from 'vite';

// https://vitejs.dev/config
export default {
  build: {
    rollupOptions: {
     
      external: ['better-sqlite3'],
    },
  },
};
