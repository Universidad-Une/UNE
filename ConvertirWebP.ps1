# Script para mover todos los archivos que NO sean WebP a backup
# Mantiene la estructura de carpetas

param(
    [string]$RutaOrigen = ".\src\assets\Imagenes\",
    [string]$RutaBackup = ".\backup\",
    [switch]$MostrarProgreso = $true
)

# Colores para la consola
$ColorExito = "Green"
$ColorAdvertencia = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

# Funcion para mostrar salida con colores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput $ColorInfo "Iniciando movimiento de archivos no-WebP a backup..."
Write-ColorOutput $ColorInfo "Origen: $RutaOrigen"
Write-ColorOutput $ColorInfo "Destino: $RutaBackup"
Write-ColorOutput $ColorInfo "=================================================="

# Verificar que la ruta origen existe
if (-not (Test-Path $RutaOrigen)) {
    Write-ColorOutput $ColorError "Error: La ruta origen '$RutaOrigen' no existe"
    exit 1
}

# Crear la carpeta backup si no existe
if (-not (Test-Path $RutaBackup)) {
    New-Item -ItemType Directory -Path $RutaBackup -Force | Out-Null
    Write-ColorOutput $ColorInfo "Carpeta backup creada: $RutaBackup"
}

# Contadores
$TotalArchivos = 0
$TotalMovidos = 0
$TotalErrores = 0

# Obtener todos los archivos que NO sean WebP recursivamente
Write-ColorOutput $ColorInfo "Buscando archivos no-WebP..."

$ArchivosNoWebP = Get-ChildItem -Path $RutaOrigen -Recurse -File | Where-Object {
    $_.Extension.ToLower() -ne ".webp"
}

$TotalArchivos = $ArchivosNoWebP.Count
Write-ColorOutput $ColorInfo "Se encontraron $TotalArchivos archivos no-WebP para mover"

if ($TotalArchivos -eq 0) {
    Write-ColorOutput $ColorAdvertencia "No se encontraron archivos no-WebP para mover"
    exit 0
}

Write-ColorOutput $ColorInfo "=================================================="

# Procesar cada archivo
foreach ($Archivo in $ArchivosNoWebP) {
    try {
        # Calcular la ruta relativa desde la carpeta origen
        $RutaRelativa = $Archivo.FullName.Substring($RutaOrigen.Length)
        if ($RutaRelativa.StartsWith("\")) {
            $RutaRelativa = $RutaRelativa.Substring(1)
        }
        
        # Crear la ruta completa de destino
        $RutaDestino = Join-Path $RutaBackup "src\assets\Imagenes\$RutaRelativa"
        
        # Crear el directorio de destino si no existe
        $DirectorioDestino = Split-Path $RutaDestino -Parent
        if (-not (Test-Path $DirectorioDestino)) {
            New-Item -ItemType Directory -Path $DirectorioDestino -Force | Out-Null
        }
        
        # Mostrar progreso
        if ($MostrarProgreso) {
            $Porcentaje = [math]::Round((($TotalMovidos + $TotalErrores + 1) / $TotalArchivos) * 100, 1)
            Write-Progress -Activity "Moviendo archivos" -Status "Procesando: $($Archivo.Name)" -PercentComplete $Porcentaje
        }
        
        # Mover el archivo
        Move-Item -Path $Archivo.FullName -Destination $RutaDestino -Force
        
        Write-ColorOutput $ColorExito "Movido: $RutaRelativa"
        $TotalMovidos++
    }
    catch {
        Write-ColorOutput $ColorError "Error al mover: $($Archivo.Name) - $($_.Exception.Message)"
        $TotalErrores++
    }
}

# Ocultar la barra de progreso
if ($MostrarProgreso) {
    Write-Progress -Activity "Moviendo archivos" -Completed
}

# Mostrar resumen final
Write-ColorOutput $ColorInfo "=================================================="
Write-ColorOutput $ColorInfo "RESUMEN FINAL:"
Write-ColorOutput $ColorInfo "   Total de archivos encontrados: $TotalArchivos"
Write-ColorOutput $ColorExito "   Movidos exitosamente: $TotalMovidos"
Write-ColorOutput $ColorError "   Errores: $TotalErrores"
Write-ColorOutput $ColorInfo "=================================================="

if ($TotalMovidos -gt 0) {
    Write-ColorOutput $ColorExito "Movimiento completado!"
    Write-ColorOutput $ColorInfo "Los archivos se han movido a: $RutaBackup"
}
else {
    Write-ColorOutput $ColorError "No se pudieron mover los archivos"
}

# Mostrar estructura final
Write-ColorOutput $ColorInfo ""
Write-ColorOutput $ColorInfo "Estructura de backup creada:"
if (Test-Path $RutaBackup) {
    Get-ChildItem -Path $RutaBackup -Recurse -Directory | Select-Object -First 10 | ForEach-Object {
        Write-ColorOutput $ColorInfo "   $($_.FullName.Replace($RutaBackup, ''))"
    }
}