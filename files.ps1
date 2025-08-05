# Script para renombrar archivos con caracteres especiales
$LogrosPath = ".\src\assets\Imagenes\logros"

Write-Host "Renombrando archivos con caracteres especiales..." -ForegroundColor Green

# Obtener todos los archivos que contengan el símbolo º
$archivosProblematicos = Get-ChildItem -Path $LogrosPath -Recurse -File | Where-Object { $_.Name -match "[º°]" }

Write-Host "Archivos encontrados con símbolos problemáticos: $($archivosProblematicos.Count)" -ForegroundColor Cyan

foreach ($archivo in $archivosProblematicos) {
    $nombreOriginal = $archivo.Name
    $rutaOriginal = $archivo.FullName
    
    # Reemplazar el símbolo º por "o" simple
    $nombreNuevo = $nombreOriginal -replace "[º°]", "o"
    $rutaNueva = Join-Path $archivo.DirectoryName $nombreNuevo
    
    # Mostrar el cambio
    Write-Host "RENOMBRANDO:" -ForegroundColor Yellow
    Write-Host "  De: $nombreOriginal" -ForegroundColor Red
    Write-Host "  A:  $nombreNuevo" -ForegroundColor Green
    
    try {
        # Renombrar el archivo
        Rename-Item -Path $rutaOriginal -NewName $nombreNuevo -Force
        Write-Host "  EXITO: Archivo renombrado" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "" # Línea en blanco
}

# Verificar cambios
Write-Host "===============================================" -ForegroundColor Gray
Write-Host "VERIFICACION DE CAMBIOS" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Gray

$archivosRestantes = Get-ChildItem -Path $LogrosPath -Recurse -File | Where-Object { $_.Name -match "[º°]" }
Write-Host "Archivos que aún tienen símbolos problemáticos: $($archivosRestantes.Count)" -ForegroundColor Yellow

if ($archivosRestantes.Count -eq 0) {
    Write-Host "PERFECTO: Todos los archivos han sido renombrados correctamente" -ForegroundColor Green
} else {
    Write-Host "ARCHIVOS PENDIENTES:" -ForegroundColor Red
    $archivosRestantes | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor Red }
}

Write-Host ""
Write-Host "SIGUIENTE PASO:" -ForegroundColor Cyan
Write-Host "1. Actualiza las referencias en tu código Astro" -ForegroundColor White
Write-Host "2. Haz commit de los archivos renombrados" -ForegroundColor White
Write-Host "3. Verifica que el build funcione correctamente" -ForegroundColor White