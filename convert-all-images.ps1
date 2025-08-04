# Convertir todas las imagenes a WebP
$ImagenesPath = ".\src\assets\Imagenes"
$HerosFolder = "Heros"

Write-Host "Iniciando conversion de imagenes a WebP..." -ForegroundColor Green

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
    exit
}

$totalOriginal = 0
$totalWebp = 0
$convertidos = 0
$saltados = 0

# Buscar todas las imagenes
$imagenes = Get-ChildItem -Path $ImagenesPath -Include "*.webp","*.webp","*.webp" -Recurse

Write-Host "Imagenes encontradas: $($imagenes.Count)" -ForegroundColor Cyan

foreach ($imagen in $imagenes) {
    $archivoOriginal = $imagen.FullName
    $archivoWebp = $archivoOriginal -replace '\.(png|jpg|jpeg)$', '.webp'
    $rutaRelativa = $imagen.FullName.Replace((Resolve-Path $ImagenesPath).Path, "").TrimStart('\')
    
    # Saltar si ya existe
    if (Test-Path $archivoWebp) {
        Write-Host "SALTANDO: $rutaRelativa - Ya existe WebP" -ForegroundColor Yellow
        $saltados++
        continue
    }
    
    # Determinar calidad
    $esHeros = $rutaRelativa -match "^$HerosFolder\\"
    $calidad = if ($esHeros) { 95 } else { 75 }
    $modo = if ($esHeros) { "Alta calidad (Heros)" } else { "Compresion media" }
    
    Write-Host "PROCESANDO: $rutaRelativa" -ForegroundColor Green
    Write-Host "  Modo: $modo (calidad $calidad)" -ForegroundColor Yellow
    
    # Convertir
    $resultado = & cwebp -q $calidad $archivoOriginal -o $archivoWebp 2>&1
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $archivoWebp)) {
        $tamanoOriginal = $imagen.Length
        $tamanoWebp = (Get-Item $archivoWebp).Length
        $ahorro = [math]::Round((($tamanoOriginal - $tamanoWebp) / $tamanoOriginal) * 100, 1)
        
        $totalOriginal += $tamanoOriginal
        $totalWebp += $tamanoWebp
        $convertidos++
        
        Write-Host "  EXITO: Ahorro del $ahorro%" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: $resultado" -ForegroundColor Red
    }
}

# Resumen final detallado
Write-Host ""
Write-Host "===============================================" -ForegroundColor Gray
Write-Host "RESUMEN FINAL DE CONVERSION" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Gray
Write-Host "Total de imagenes encontradas: $($imagenes.Count)" -ForegroundColor Cyan
Write-Host "Archivos convertidos exitosamente: $convertidos" -ForegroundColor White
Write-Host "Archivos saltados (ya existian WebP): $saltados" -ForegroundColor Yellow

if ($convertidos -gt 0) {
    $originalKB = [math]::Round($totalOriginal / 1KB, 1)
    $originalMB = [math]::Round($totalOriginal / 1MB, 2)
    $webpKB = [math]::Round($totalWebp / 1KB, 1)
    $webpMB = [math]::Round($totalWebp / 1MB, 2)
    $ahorroTotal = [math]::Round((($totalOriginal - $totalWebp) / $totalOriginal) * 100, 1)
    $ahorroKB = [math]::Round(($totalOriginal - $totalWebp) / 1KB, 1)
    $ahorroMB = [math]::Round(($totalOriginal - $totalWebp) / 1MB, 2)
    
    Write-Host ""
    Write-Host "ESTADISTICAS DE COMPRESION:" -ForegroundColor Magenta
    Write-Host "Peso total original: $originalKB KB - $originalMB MB" -ForegroundColor Cyan
    Write-Host "Peso total WebP: $webpKB KB - $webpMB MB" -ForegroundColor Cyan
    Write-Host "AHORRO TOTAL: $ahorroTotal% - $ahorroKB KB - $ahorroMB MB" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "CONFIGURACION APLICADA:" -ForegroundColor Magenta
    Write-Host "✓ Carpeta Heros: Calidad 95 (alta calidad)" -ForegroundColor Green
    Write-Host "✓ Otras carpetas: Calidad 75 (compresion optimizada)" -ForegroundColor Green
    Write-Host "✓ Archivos originales conservados intactos" -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Gray
Write-Host "CONVERSION COMPLETADA EXITOSAMENTE!" -ForegroundColor Blue
Write-Host "===============================================" -ForegroundColor Gray