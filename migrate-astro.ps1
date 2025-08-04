# ================================
# MIGRACION DE ESTRUCTURA ASTRO CON POWERSHELL
# ================================

# Paso 1: Crear la nueva estructura de directorios
Write-Host "Creando nueva estructura de directorios..." -ForegroundColor Green

# Crear directorios principales
$directories = @(
    "src\components\layout",
    "src\components\ui", 
    "src\components\sections\home",
    "src\components\sections\blog",
    "src\components\sections\admissions",
    "src\components\sections\programs",
    "src\components\sections\shared",
    "src\components\features\search",
    "src\components\features\contact",
    "src\components\features\navigation",
    "src\layouts",
    "src\pages\blog",
    "src\pages\admissions",
    "src\pages\programs",
    "src\pages\programs\[category]",
    "src\pages\programs\[program]",
    "src\pages\about",
    "src\pages\contact",
    "src\utils"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Creado: $dir" -ForegroundColor Cyan
    } else {
        Write-Host "Ya existe: $dir" -ForegroundColor Yellow
    }
}

Write-Host "Estructura de directorios creada exitosamente!" -ForegroundColor Green

# Paso 2: Mover componentes existentes
Write-Host "Moviendo componentes a su nueva ubicacion..." -ForegroundColor Green

# Funcion para mover archivos si existen
function Move-ComponentIfExists {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$ComponentName
    )
    
    if (Test-Path $Source) {
        # Crear directorio destino si no existe
        $destDir = Split-Path $Destination -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force
        }
        
        Move-Item -Path $Source -Destination $Destination -Force
        Write-Host "Movido: $ComponentName" -ForegroundColor Green
    } else {
        Write-Host "No encontrado: $ComponentName" -ForegroundColor Yellow
    }
}

# Layout components
Move-ComponentIfExists "src\components\Header.astro" "src\components\layout\Header.astro" "Header"
Move-ComponentIfExists "src\components\Footer.astro" "src\components\layout\Footer.astro" "Footer"

# UI components
Move-ComponentIfExists "src\components\Tabs.astro" "src\components\ui\Tabs.astro" "Tabs"

# Home sections
Move-ComponentIfExists "src\components\Hero.astro" "src\components\sections\home\Hero.astro" "Hero"
Move-ComponentIfExists "src\components\DescubreUNE.astro" "src\components\sections\home\DescubreUNE.astro" "DescubreUNE"
Move-ComponentIfExists "src\components\SobreUNE.astro" "src\components\sections\home\SobreUNE.astro" "SobreUNE"
Move-ComponentIfExists "src\components\DentroUNE.astro" "src\components\sections\home\DentroUNE.astro" "DentroUNE"
Move-ComponentIfExists "src\components\Cards_Niveles.astro" "src\components\sections\home\Cards_Niveles.astro" "Cards_Niveles"
Move-ComponentIfExists "src\components\Carousel_carreras.astro" "src\components\sections\home\Carousel_carreras.astro" "Carousel_carreras"

# Shared sections
Move-ComponentIfExists "src\components\CallAction.astro" "src\components\sections\shared\CallAction.astro" "CallAction"
Move-ComponentIfExists "src\components\GeneralCTA.astro" "src\components\sections\shared\GeneralCTA.astro" "GeneralCTA"
Move-ComponentIfExists "src\components\Faq.astro" "src\components\sections\shared\Faq.astro" "Faq"
Move-ComponentIfExists "src\components\SplashScreen.astro" "src\components\sections\shared\SplashScreen.astro" "SplashScreen"

# Blog sections
Move-ComponentIfExists "src\components\Blog.astro" "src\components\sections\blog\Blog.astro" "Blog"

# Accesos component (necesita clasificacion manual)
Move-ComponentIfExists "src\components\Accesos.astro" "src\components\sections\shared\Accesos.astro" "Accesos (movido a shared, revisar ubicacion)"

Write-Host "Migracion de componentes completada!" -ForegroundColor Green

# Paso 3: Crear archivos de ejemplo
Write-Host "Creando archivos de ejemplo..." -ForegroundColor Green

# Layout principal
$layoutContent = @'
---
// Layout principal de la aplicacion
import Header from '../components/layout/Header.astro';
import Footer from '../components/layout/Footer.astro';

export interface Props {
  title: string;
  description?: string;
}

const { title, description } = Astro.props;
---

<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  {description && <meta name="description" content={description}>}
</head>
<body>
  <Header />
  <main>
    <slot />
  </main>
  <Footer />
</body>
</html>
'@

$layoutContent | Out-File -FilePath "src\layouts\Layout.astro" -Encoding UTF8
Write-Host "Creado: Layout.astro" -ForegroundColor Green

