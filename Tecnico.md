# Universidad UNE - Documentación Técnica de Migración Web
**Plan de Implementación y Especificaciones del Sistema - Versión Completa**

**Elaborado por:** Equipo de Mercadotecnia  
**Autor:** Ing. Eliezer Solano Martínez  
**Fecha:** Agosto 2025

---

## ÍNDICE

1. [Estado Actual del Proyecto](#1-estado-actual-del-proyecto)
2. [Problemática Identificada](#2-problemática-identificada)
3. [Solución Propuesta](#3-solución-propuesta)
4. [Plan de Migración](#4-plan-de-migración)
5. [Responsabilidades y Roles](#5-responsabilidades-y-roles)
6. [Timeline de Implementación](#6-timeline-de-implementación)
7. [Arquitectura Técnica](#7-arquitectura-técnica)
8. [Especificaciones de Infraestructura](#8-especificaciones-de-infraestructura)
9. [Sistema de Integración APIs](#9-sistema-de-integración-apis)
10. [Configuración del Servidor](#10-configuración-del-servidor)
11. [Análisis de Rendimiento](#11-análisis-de-rendimiento)
12. [Core Web Vitals y Métricas](#12-core-web-vitals-y-métricas)
13. [Integraciones Adicionales](#13-integraciones-adicionales)
14. [Desarrollo de Intranet Institucional](#14-desarrollo-de-intranet-institucional)

---

## 1. ESTADO ACTUAL DEL PROYECTO

### 1.1 Situación Previa a la Migración

**Plataforma Actual:** Odoo Website Builder  
**Estado:** Segundo intento de migración (primer intento falló el 11 de agosto 2025)  
**Problema Principal:** Esperando implementación de APIs de formularios y manejo de dominios

### 1.2 Stack Tecnológico de Desarrollo

**Framework Principal:** Astro 5.10
**Tecnologías Complementarias:**
- CSS Framework: TailwindCSS 4.1
- JavaScript: Vanilla + Splide.js para carruseles
- PDF Generation: PDF-lib para documentos dinámicos
- Build Tool: Vite (integrado en Astro)

---

## 2. PROBLEMÁTICA IDENTIFICADA

### 2.1 Limitaciones Críticas del Sistema Actual

**Problemas de Rendimiento Extremos:**
- Performance Mobile: 7/100 Lighthouse (crítico)
- Performance Desktop: 42/100 Lighthouse (deficiente)
- First Contentful Paint Mobile: 8.9 segundos (inaceptable)
- Largest Contentful Paint Mobile: 30.8 segundos (completamente inutilizable)
- Total Blocking Time Desktop: 730ms (impacta interactividad)

**Problemas Operacionales:**
- Inestabilidad del sistema: Caídas frecuentes del servicio Odoo
- Limitaciones de personalización: Restricciones severas en diseño y funcionalidad
- Abandono técnico histórico: Sitio constantemente con áreas de oportunidad sin atender

### 2.2 Impacto en Métricas de Conversión

**Problemas de Conversión Identificados:**
- Solo 10% de visitantes del formulario de contacto completan el envío
- Alta tasa de abandono por lentitud en móviles (70% de tráfico)
- Percepción institucional afectada por problemas técnicos

### 2.3 Problemas de Infraestructura

**Riesgo Crítico Identificado:**
- Ambigüedad en ownership del VPS Contabo actual
- Dependencia en infraestructura externa sin control administrativo claro
- Falta de aprovechamiento de Google VM ya disponible institucionalmente

---

## 3. SOLUCIÓN PROPUESTA

### 3.1 Estrategia de Separación Frontend/Backend

**Enfoque Arquitectónico:**
- Frontend: Astro (sitio estático optimizado) - Público
- Backend: Odoo ERP (mantiene funcionalidad interna) - Interno
- Integración: APIs REST desarrolladas por Xmarts bajo convenio TI

### 3.2 Beneficios de la nueva solución

**Mejoras de Performance Proyectadas:**
- Desktop: 42 → 87 Lighthouse (+107%)
- Mobile: 7 → 65 Lighthouse (+829%)
- First Contentful Paint Mobile: 8.9s → 2.5s (-72%)
- Largest Contentful Paint Mobile: 30.8s → 10.1s (-67%)

**Beneficios Operacionales:**
- Control total del código y modificaciones
- Reducción dramática de dependencia externa
- Mejora significativa en conversiones esperada (objetivo: ~15%)

### 3.3 Migración de Infraestructura a Google VM

**Ventajas de Google Virtual Machine:**
- Universidad UNE ya cuenta con plan institucional
- Nuevas instancias sin costo adicional
- Control administrativo completo
- Herramientas de monitoreo integradas
- Backup automático disponible
- Eliminación del riesgo de ownership

---

## 4. PLAN DE MIGRACIÓN

### 4.1 Fases de Implementación

#### Fase 1: Preparación (COMPLETADA)
- Desarrollo completo del sitio en Astro
- Implementación de diseño responsive optimizado
- Optimización de assets (imágenes WebP, videos comprimidos)
- Testing exhaustivo en ambiente de desarrollo

#### Fase 2: Integración API (EN PROGRESO)
- Formulario principal de contacto: IMPLEMENTADO Y FUNCIONAL
- Formulario agendar visita: PENDIENTE (desarrollo Xmarts)
- Formulario inscripción directa: PENDIENTE (desarrollo Xmarts)

#### Fase 3: Deploy y DNS Switch (PROGRAMADA para 29 Agosto)
- Configuración final del servidor
- Cambio de DNS coordinado
- Monitoreo intensivo post-migración
- Validación completa de funcionalidades

### 4.2 Consolidación de Dominios

**Estado Actual (11 dominios conocidos dispersos):**
```
www.universidad-une.com (principal)
www.une-enlinea.com (educación online)
www.vivetuuniversidad.com (portal estudiantil)
talento.universidad-une.com (RRHH)
blog.universidad-une.com (blog)
soporteescolar.universidad-une.com (soporte)
virtual.une-enlinea.com (campus virtual)
credenciales.universidad-une.com (certificados)
profesorado.universidad-une.com (docentes)
alumnado.universidad-une.com (estudiantes)
intranet.universidad-une.com (interno - pendiente)
```

**Consolidación Propuesta (6 sistemas optimizados):**
```
PORTAL PRINCIPAL CONSOLIDADO:
├── www.universidad-une.com (absorbe: vivetuuniversidad, blog, soporte)

SISTEMAS INDEPENDIENTES:
├── www.une-enlinea.com (educación a distancia)
├── intranet.universidad-une.com (sistemas internos + talento)
├── virtual.une-enlinea.com (Moodle)
├── credenciales.universidad-une.com (credenciales)
└── profesorado/alumnado.universidad-une.com (portales especializados)
```

### 4.3 Propuesta para Gestión de Contenido (Mini CMS)

**Propuesta de Arquitectura:**
Sistema interno para que el equipo de Mercadotecnia actualice contenido sin dependencia técnica.

**Características Propuestas:**
- Interface administrativa basada en React para edición visual
- Base de datos JSON almacenada en repositorio Git para versionado
- Generación estática automática con Astro tras cada cambio
- Gestión CRUD completa de programas académicos
- Configuración SEO independiente por página
- Sistema de versiones integrado con Git para trazabilidad

**Flujo de Trabajo Propuesto:**
Editor web → Modificación JSON → Build automático → Deploy (2-3 minutos)

**Beneficios del Mini CMS:**
- Autonomía completa para actualizaciones de contenido
- Reducción de dependencia técnica para cambios rutinarios
- Mantenimiento de performance (generación estática)
- Control de versiones y rollback capabilities

---

## 5. RESPONSABILIDADES Y ROLES

### 5.1 Asignación Detallada de Responsabilidades

#### Ing. Eliezer Solano Martínez (Desarrollador Frontend/Fullstack)
**Contexto:** Oficialmente contratado como Frontend Developer en Mercadotecnia, ejecutando responsabilidades de Fullstack/DevOps por necesidad institucional.

**Responsabilidades Técnicas:**
```yaml
Desarrollo:
  - Mantenimiento y evolución del código Astro/TailwindCSS
  - Implementación de nuevas funcionalidades solicitadas
  - Testing y QA integral de todos los cambios
  - Optimización continua de assets y performance

DevOps y Infraestructura:
  - Gestión completa del servidor (VPS/GCP)
  - Configuración y mantenimiento de Nginx
  - Gestión de certificados SSL/TLS
  - Implementación de estrategias de backup y recovery
  - Deployment y rollback procedures

Monitoreo y Análisis:
  - Configuración de Google Analytics 4 y Microsoft Clarity
  - Performance monitoring y configuración de alertas
  - SEO tracking y optimización continua
  - Error tracking, debugging y resolución de issues
```

#### Xmarts Consulting (Proveedor de APIs)
**Responsabilidades bajo Convenio TI:**
- Desarrollo de endpoints REST para integración con Odoo
- Mantenimiento y soporte técnico de APIs existentes
- Documentación técnica completa de todas las APIs
- Testing de integraciones y validación de funcionalidad

**Deliverables Específicos Pendientes:**
```yaml
Endpoint "Agendar Visita":
  - Validación completa de formulario
  - Integración con módulo de calendario Odoo
  - Sistema de confirmación automática vía email
  - Timeline: 2 semanas post-lanzamiento

Endpoint "Inscripción Directa":
  - Procesamiento de datos completos de estudiante
  - Sistema de upload y validación de documentos
  - Creación automática de expediente en Odoo
  - Workflow de seguimiento automatizado
  - Timeline: 4 semanas post-lanzamiento
```

---

## 6. TIMELINE DE IMPLEMENTACIÓN

### 6.1 Cronograma Crítico

#### Miércoles 28 Agosto 2025
```yaml
Actividades Matutinas (9:00-12:00):
  - Testing final completo en ambiente staging
  - Validación de 100+ redirects SEO configurados
  - Verificación de responsive design en todos dispositivos target
  - Testing de formulario principal con casos edge

Actividades Vespertinas (14:00-18:00):
  - Preparación de documentación post-lanzamiento
  - Configuración avanzada de sistemas de monitoreo
  - Coordinación final con Xmarts para APIs pendientes
  - Preparación de plan de comunicación interna
```

#### Jueves 29 Agosto 2025 - DÍA DEL DEPLOYMENT
```yaml
Pre-Launch Phase (8:00-10:00):
  - Backup final y completo del sistema actual
  - Verificación de última hora de todas las integraciones críticas
  - Comunicación oficial a todos los stakeholders sobre el cambio inminente
  - Confirmación de disponibilidad de equipo de respuesta

Launch Window (10:00-12:00):
  - Ejecución del cambio de DNS programado
  - Monitoreo activo y continuo durante la primera hora crítica
  - Testing inmediato de funcionalidades críticas en producción
  - Validación de métricas de performance en tiempo real

Post-Launch Monitoring (12:00-18:00):
  - Monitoreo intensivo de métricas de performance y disponibilidad
  - Validación exhaustiva de formularios en ambiente de producción
  - Respuesta inmediata a cualquier issue identificado
  - Comunicación oficial de éxito del deployment a dirección
```

---

## 7. ARQUITECTURA TÉCNICA

### 7.1 Separación de Responsabilidades

```
┌─────────────────────────┐    ┌─────────────────────────┐
│     FRONTEND WEB        │    │     BACKEND ERP         │
│      (Público)          │    │     (Interno)           │
├─────────────────────────┤    ├─────────────────────────┤
│ • Astro 5.10            │◄──►│ • Odoo ERP              │
│ • Sitio Estático        │    │ • Módulos Internos      │
│ • Google VM / VPS       │    │ • Xmarts (APIs)         │
│ • Nginx + SSL           │    │ • CRM/Leads             │
└─────────────────────────┘    └─────────────────────────┘
```

### 7.2 Ventajas de la Arquitectura Estática

**Performance:**
- Eliminación total de consultas a base de datos en runtime
- Archivos servidos directamente desde nginx optimizado
- Optimización automática de assets con build process
- Lazy loading implementado para componentes no críticos

**Seguridad:**
- Superficie de ataque minimizada (solo archivos estáticos)
- Eliminación de código ejecutable en servidor web público
- SSL/TLS con certificados Let's Encrypt renovación automática
- Ausencia completa de vulnerabilidades típicas de CMS/plugins

**Escalabilidad:**
- Capacidad CDN nativa para distribución global
- Manejo eficiente de picos de tráfico sin degradación
- Recursos de servidor mínimos requeridos (costo-eficiente)
- Horizontal scaling simple mediante load balancers

---

## 8. ESPECIFICACIONES DE INFRAESTRUCTURA

### 8.1 Servidor Actual (VPS Contabo) - Temporal

**Especificaciones Técnicas:**
- CPU: 3 vCPU AMD EPYC @ 2.800GHz
- RAM: 8GB DDR4
- Storage: 75GB NVMe SSD (alta velocidad)
- Bandwidth: 32TB mensual (más que suficiente)
- OS: Ubuntu 24.04.3 LTS (soporte extendido)
- Costo: $4.95 USD/mes

### 8.2 Migración Planificada: Google Virtual Machine

**Especificaciones Equivalentes Propuestas:**
```yaml
machine_type: e2-standard-2
cpu: 2 vCPU (suficiente para sitio estático)
memory: 8GB RAM 
disk: 75GB SSD persistent
os: ubuntu-2404-lts
region: us-central1 (latencia óptima)
costo: $0 adicional (incluido en plan institucional)
```

**Justificación Técnica de la Migración:**
- Eliminación completa del riesgo de ownership
- Aprovechamiento de infraestructura ya disponible
- Herramientas avanzadas de monitoreo incluidas
- Backup automático y disaster recovery integrado
- Mayor confiabilidad y SLA empresarial

### 8.3 Plan Detallado de Migración VPS → Google VM

#### Fase de Preparación (1 semana pre-migración)
```yaml
Configuración GCP:
  - Provisión de VM con especificaciones equivalentes
  - Configuración de networking y firewall rules
  - Setup de certificados SSL
  - Configuración de backup automático

Testing de Migración:
  - Deploy completo en ambiente GCP staging
  - Testing de performance comparativo
  - Validación de DNS y routing
  - Load testing en nuevo environment
```

#### Fase de Ejecución (ventana de mantenimiento)
```yaml
Migración de Datos:
  - Sync final de archivos estáticos
  - Backup completo pre-migración
  - DNS switch coordinado
  - Validación post-migración inmediata

Rollback Plan:
  - DNS revert en <5 minutos si falla
  - Backup del VPS actual por 30 días
  - Procedimiento documentado paso a paso
```

---

## 9. SISTEMA DE INTEGRACIÓN APIs

### 9.1 API Principal de Contacto (OPERATIVA)

**Endpoint Actual:** `https://intranet.universidad-une.com/api/createleads`

**Estructura de Payload:**
```javascript
const payload = {
  nombre: string,
  apellido_p: string,
  apellido_m: string,
  correo: string (email validation),
  telefono: string,
  nivel_educativo: enum,
  plantel_interes: enum,
  programa_interes: string,
  modalidad: enum,
  medio: "Página web" (fixed)
};
```

### 9.2 APIs Pendientes para Funcionalidad Completa

#### Formulario Agendar Visita
**Integración Objetivo:** Módulo Citas en Odoo (separado del CRM principal)
**Justificación:** Los visitantes que soliciten tours del campus se registrarán en el sistema de citas separado del CRM principal, ya que una visita no constituye automáticamente un prospecto calificado.

**PLAN DE CONTINGENCIA:**
Si Xmarts no puede desarrollar la integración con el módulo Citas en el tiempo necesario, el formulario enviará la información al CRM como leads regulares. Aunque esto generará leads basura (visitantes no calificados mezclados con prospectos reales), permitirá funcionalidad inmediata mientras se desarrolla la solución óptima posteriormente.

**Timeline:** 2 semanas post-lanzamiento  
**Responsable:** Xmarts bajo convenio TI

#### Formulario Inscripción Directa
**Funcionalidad:** Sistema completo de matriculación automática en módulo Alumnado de Odoo
**Consideración Administrativa:** Este proceso requiere clarificación administrativa del flujo cuando un prospecto con ficha CRM existente procede directamente a matriculación, determinando si fusionar información o eliminar el registro previo.

**Funcionalidades Requeridas:**
- Procesamiento completo de datos personales y académicos
- Sistema robusto de upload y validación de documentos
- Creación automática de expediente en Odoo con número único
- Workflow automatizado de seguimiento de inscripción
- Integración con sistema de pagos (futuro)

**Timeline:** 4 semanas post-lanzamiento  
**Responsable:** Xmarts bajo convenio TI

### 9.3 Gestión de Errores y Fallbacks

**Estrategia de Contingencia:**
- Logging completo de errores para debugging
- Analytics tracking de fallos para métricas
- Mensaje user-friendly sin exposición de errores técnicos

---

## 10. CONFIGURACIÓN DEL SERVIDOR

### 10.1 Configuración Nginx Optimizada

```nginx
# /etc/nginx/sites-available/universidad-une.com
server {
    listen 443 ssl http2;
    server_name www.universidad-une.com universidad-une.com 
                www.vivetuuniversidad.com vivetuuniversidad.com;
    
    root /var/www/UNE/dist;
    index index.html index.htm;
    
    # Incluir 100+ redirects SEO
    include /etc/nginx/nginx-redirects.conf;
    
    # SPA-like behavior para rutas dinámicas
    location / {
        try_files $uri $uri/ $uri.html /index.html;
    }
    
    # Optimización agresiva de assets estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|webp|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }
    
    # SSL Configuration con grade A+
    ssl_certificate /etc/letsencrypt/live/vivetuuniversidad.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vivetuuniversidad.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```

### 10.2 Sistema de Redirects SEO

**100+ Redirects Configurados:**
- Páginas principales: /contacto, /licenciaturas, /maestrias, /bachilleratos
- Programas específicos con patterns regex para escalabilidad
- Campus redirects para consolidación
- Blog y noticias para unificación de contenido

### 10.3 Deployment Scripts Automatizados

**Script Principal de Deployment:**
- Backup automático pre-deployment
- Git pull con validación de errores
- Build con validación de integridad
- Rollback automático en caso de fallo
- Cleanup de backups antiguos (retención 5 versiones)

---

## 11. ANÁLISIS DE RENDIMIENTO

### 11.1 Comparativo de Performance

#### Desktop Performance
| Métrica | Antes (Odoo) | Después (Astro) | Mejora |
|---------|--------------|-----------------|--------|
| Lighthouse Score | 42/100 | 87/100 | +107% |
| First Contentful Paint | 1.5s | 0.3s | -80% |
| Largest Contentful Paint | 2.7s | 1.8s | -33% |
| Total Blocking Time | 730ms | 30ms | -96% |
| Cumulative Layout Shift | 0.098 | 0.002 | -98% |

#### Mobile Performance  
| Métrica | Antes (Odoo) | Después (Astro) | Mejora |
|---------|--------------|-----------------|--------|
| Lighthouse Score | 7/100 | 65/100 | +829% |
| First Contentful Paint | 8.9s | 2.5s | -72% |
| Largest Contentful Paint | 30.8s | 10.1s | -67% |
| Total Blocking Time | 1,780ms | 110ms | -94% |
| Cumulative Layout Shift | 0.532 | 0.0 | -100% |

### 11.2 Optimizaciones Implementadas

**Assets Optimization:**
- 768 imágenes convertidas a formato WebP con compresión optimizada
- 27 videos optimizados en formato WebM/MP4 con calidad balanceada
- Lazy loading implementado para todos los elementos no críticos
- Critical CSS inlined para above-the-fold content

**JavaScript Optimization:**
- Componentes pesados cargados condicionalmente con Intersection Observer
- Bundle splitting para reducir JavaScript inicial
- Preloading de recursos críticos
- Service Worker para caching avanzado (futuro)

---

## 12. CORE WEB VITALS Y MÉTRICAS

### 12.1 Core Web Vitals - Estado Actual vs Objetivo

**Largest Contentful Paint (LCP):**
- Antes: 30.8s (móvil) / 2.7s (desktop) - CRÍTICO
- Después: 10.1s (móvil) / 1.8s (desktop) - ACEPTABLE
- Objetivo futuro: <2.5s (móvil) / <1.2s (desktop)

**First Input Delay (FID) / Interaction to Next Paint (INP):**
- Antes: >300ms - Interactividad muy pobre
- Después: <100ms - Interactividad buena
- Objetivo: <100ms consistente

**Cumulative Layout Shift (CLS):**
- Antes: 0.532 (móvil) / 0.098 (desktop) - Muy pobre
- Después: 0.0 (móvil) / 0.002 (desktop) - Excelente
- Objetivo: <0.1 mantenido

### 12.2 Monitoreo Continuo

**Google Analytics 4:**
- Enhanced ecommerce tracking para programas de interés
- Custom events para form submissions y conversiones
- Real User Monitoring (RUM) para Core Web Vitals

**Microsoft Clarity:**
- Heatmaps para identificar patrones de uso
- Session recordings para análisis cualitativo de UX
- Funnel analysis para optimización de conversión

**Uptime Monitoring:**
- Health checks automatizados cada 5 minutos
- Alertas inmediatas en caso de downtime
- Performance threshold alerts para degradación

---

## 13. INTEGRACIONES ADICIONALES

### 13.1 Bolsa de Trabajo de Talento

**Necesidad Identificada:** Nueva sección en página principal para aplicaciones laborales directas que surge de la necesidad identificada por Mercadotecnia al asumir la gestión integral del sitio web.

**Información Capturada:**
- **Datos personales completos:** nombres, apellidos, género, estado civil
- **Información de contacto:** teléfono, correo, fecha de nacimiento
- **Datos profesionales:** escolaridad, especialización, experiencia
- **Plantel de interés laboral**
- **Canal de conocimiento:** Facebook, Indeed, recomendación, etc.
- **Documentos:** perfil LinkedIn y currículum vitae

**Proceso de Integración:**
Información enviada directamente al área RRHH en Odoo para evaluación según procedimientos institucionales de contratación.

**Responsable:** 
- Xmarts (desarrollo API)
- Ing. Eliezer Solano (implementación frontend)

---

## 14. DESARROLLO DE INTRANET INSTITUCIONAL

### 14.1 Portal del Empleado UNE

**Dominio:** intranet.universidad-une.com  
**Objetivo:** Centralizar el acceso digital para empleados, absorbiendo y expandiendo las funcionalidades de talento.universidad-une.com

**Funcionalidades Principales:**
- Información RRHH centralizada (políticas, beneficios, capacitaciones)
- Sistema de tickets departamentales
- Comunicados oficiales y actualizaciones institucionales
- Portal de acceso a módulos internos de Odoo

### 14.2 Sistema de Tickets por Departamentos

**Estrategia de Implementación:**
Se consultará primero con Xmarts si pueden desarrollar APIs para los 12 formularios departamentales. En caso de no ser viable por tiempos o recursos, se desarrollarán usando Odoo Website Builder que ofrece formularios incrustados nativos, agilizando la implementación. La intranet mantendrá dependencia de Odoo temporalmente para funcionalidad inmediata.

#### Creatividad y Diseño (4 formularios)
- **Diseño Digital:** Solicitudes de material gráfico digital
- **Diseño Impreso:** Material promocional físico
- **Audiovisual:** Contenido multimedia y video
- **Cobertura foto-audiovisual de eventos:** Documentación de actividades institucionales

#### Mercadotecnia (5 formularios)
- **Comunicación institucional:** Estrategias de comunicación externa
- **Mercadotecnia tradicional:** Campañas publicitarias convencionales
- **Comunicados oficiales UNE campus digital:** Información oficial para plataformas digitales
- **Solicitudes de redes sociales:** Contenido para medios sociales
- **Incidencias web:** Reportes de problemas o mejoras del sitio web

#### Recursos Humanos (3 formularios)
- **Solicitud de permisos RRHH:** Gestión de ausencias y permisos
- **Formulario de baja RRHH:** Proceso de desvinculación laboral
- **Becas para empleado UNE y familiares:** Programa de beneficios educativos

#### Sistemas TI
**Cambio de Proceso:** Transición a comunicación directa por correo electrónico, eliminando formularios web para soporte técnico en favor de atención personalizada.

### 14.3 Arquitectura Técnica de la Intranet

```
┌─────────────────────────────────────┐
│        INTRANET UNE                 │
│   (intranet.universidad-une.com)    │
├─────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────┐ │
│ │   Portal    │ │  Tickets Dept.  │ │
│ │  Empleado   │ │  (12 formas)    │ │
│ └─────────────┘ └─────────────────┘ │
├─────────────────────────────────────┤
│         Backend Integration         │
│    Odoo Website Builder (temp)      │
│         ↓ (futuro)                  │
│       APIs Xmarts                   │
└─────────────────────────────────────┘
```

**Responsable:** 
- Xmarts (si es viable desarrollo de APIs)
- Ing. Eliezer Solano (implementación alternativa con Odoo Website Builder)

---

## APÉNDICES

### Apéndice A: Especificaciones Técnicas Detalladas

**Build Configuration (astro.config.mjs):**
```javascript
export default defineConfig({
  output: 'static',
  integrations: [
    tailwind(),
    compress({ CSS: true, HTML: true, Image: false, JavaScript: true, SVG: true })
  ],
  vite: {
    build: {
      cssMinify: 'lightningcss',
      rollupOptions: {
        output: {
          assetFileNames: 'assets/[name]-[hash][extname]',
          chunkFileNames: 'assets/[name]-[hash].js',
          entryFileNames: 'assets/[name]-[hash].js'
        }
      }
    }
  }
});
```

### Apéndice B: Lista Completa de Redirects SEO

**Sample de Redirects Configurados (100+ total):**
```nginx
# Programas académicos principales
rewrite ^/licenciaturas/administracion/?$ /licenciaturas/administracion-de-empresas permanent;
rewrite ^/maestrias/educacion/?$ /maestrias/maestria-en-educacion permanent;
rewrite ^/bachilleratos/?$ /bachillerato-tecnologico permanent;

# Campus consolidation
rewrite ^/campus/guadalajara/?$ /campus/zapopan permanent;
rewrite ^/campus/.*$ /contacto permanent;

# Blog y noticias
rewrite ^/blog/(.*)$ /noticias/$1 permanent;
rewrite ^/noticias/old/(.*)$ /noticias/$1 permanent;
```

### Apéndice C: Contact Information y Escalation Matrix

**Escalation Matrix para Incidentes:**
```yaml
Severidad 1 (Crítico):
  - Primary: Ing. Eliezer Solano (immediato)
  - Secondary: Director TI UNE (15 min)
  - Escalation: Dirección General (30 min)

Severidad 2-3:
  - Primary: Ing. Eliezer Solano (business hours)
  - Secondary: Equipo Mercadotecnia
  - Escalation: Director TI UNE (si no se resuelve en 4hrs)

APIs Issues:
  - Primary: Xmarts Support Team
  - Secondary: Ing. Eliezer Solano  
  - Escalation: Convenio TI UNE
```

### Apéndice D: Checklist de Go-Live

**Pre-Launch Checklist (24 horas antes):**
- [ ] Testing completo en staging environment
- [ ] Validación de todos los redirects SEO
- [ ] Verificación de formularios y APIs
- [ ] Backup completo del sistema actual
- [ ] Coordinación con equipo de TI para cambio DNS
- [ ] Preparación de plan de comunicación
- [ ] Configuración de monitoreo intensivo

**Launch Day Checklist:**
- [ ] Ejecución de cambio DNS
- [ ] Validación inmediata de funcionalidades críticas
- [ ] Verificación de métricas de performance
- [ ] Testing de formularios en producción
- [ ] Monitoreo de logs de errores
- [ ] Comunicación de éxito a stakeholders

**Post-Launch Checklist (primera semana):**
- [ ] Monitoreo diario de métricas de performance
- [ ] Análisis de comportamiento de usuarios
- [ ] Identificación y resolución de issues menores
- [ ] Optimizaciones basadas en datos reales
- [ ] Preparación de reporte de éxito

### Apéndice E: Flujo de Tickets Departamentales

**Proceso de Solicitud Interna:**
```
Empleado → Formulario Departamental → Sistema Tickets → Asignación → Resolución → Cierre
     ↓                ↓                    ↓              ↓             ↓          ↓
   Login         Validación           Odoo/API      Responsable    Seguimiento   Feedback
```

**Estados de Ticket:**
- **Nuevo:** Solicitud recién creada
- **En Progreso:** Asignado y en desarrollo
- **En Revisión:** Completado, pendiente aprobación
- **Resuelto:** Finalizado satisfactoriamente
- **Cerrado:** Confirmado por solicitante

### Apéndice F: Roadmap de Desarrollo Futuro



**Fase 5: Mini CMS Completo (6-12 meses)**
- Interface visual completa para gestión de contenido
- Sistema de versiones y rollback
- Preview de cambios antes de publicación
- Gestión de usuarios y permisos


---

**Especificaciones Técnicas Finales:**
- **Framework:** Astro 5.10 + TailwindCSS 4.1
- **Servidor:** Ubuntu 24.04.3, Nginx optimizado, SSL/TLS A+
- **Performance:** 87/100 desktop, 65/100 móvil (objetivos alcanzados)
- **Assets:** 768 imágenes WebP, 27 videos optimizados, 557MB build total
- **Uptime esperado:** 99.97%+ con monitoreo automatizado
- **Security:** Grade A+ SSL, comprehensive firewall, automated backups
- **Recovery:** RTO <15min para críticos, RPO <1 hora
- **Monitoring:** Real-time dashboards, automated alerting, weekly reports

**Arquitectura de Integración Final:**
```
┌─────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA DIGITAL UNE                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   SITIO WEB     │  │    INTRANET     │  │   SISTEMAS  │  │
│  │   PRINCIPAL     │  │   EMPLEADOS     │  │  INTERNOS   │  │
│  │                 │  │                 │  │             │  │
│  │ • Astro 5.10    │  │ • Portal RRHH   │  │ • Odoo ERP  │  │
│  │ • Público       │  │ • Tickets Dept. │  │ • CRM/Lead  │  │
│  │ • Optimizado    │  │ • Comunicación  │  │ • Alumnado  │  │
│  │ • SEO           │  │ • Accesos       │  │ • Finanzas  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│           │                     │                   │       │
│           └─────────────────────┼───────────────────┘       │
│                                 │                           │
│              ┌─────────────────────────────────┐            │
│              │         APIs XMARTS             │            │
│              │                                 │            │
│              │ • Formulario Contacto ✓         │            │
│              │ • Agendar Visita (pending)      │            │
│              │ • Inscripción Directa (pending) │            │
│              │ • Bolsa Trabajo (nuevo)         │            │
│              │ • Tickets Sistema (opcional)    │            │
│              └─────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

**Métricas de Éxito Proyectadas:**
- **Performance:** Mejora +829% móvil, +107% desktop
- **Conversión:** Objetivo 15% (vs 10% actual)
- **Uptime:** 99.97%+ (vs 95% actual estimado)
- **Loading Time:** -72% First Contentful Paint móvil
- **User Experience:** CLS 0.0 (eliminación completa layout shift)
- **SEO:** Core Web Vitals "Good" en todas las métricas
- **Maintenance:** -90% dependencia externa para cambios

**Timeline Consolidado:**
- **29 Agosto 2025:** Go-live sitio principal
- **Septiembre 2025:** APIs pendientes (Agendar Visita, Inscripción)
- **Octubre 2025:** Bolsa de Trabajo integrada
- **Noviembre 2025:** Intranet institucional completa
- **Diciembre 2025:** Migración completa a Google VM
- **Q1 2026:** Mini CMS y optimizaciones avanzadas

---

**Ing. Eliezer Solano Martínez - Departamento de Mercadotecnia**  
**Universidad UNE - Agosto 2025**

---

*Documento técnico completo que incluye especificaciones de migración web, integraciones de APIs, desarrollo de intranet institucional, y roadmap de implementación para el ecosistema digital completo de Universidad UNE.*