import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: '.',
  build: {
    outDir: '../dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        login: resolve(__dirname, 'login.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        admin: resolve(__dirname, 'admin.html'),
        batch: resolve(__dirname, 'batch.html'),
        collab: resolve(__dirname, 'collab.html'),
        profile: resolve(__dirname, 'profile.html'),
        reports: resolve(__dirname, 'reports.html'),
        settings: resolve(__dirname, 'settings.html'),
        help: resolve(__dirname, 'help.html'),
        landing: resolve(__dirname, 'landing.html'),
        generate: resolve(__dirname, 'generate.html'),
        status: resolve(__dirname, 'status.html'),
        signup: resolve(__dirname, 'signup.html'),
        notfound: resolve(__dirname, '404.html')
      },
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
});