# Pagina index ejemplo
$indexContent = @'
---
// Pagina principal con nueva estructura
import Layout from '../layouts/Layout.astro';
import Hero from '../components/sections/home/Hero.astro';
import DescubreUNE from '../components/sections/home/DescubreUNE.astro';
import SobreUNE from '../components/sections/home/SobreUNE.astro';
import CallAction from '../components/sections/shared/CallAction.astro';
---

<Layout title="UNE - Universidad">
  <Hero />
  <DescubreUNE />
  <SobreUNE />
  <CallAction />
</Layout>
'@

$indexContent | Out-File -FilePath "src\pages\index.astro" -Encoding UTF8 -Force
Write-Host "Actualizado: index.astro" -ForegroundColor Green

# Constantes de utilidad
$constantsContent = @'
// Constantes de la aplicacion
export const SITE_CONFIG = {
  title: 'UNE - Universidad',
  description: 'Universidad Nacional de Educacion',
  url: 'https://une.edu.mx',
  image: '/images/og-image.webp'
};

export const NAVIGATION = {
  main: [
    { name: 'Inicio', href: '/' },
    { name: 'Programas', href: '/programs' },
    { name: 'Admisiones', href: '/admissions' },
    { name: 'Blog', href: '/blog' },
    { name: 'Contacto', href: '/contact' }
  ]
};
'@

$constantsContent | Out-File -FilePath "src\utils\constants.js" -Encoding UTF8
Write-Host "Creado: constants.js" -ForegroundColor Green

# Paso 4: Generar reporte de migracion
Write-Host "Generando reporte de migracion..." -ForegroundColor Green

$currentDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$reportContent = @"
# REPORTE DE MIGRACION - $currentDate

## Directorios Creados
* src/components/layout/
* src/components/ui/
* src/components/sections/home/
* src/components/sections/blog/
* src/components/sections/admissions/
* src/components/sections/programs/
* src/components/sections/shared/
* src/components/features/search/
* src/components/features/contact/
* src/components/features/navigation/
* src/layouts/
* src/utils/

## Componentes Migrados
* Header.astro -> layout/
* Footer.astro -> layout/
* Tabs.astro -> ui/
* Hero.astro -> sections/home/
* DescubreUNE.astro -> sections/home/
* SobreUNE.astro -> sections/home/
* DentroUNE.astro -> sections/home/
* Cards_Niveles.astro -> sections/home/
* Carousel_carreras.astro -> sections/home/
* CallAction.astro -> sections/shared/
* GeneralCTA.astro -> sections/shared/
* Faq.astro -> sections/shared/
* SplashScreen.astro -> sections/shared/
* Blog.astro -> sections/blog/
* Accesos.astro -> sections/shared/

## Archivos Creados
* src/layouts/Layout.astro
* src/pages/index.astro (actualizado)
* src/utils/constants.js

## Proximos Pasos
1. Actualizar imports en archivos existentes
2. Verificar que todos los componentes funcionen correctamente
3. Crear componentes adicionales segun necesidades
4. Actualizar referencias en otros archivos del proyecto

## Verificacion Manual Necesaria
* Revisar si Accesos.astro debe estar en shared/ o en otra ubicacion
* Actualizar imports en archivos que no se migraron automaticamente
* Verificar paths de assets e imagenes
"@

$reportContent | Out-File -FilePath "MIGRATION_REPORT.md" -Encoding UTF8
Write-Host "Reporte guardado en: MIGRATION_REPORT.md" -ForegroundColor Green

# Paso 5: Buscar archivos que necesitan actualizacion de imports
Write-Host "Buscando archivos que necesitan actualizacion de imports..." -ForegroundColor Green

$filesToCheck = Get-ChildItem -Path "src" -Recurse -Include "*.astro", "*.js", "*.ts" | Where-Object { $_.FullName -notmatch "node_modules" }

$importsToUpdate = @()
foreach ($file in $filesToCheck) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "import.*from.*['\`"]\.\.?/components/[^/]+\.astro['\`"]") {
        $importsToUpdate += $file.FullName
    }
}

if ($importsToUpdate.Count -gt 0) {
    Write-Host "Archivos que necesitan actualizacion de imports:" -ForegroundColor Yellow
    foreach ($file in $importsToUpdate) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
} else {
    Write-Host "No se encontraron imports que necesiten actualizacion" -ForegroundColor Green
}

Write-Host "Migracion completada exitosamente!" -ForegroundColor Green
Write-Host "Revisa el archivo MIGRATION_REPORT.md para mas detalles" -ForegroundColor Cyan
Write-Host "Tu proyecto ahora tiene una estructura mas organizada y escalable" -ForegroundColor Green

# Mostrar estructura final
Write-Host "Estructura final:" -ForegroundColor Green
$treeOutput = tree src /F 2>$null
if ($LASTEXITCODE -eq 0) {
    $treeOutput
} else {
    Write-Host "Para ver la estructura completa, ejecuta: tree src /F" -ForegroundColor Cyan
}