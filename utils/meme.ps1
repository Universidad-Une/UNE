# Script para eliminar imágenes aleatoriamente hasta que queden exactamente 100
# Autor: Claude
# Fecha: $(Get-Date -Format "dd/MM/yyyy")

param(
    [Parameter(Mandatory=$false)]
    [string]$RutaCarpeta = "..\src\assets\Imagenes\Graduaciones\",
    
    [Parameter(Mandatory=$false)]
    [int]$CantidadFinal = 100
)

# Función para mostrar banner
function Show-Banner {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "        ELIMINADOR RANDOM DE IMAGENES" -ForegroundColor Cyan
    Write-Host "              Objetivo: $CantidadFinal imagenes" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Función para obtener imágenes
function Get-ImageFiles {
    param([string]$Path)
    
    $extensiones = @("*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", "*.webp")
    $imagenes = @()
    
    foreach ($ext in $extensiones) {
        $imagenes += Get-ChildItem -Path $Path -Filter $ext -File
    }
    
    return $imagenes
}

# Función para mostrar estadísticas
function Show-Stats {
    param(
        [int]$Total,
        [int]$Objetivo,
        [int]$AEliminar
    )
    
    Write-Host "ESTADISTICAS:" -ForegroundColor Yellow
    Write-Host "   Imagenes encontradas: $Total" -ForegroundColor White
    Write-Host "   Objetivo final: $Objetivo" -ForegroundColor Green
    Write-Host "   A eliminar: $AEliminar" -ForegroundColor Red
    Write-Host ""
}

# Función principal
function Remove-RandomImages {
    try {
        Show-Banner
        
        # Verificar si la carpeta existe
        if (-not (Test-Path $RutaCarpeta)) {
            Write-Host "Error: La carpeta '$RutaCarpeta' no existe." -ForegroundColor Red
            return
        }
        
        # Obtener todas las imágenes
        Write-Host "Buscando imagenes en: $RutaCarpeta" -ForegroundColor Blue
        $imagenes = Get-ImageFiles -Path $RutaCarpeta
        
        if ($imagenes.Count -eq 0) {
            Write-Host "No se encontraron imagenes en la carpeta." -ForegroundColor Red
            return
        }
        
        $totalImagenes = $imagenes.Count
        
        # Verificar si ya tenemos la cantidad correcta o menos
        if ($totalImagenes -le $CantidadFinal) {
            Write-Host "Ya tienes $totalImagenes imagenes, que es igual o menor al objetivo de $CantidadFinal." -ForegroundColor Green
            Write-Host "No es necesario eliminar nada." -ForegroundColor Green
            return
        }
        
        $imagenesAEliminar = $totalImagenes - $CantidadFinal
        Show-Stats -Total $totalImagenes -Objetivo $CantidadFinal -AEliminar $imagenesAEliminar
        
        # Confirmar acción
        Write-Host "ADVERTENCIA: Esta accion eliminara $imagenesAEliminar imagenes PERMANENTEMENTE." -ForegroundColor Yellow -BackgroundColor Red
        $confirmacion = Read-Host "Estas seguro? Escribe 'SI' para continuar, cualquier otra cosa para cancelar"
        
        if ($confirmacion -ne "SI") {
            Write-Host "Operacion cancelada por el usuario." -ForegroundColor Yellow
            return
        }
        
        # Mezclar la lista de imágenes aleatoriamente
        Write-Host "Mezclando imagenes aleatoriamente..." -ForegroundColor Blue
        $imagenesMezcladas = $imagenes | Sort-Object {Get-Random}
        
        # Seleccionar las imágenes a eliminar
        $imagenesABorrar = $imagenesMezcladas | Select-Object -First $imagenesAEliminar
        
        # Mostrar el destino de TODAS las imagenes
        Write-Host ""
        Write-Host "=== ANUNCIANDO EL DESTINO DE CADA IMAGEN ===" -ForegroundColor Magenta
        Write-Host ""
        
        $imagenesQueViven = $imagenes | Where-Object { $imagenesABorrar -notcontains $_ }
        $todasParaMostrar = ($imagenesQueViven + $imagenesABorrar) | Sort-Object {Get-Random}
        
        foreach ($img in $todasParaMostrar) {
            $viveOMuere = if ($imagenesABorrar -contains $img) { "MUERE" } else { "VIVE" }
            $color = if ($imagenesABorrar -contains $img) { "Red" } else { "Green" }
            
            Write-Host "$viveOMuere - $($img.Name)" -ForegroundColor $color
            Start-Sleep -Milliseconds 200
        }
        
        Write-Host ""
        Write-Host "Ahora procediendo con las ejecuciones..." -ForegroundColor Red
        Write-Host ""
        
        $contador = 0
        $errores = 0
        
        foreach ($imagen in $imagenesABorrar) {
            $contador++
            $porcentaje = [math]::Round(($contador / $imagenesAEliminar) * 100, 1)
            
            try {
                Remove-Item $imagen.FullName -Force
                Write-Host "   OK [$contador/$imagenesAEliminar] ($porcentaje%) $($imagen.Name)" -ForegroundColor Green
            }
            catch {
                $errores++
                Write-Host "   ERROR [$contador/$imagenesAEliminar] Error eliminando: $($imagen.Name) - $($_.Exception.Message)" -ForegroundColor Red
            }
            
            # Pequeña pausa para efecto visual
            Start-Sleep -Milliseconds 50
        }
        
        # Resultados finales
        Write-Host ""
        Write-Host "RESULTADOS FINALES:" -ForegroundColor Cyan
        
        $imagenesRestantes = (Get-ImageFiles -Path $RutaCarpeta).Count
        Write-Host "   Imagenes eliminadas: $($contador - $errores)" -ForegroundColor Green
        Write-Host "   Imagenes restantes: $imagenesRestantes" -ForegroundColor Blue
        
        if ($imagenesRestantes -eq $CantidadFinal) {
            Write-Host "   OBJETIVO ALCANZADO! Tienes exactamente $CantidadFinal imagenes." -ForegroundColor Green -BackgroundColor DarkGreen
        } else {
            Write-Host "   Objetivo no alcanzado exactamente (errores: $errores)" -ForegroundColor Yellow
        }
        
        if ($errores -gt 0) {
            Write-Host "   Errores encontrados: $errores" -ForegroundColor Red
        }
        
    }
    catch {
        Write-Host "Error inesperado: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Mensaje de ayuda
function Show-Help {
    Write-Host "USO DEL SCRIPT:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ejemplos de uso:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "# Eliminar hasta dejar 100 imagenes:" -ForegroundColor White
    Write-Host ".\eliminar-imagenes-random.ps1" -ForegroundColor Green
    Write-Host ""
    Write-Host "# Especificar carpeta diferente:" -ForegroundColor White
    Write-Host ".\eliminar-imagenes-random.ps1 -RutaCarpeta 'C:\MisImagenes\'" -ForegroundColor Green
    Write-Host ""
    Write-Host "# Dejar diferente cantidad de imagenes:" -ForegroundColor White
    Write-Host ".\eliminar-imagenes-random.ps1 -CantidadFinal 50" -ForegroundColor Green
    Write-Host ""
    Write-Host "Parametros:" -ForegroundColor Yellow
    Write-Host "  -RutaCarpeta      : Carpeta con las imagenes (default: '..\src\assets\Imagenes\Graduaciones\')" -ForegroundColor White
    Write-Host "  -CantidadFinal    : Cantidad de imagenes a conservar (default: 100)" -ForegroundColor White
    Write-Host "  -Help             : Mostrar esta ayuda" -ForegroundColor White
}

# Verificar si se pidió ayuda
if ($args -contains "-Help" -or $args -contains "--help" -or $args -contains "/?") {
    Show-Help
    return
}

# Ejecutar función principal
Remove-RandomImages