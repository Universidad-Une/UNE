# Script para generar archivos de actividades basados en la plantilla de Futbol.astro

# Ruta base donde están los archivos
$basePath = "C:\Users\UNE\Documents\VSCode\UNE\src\pages\Vivetuuniversidad\Actividades"
$templateFile = Join-Path $basePath "Futbol.astro"

# Lista de actividades
$actividades = @(
    "Actuacion",
    "Baldor",
    "Bisuteria",
    "Box",
    "Basquetbol",
    "Canto",
    "DEJANDO_HUELLAS",
    "Danza",
    "Defensa_personal_Karate",
    "Deportivo",
    "Dibujo",
    "Dibujo_y_Pintura",
    "Expresion_Oral_y_Escrita",
    "Futbol",
    "GENERANDO_IMPACTO_POSITIVO",
    "Gastronomia",
    "Jazz",
    "Karate",
    "Kpop_Urbano",
    "LENGUAJE_DE_SENAS",
    "Manualidades",
    "Natacion",
    "PRIMEROS_AUXILIOS",
    "PRINCIPIOS_BASICOS_EN_ATENCION_A_PACIENTES",
    "Programacion",
    "ROMPIENDO_PARADIGMAS",
    "Ritmos_Latinos",
    "Taller_Administrativos",
    "Teatro",
    "Tochito",
    "Voleibol"
)

# Verificar que el archivo plantilla existe
if (-not (Test-Path $templateFile)) {
    Write-Error "El archivo plantilla $templateFile no existe"
    exit 1
}

# Leer el contenido de la plantilla
$templateContent = Get-Content $templateFile -Raw

Write-Host "Iniciando generacion de archivos de actividades..." -ForegroundColor Green
Write-Host "Plantilla base: $templateFile" -ForegroundColor Yellow

# Generar un archivo para cada actividad
foreach ($actividad in $actividades) {
    $fileName = "$actividad.astro"
    $filePath = Join-Path $basePath $fileName
    
    # Si el archivo ya existe, preguntar si se quiere sobrescribir
    if (Test-Path $filePath) {
        $overwrite = Read-Host "El archivo $fileName ya existe. Deseas sobrescribirlo? (s/n)"
        if ($overwrite -ne "s" -and $overwrite -ne "S") {
            Write-Host "Saltando $fileName" -ForegroundColor Yellow
            continue
        }
    }
    
    # Crear el contenido personalizado reemplazando "Futbol" por la actividad actual
    $personalizedContent = $templateContent -replace "Futbol", $actividad -replace "futbol", $actividad.ToLower()
    
    # Escribir el archivo
    try {
        $personalizedContent | Set-Content $filePath -Encoding UTF8
        Write-Host "Creado: $fileName" -ForegroundColor Green
    } catch {
        Write-Error "Error al crear $fileName : $_"
    }
}

Write-Host "Proceso completado!" -ForegroundColor Green
Write-Host "Se han generado los archivos en: $basePath" -ForegroundColor Cyan

# Mostrar resumen de archivos creados
Write-Host "Archivos generados:" -ForegroundColor Yellow
Get-ChildItem $basePath -Filter "*.astro" | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize