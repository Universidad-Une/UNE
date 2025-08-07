// src/pages/sitemap.xml.ts
import type { APIRoute } from 'astro';

// Define tus rutas principales aquí
const staticRoutes = [
  '',
  'licenciaturas',
  'posgrados',
  'educacion-continua',
  'admisiones',
  'nosotros',
  'contacto',
  'campus',
  'biblioteca',
  'servicios-estudiantiles',
];

// Rutas dinámicas - agregar según tu estructura
const dynamicRoutes = [
  // Ejemplo: 'licenciaturas/administracion',
  // 'licenciaturas/derecho',
  // etc.
];

export const GET: APIRoute = async ({ site }) => {
  const baseUrl = site?.href || 'https://une.edu.mx';
  
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${staticRoutes.map(route => `
  <url>
    <loc>${baseUrl}${route}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>${route === '' ? 'daily' : 'weekly'}</changefreq>
    <priority>${route === '' ? '1.0' : '0.8'}</priority>
  </url>`).join('')}
  ${dynamicRoutes.map(route => `
  <url>
    <loc>${baseUrl}${route}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>`).join('')}
</urlset>`;

  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600'
    }
  });
};