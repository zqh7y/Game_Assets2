import { defineConfig } from 'vite';

export default defineConfig({
  // Relative URLs so the build works from any folder.
  base: './',
  server: {
    host: true,
    // The brawler sheets are imported straight from the repo's animations/ folder.
    fs: { allow: ['..'] },
  },
  build: {
    // Phaser alone is over the default 500 kB warning.
    chunkSizeWarningLimit: 2000,
  },
});
