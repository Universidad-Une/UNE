# Universidad UNE - Sitio Web Oficial

Sitio web oficial de Universidad UNE, una institución educativa mexicana con 30 años de trayectoria bajo el lema "30 Años Creyendo en Ti".

## 🌐 Demo

**Sitio en vivo:** [vivetuuniversidad.com](une-demo.pages.dev)

## 🎓 Acerca de Universidad UNE

Universidad UNE es una institución educativa integral que ofrece múltiples niveles de educación:

- **Educación Básica:** Primaria y Secundaria
- **Educación Media Superior:** Bachillerato General y BIS (Bachillerato Internacional)
- **Educación Superior:** Licenciaturas en Ingeniería, Medicina, Negocios, Derecho, y más
- **Posgrados:** Maestrías especializadas
- **Educación Continua:** Programas de actualización profesional

### 🏢 Sistema Multi-Campus

La universidad opera en múltiples campus en Jalisco, México:

**Área Metropolitana de Guadalajara:**
- Centro, Centro Médico, Milenio, Chapultepec, Tesistán, Tlajomulco, Tlaquepaque, Tonalá, Zapopan, Plaza del Sol

**Puerto Vallarta:**
- Campus Puerto Vallarta, Av. México, Caracol, Las Juntas

**Otros campus:**
- Tepatitlán

## 🔄 Migración desde Odoo Website

Este proyecto representa una migración completa desde Odoo Website Builder a Astro, motivada por:

### Problemas del sistema anterior:
- **Limitaciones de rendimiento:** Tiempos de carga lentos
- **Falta de flexibilidad:** Limitaciones severas en personalización
- **Dominios fragmentados:** `vivetuuniversidad` era un dominio separado

### Beneficios obtenidos:
- ✅ **Rendimiento mejorado:** Sitio estático optimizado
- ✅ **Mayor flexibilidad:** Control total sobre diseño y funcionalidad
- ✅ **Consolidación:** Unificación de todos los dominios y contenidos
- ✅ **Mantenimiento independiente:** Reducción de dependencias técnicas
- ✅ **SEO optimizado:** Mejor posicionamiento en buscadores

## 💻 Stack Tecnológico

### Frontend
- **Astro 5.10** - Generador de sitios estáticos
- **TailwindCSS 4.1** - Framework de CSS
- **JavaScript/TypeScript** - Lógica del cliente
- **Splide.js** - Carruseles y sliders
- Primer commit - 25 jun. 2025

### Herramientas y Librerías
- **PDF-lib** - Generación de documentos PDF
- **Microsoft Clarity** - Analytics de comportamiento
- **Google Analytics** - Métricas de tráfico

### Deploy y Hosting
- **VPS con Nginx** - Servidor actual con sistema de redirects
- **Cloudflare Pages** - Planeado para migración futura (sujeto a aprobación de TI)

## 📊 Rendimiento y Core Web Vitals

### Lighthouse Scores

**Desktop:**
- 🚀 Rendimiento: **94/100**
- ♿ Accesibilidad: **100/100**
- 🔧 Mejores Prácticas: **100/100**
- 📈 SEO: **88/100**

**Mobile:**
- 🚀 Rendimiento: **60/100***
- ♿ Accesibilidad: **96/100**
- 🔧 Mejores Prácticas: **100/100**
- 📈 SEO: **91/100**

### Métricas Core Web Vitals

**Desktop:**
- First Contentful Paint: **0.6s**
- Largest Contentful Paint: **1.6s**
- Total Blocking Time: **60ms**
- Cumulative Layout Shift: **0.002**

**Mobile:**
- First Contentful Paint: **4.3s**
- Largest Contentful Paint: **10.6s**
- Total Blocking Time: **10ms**
- Cumulative Layout Shift: **0.002**

*\*El rendimiento móvil se ve afectado por el video hero y slider de imágenes solicitados por el área administrativa. Sin estos elementos, el score sería aproximadamente 90+.*

## 🎯 Características Principales

### Funcionalidades del Sitio
- 🏫 **Selector de Campus:** Sistema dinámico de selección por ubicación
- 📚 **Catálogo de Programas:** Información completa de todas las carreras
- 📄 **Generador de PDFs:** Creación dinámica de documentos informativos
- 📱 **Diseño Responsivo:** Optimizado para todos los dispositivos
- 🎨 **Contenido Dinámico:** Información actualizable por campus y programa

### Modalidades de Estudio
- **Presencial** - Clases en campus
- **Semiescolarizada** - Modalidad híbrida
- **Sabatina** - Clases los sábados
- **En línea** - Programas completamente virtuales

### Programas Destacados
- **Ingenierías:** Desarrollo de Software, Inteligencia de Datos y Ciberseguridad, Civil, Mecánica
- **Ciencias de la Salud:** Odontología, Enfermería, Nutrición, Psicología
- **Negocios:** Administración, Mercadotecnia, Negocios Internacionales
- **Otras especialidades:** Derecho, Arquitectura, Gastronomía, Diseño Gráfico

## 🚀 Instalación y Desarrollo

### Requisitos Previos
- Node.js (versión 18+)
- npm o yarn

### Instalación
```bash
# Clonar el repositorio
git clone [https://github.com/Universidad-Une/UNE.git]
cd UNE

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Build para producción
npm run build
```

### Scripts Disponibles
```bash
npm run dev          # Servidor de desarrollo
npm run build        # Build de producción
npm run preview      # Vista previa del build
npm run astro        # Comandos de Astro CLI
```

## 📁 Estructura del Proyecto

```
une-website/
├── src/
│   ├── components/     # Componentes reutilizables
│   ├── layouts/        # Layouts de página
│   ├── pages/          # Páginas del sitio
│   ├── styles/         # Estilos globales
│   └── utils/          # Utilidades y helpers
├── public/             # Assets estáticos
├── astro.config.mjs    # Configuración de Astro
└── tailwind.config.js  # Configuración de Tailwind
```



## 🚢 Deploy

### Configuración Actual (VPS + Nginx)
El sitio actualmente se despliega en un VPS con configuración Nginx que incluye:
- Redirects automáticos para URLs legacy
- Optimización de assets estáticos
- Configuración SSL

### Migración Planeada
- **Cloudflare Pages:** Pendiente de aprobación del departamento de TI
- **Beneficios esperados:** CDN global, mejor rendimiento, deploy automático

## 🤝 Contribución

### Guidelines de Desarrollo
1. Seguir las convenciones de código establecidas
2. Probar en múltiples dispositivos antes de hacer push
3. Optimizar imágenes y assets
4. Mantener accesibilidad en mente (WCAG 2.1)

### Proceso de Updates
1. Crear rama feature desde `main`
2. Desarrollar y probar localmente
3. Crear Pull Request con descripción detallada
4. Review y merge tras aprobación

## 📈 Monitoreo y Analytics

- **Microsoft Clarity:** Mapas de calor y grabaciones de sesión
- **Google Analytics:** Métricas de tráfico y conversión
- **Core Web Vitals:** Monitoreo continuo de rendimiento

## 🐛 Problemas Conocidos

- **Rendimiento móvil:** Impactado por video hero (decisión administrativa)
- **LCP móvil:** Optimización en progreso para dispositivos de gama baja


## 📞 Contacto

**Universidad UNE**
- Sitio web: [universidad-une.com](https://universidad-une.com)
- Información de contacto disponible en el sitio web

---

### 🏆 Logros del Proyecto

- ✅ Migración exitosa sin pérdida de funcionalidad
- ✅ Mejora significativa en rendimiento desktop
- ✅ Consolidación de múltiples dominios
- ✅ Scores perfectos en accesibilidad y mejores prácticas
- ✅ Implementación exitosa de analytics avanzados

---

*Desarrollado con ❤️ para Universidad UNE - 30 Años Creyendo en Ti*