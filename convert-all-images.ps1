# Convertir imagenes de logros a WebP (recursivo)
$ImagenesPath = ".\src\assets\Imagenes\logros"

Write-Host "Iniciando conversion de imagenes de LOGROS a WebP..." -ForegroundColor Green

# Verificar ruta
if (-not (Test-Path $ImagenesPath)) {
    Write-Host "ERROR: No se encontro la ruta $ImagenesPath" -ForegroundColor Red
    exit
}

# Verificar cwebp
try {
    $version = & cwebp --version 2>&1
    Write-Host "cwebp encontrado: $version" -ForegroundColor Green
} catch {
    Write-Host "ERROR: cwebp no disponible" -ForegroundColor Red
    Write-Host "Instala WebP tools desde: https://developers.google.com/speed/webp/download" -ForegroundColor Yellow
    exit
}

$totalOriginal = 0
$totalWebp = 0
$convertidos = 0
$saltados = 0
$errores = 0

# Buscar todas las imagenes PNG, JPG, JPEG recursivamente
$imagenes = Get-ChildItem -Path $ImagenesPath -Include "*.png","*.jpg","*.jpeg" -Recurse

Write-Host "Imagenes encontradas para conversion: $($imagenes.Count)" -ForegroundColor Cyan
Write-Host "Procesando recursivamente desde: $ImagenesPath" -ForegroundColor Cyan
Write-Host ""

foreach ($imagen in $imagenes) {
    $archivoOriginal = $imagen.FullName
    $nombreSinExtension = [System.IO.Path]::GetFileNameWithoutExtension($archivoOriginal)
    $directorioArchivo = [System.IO.Path]::GetDirectoryName($archivoOriginal)
    $archivoWebp = Join-Path $directorioArchivo "$nombreSinExtension.webp"
    
    # Obtener ruta relativa para mostrar
    $rutaRelativa = $imagen.FullName.Replace((Resolve-Path $ImagenesPath).Path, "").TrimStart('\')
    
    # Saltar si ya existe WebP
    if (Test-Path $archivoWebp) {
        Write-Host "SALTANDO: $rutaRelativa - Ya existe WebP" -ForegroundColor Yellow
        $saltados++
        continue
    }
    
    # Calidad alta para logros (85% para balance entre calidad y tamaño)
    $calidad = 85
    
    Write-Host "PROCESANDO: $rutaRelativa" -ForegroundColor Green
    Write-Host "  Aplicando calidad: $calidad (optimizada para logros)" -ForegroundColor Yellow
    
    # Mostrar tamaño original
    $tamanoOriginalMB = [math]::Round($imagen.Length / 1MB, 2)
    Write-Host "  Tamaño original: $tamanoOriginalMB MB" -ForegroundColor Cyan
    
    # Convertir a WebP
    try {
        $resultado = & cwebp -q $calidad "$archivoOriginal" -o "$archivoWebp" 2>&1
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $archivoWebp)) {
            $tamanoOriginal = $imagen.Length
            $tamanoWebp = (Get-Item $archivoWebp).Length
            $ahorro = [math]::Round((($tamanoOriginal - $tamanoWebp) / $tamanoOriginal) * 100, 1)
            $tamanoWebpMB = [math]::Round($tamanoWebp / 1MB, 2)
            
            $totalOriginal += $tamanoOriginal
            $totalWebp += $tamanoWebp
            $convertidos++
            
            Write-Host "  EXITO: $tamanoWebpMB MB - Ahorro del $ahorro%" -ForegroundColor Green
        } else {
            Write-Host "  ERROR en conversion: $resultado" -ForegroundColor Red
            $errores++
        }
    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $errores++
    }
    
    Write-Host "" # Linea en blanco para separar
}

# Resumen final detallado
Write-Host ""
Write-Host "===============================================" -ForegroundColor Gray
Write-Host "RESUMEN CONVERSION - CARPETA LOGROS" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Gray
Write-Host "Ruta procesada: $ImagenesPath" -ForegroundColor White
Write-Host "Total de imagenes encontradas: $($imagenes.Count)" -ForegroundColor Cyan
Write-Host "Archivos convertidos exitosamente: $convertidos" -ForegroundColor Green
Write-Host "Archivos saltados (ya existian WebP): $saltados" -ForegroundColor Yellow
Write-Host "Errores en conversion: $errores" -ForegroundColor Red

if ($convertidos -gt 0) {
    $originalMB = [math]::Round($totalOriginal / 1MB, 2)
    $webpMB = [math]::Round($totalWebp / 1MB, 2)
    $ahorroTotal = [math]::Round((($totalOriginal - $totalWebp) / $totalOriginal) * 100, 1)
    $ahorroMB = [math]::Round(($totalOriginal - $totalWebp) / 1MB, 2)
    
    Write-Host ""
    Write-Host "ESTADISTICAS DE COMPRESION:" -ForegroundColor Magenta
    Write-Host "Peso total original: $originalMB MB" -ForegroundColor Cyan
    Write-Host "Peso total WebP: $webpMB MB" -ForegroundColor Cyan
    Write-Host "AHORRO TOTAL: $ahorroTotal% ($ahorroMB MB menos)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "CONFIGURACION APLICADA:" -ForegroundColor Magenta
    Write-Host "Calidad: 85% (balance optimo para logros)" -ForegroundColor Green
    Write-Host "Procesamiento recursivo en subcarpetas" -ForegroundColor Green
    Write-Host "Archivos originales conservados intactos" -ForegroundColor Green
    Write-Host "Formato WebP para mejor rendimiento web" -ForegroundColor Green
}

Write-Host ""
if ($errores -eq 0) {
    Write-Host "===============================================" -ForegroundColor Gray
    Write-Host "CONVERSION COMPLETADA EXITOSAMENTE!" -ForegroundColor Blue
    Write-Host "===============================================" -ForegroundColor Gray
} else {
    Write-Host "===============================================" -ForegroundColor Gray
    Write-Host "CONVERSION COMPLETADA CON $errores ERRORES" -ForegroundColor Yellow
    Write-Host "===============================================" -ForegroundColor Gray
}

Write-Host ""
Write-Host "SIGUIENTE PASO:" -ForegroundColor Cyan
Write-Host "Actualiza las referencias en tu codigo Astro para usar los archivos .webp" -ForegroundColor White