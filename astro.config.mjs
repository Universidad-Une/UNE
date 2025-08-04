// @ts-check
import { defineConfig } from 'astro/config';
import path from 'path';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  // Configuración específica para Cloudflare Pages
  output: 'static', // Asegura generación estática
  // site: omitido - Cloudflare Pages maneja las URLs automáticamente
  base: '/', // Base path (ajustar si usas subdirectorio)
  
  // Configuración de build optimizada
  build: {
    format: 'directory', // Genera directorios con index.html
    inlineStylesheets: 'auto'
  },
  
  // Configuración de servidor para desarrollo
  server: {
    port: 3000,
    host: true
  },
  
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        // Alias principal
        '@': path.resolve('./src'),
        
        // Alias específicos para mejor organización
        '@assets': path.resolve('./src/assets'),
        '@components': path.resolve('./src/components'),
        '@layouts': path.resolve('./src/layouts'),
        '@utils': path.resolve('./src/utils'),
        '@pages': path.resolve('./src/pages'),
        '@helpers': path.resolve('./src/helpers'),
        
        // Alias para subcarpetas de componentes
        '@ui': path.resolve('./src/components/ui'),
        '@layout': path.resolve('./src/components/layout'),
        '@sections': path.resolve('./src/components/sections'),
        '@features': path.resolve('./src/components/features'),
        
        // Alias para assets específicos
        '@images': path.resolve('./src/assets/images'),
        '@logos': path.resolve('./src/assets/Logos'),
        '@icons': path.resolve('./src/assets/icons'),
        
        // Alias para tipos si usas TypeScript
        '@types': path.resolve('./src/types')
      }
    },
    
    // Optimizaciones adicionales para Cloudflare
    build: {
      rollupOptions: {
        output: {
          manualChunks: undefined,
        }
      }
    }
  }
});