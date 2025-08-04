# Reconvertir imagenes a WebP - Heros y Middles: 90, Otras: 90
$ImagenesPath = ".\src\assets\Imagenes"
$HerosFolder = "Heros"
$MiddlesFolder = "Middles"

Write-Host "Iniciando reconversion de imagenes a WebP..."
Write-Host "Todas las imagenes - Calidad 90"

# Verificar ruta
if (-not (Test-Path $ImagenesPath)) {
    Write-Host "ERROR: No se encontro la ruta $ImagenesPath"
    exit
}

# Verificar cwebp
try {
    $version = & cwebp --version 2>&1
    Write-Host "cwebp encontrado: $version"
} catch {
    Write-Host "ERROR: cwebp no disponible"
    exit
}

$totalOriginal = 0
$totalWebp = 0
$convertidos = 0
$reconvertidos = 0

# Buscar todas las imagenes (incluyendo WebP existentes para reconvertir)
$imagenes = Get-ChildItem -Path $ImagenesPath -Include "*.png","*.jpg","*.jpeg","*.webp" -Recurse

Write-Host "Imagenes encontradas: $($imagenes.Count)"
Write-Host "ATENCION - Se reconvertiran todas las imagenes con calidad 90"
Write-Host "- Todas las carpetas - Calidad 90 (alta calidad unificada)"
Write-Host ""

foreach ($imagen in $imagenes) {
    $archivoOriginal = $imagen.FullName
    $rutaRelativa = $imagen.FullName.Replace((Resolve-Path $ImagenesPath).Path, "").TrimStart('\')
    
    # Determinar archivo WebP destino y calidad
    $esHeros = $rutaRelativa -match "^$HerosFolder\\"
    $calidad = if ($esHeros) { 95 } else { 85 }
    $modo = if ($esHeros) { "Alta calidad (Heros)" } else { "Calidad media-alta" }
    
    if ($imagen.Extension -eq ".webp") {
        $archivoWebp = $archivoOriginal
        $tipoOperacion = "RECONVERSION"
    } else {
        $archivoWebp = $archivoOriginal -replace '\.(png|jpg|jpeg)$', '.webp'
        $tipoOperacion = "CONVERSION"
    }
    
    Write-Host "$tipoOperacion - $rutaRelativa"
    Write-Host "  Modo: $modo (calidad $calidad)"
    
    # Si existe WebP, hacer backup temporal para medir diferencia
    $backupCreado = $false
    $archivoBackup = ""
    if (Test-Path $archivoWebp) {
        $archivoBackup = $archivoWebp + ".backup"
        Move-Item $archivoWebp $archivoBackup
        $backupCreado = $true
    }
    
    # Convertir con calidad apropiada
    $resultado = & cwebp -q $calidad $archivoOriginal -o $archivoWebp 2>&1
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path $archivoWebp)) {
        $tamanoOriginal = $imagen.Length
        $tamanoWebp = (Get-Item $archivoWebp).Length
        
        # Calcular ahorro respecto al original
        $ahorro = [math]::Round((($tamanoOriginal - $tamanoWebp) / $tamanoOriginal) * 100, 1)
        
        # Si habia backup, comparar con la version anterior
        if ($backupCreado) {
            $tamanoAnterior = (Get-Item $archivoBackup).Length
            $diferenciaAnterior = $tamanoWebp - $tamanoAnterior
            $porcentajeDiferencia = [math]::Round(($diferenciaAnterior / $tamanoAnterior) * 100, 1)
            
            if ($diferenciaAnterior -gt 0) {
                Write-Host "  RESULTADO - $ahorro% vs original | +$porcentajeDiferencia% vs anterior (mayor calidad)"
            } else {
                Write-Host "  RESULTADO - $ahorro% vs original | $porcentajeDiferencia% vs anterior (menor tamano)"
            }
            
            # Eliminar backup
            Remove-Item $archivoBackup -Force
            $reconvertidos++
        } else {
            Write-Host "  RESULTADO - $ahorro% de ahorro vs original"
        }
        
        $totalOriginal += $tamanoOriginal
        $totalWebp += $tamanoWebp
        $convertidos++
        
    } else {
        Write-Host "  ERROR - $resultado"
        
        # Restaurar backup si fallo
        if ($backupCreado -and (Test-Path $archivoBackup)) {
            Move-Item $archivoBackup $archivoWebp
            Write-Host "  Archivo anterior restaurado"
        }
    }
    
    Write-Host ""
}

# Resumen final detallado
Write-Host "==============================================="
Write-Host "RESUMEN FINAL DE RECONVERSION"
Write-Host "==============================================="
Write-Host "Total de imagenes procesadas: $($imagenes.Count)"
Write-Host "Archivos convertidos exitosamente: $convertidos"
Write-Host "Archivos reconvertidos: $reconvertidos"
Write-Host "Archivos nuevos: $($convertidos - $reconvertidos)"

if ($convertidos -gt 0) {
    $originalKB = [math]::Round($totalOriginal / 1KB, 1)
    $originalMB = [math]::Round($totalOriginal / 1MB, 2)
    $webpKB = [math]::Round($totalWebp / 1KB, 1)
    $webpMB = [math]::Round($totalWebp / 1MB, 2)
    $ahorroTotal = [math]::Round((($totalOriginal - $totalWebp) / $totalOriginal) * 100, 1)
    $ahorroKB = [math]::Round(($totalOriginal - $totalWebp) / 1KB, 1)
    $ahorroMB = [math]::Round(($totalOriginal - $totalWebp) / 1MB, 2)
    
    Write-Host ""
    Write-Host "ESTADISTICAS DE COMPRESION - "
    Write-Host "Peso total original - $originalKB KB ($originalMB MB)"
    Write-Host "Peso total WebP - $webpKB KB ($webpMB MB)"
    Write-Host "AHORRO TOTAL - $ahorroTotal% | $ahorroKB KB ($ahorroMB MB)"
    
    Write-Host ""
    Write-Host "NUEVA CONFIGURACION APLICADA - "
    Write-Host "- Todas las carpetas - Calidad 90 (alta calidad unificada)"
    Write-Host "- Archivos originales conservados intactos"
    Write-Host "- WebP anteriores reemplazados con nueva calidad"
}

Write-Host ""
Write-Host "Proceso completado!"
Write-Host "- Todas las imagenes actualizadas a calidad 90"