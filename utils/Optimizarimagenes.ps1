# Script para optimizar imagenes usando cwebp
# Mantiene los archivos originales y crea versiones optimizadas

param(
    [string]$RutaCarpeta = "",
    [int]$NivelCompresion = -1
)

function Mostrar-Banner {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "    OPTIMIZADOR DE IMAGENES CON CWEBP      " -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
}

function Verificar-Cwebp {
    try {
        $version = & cwebp -version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "cwebp encontrado y funcionando" -ForegroundColor Green
            Write-Host "Version: $($version[0])" -ForegroundColor Gray
            return $true
        }
    }
    catch {
        Write-Host "Error: cwebp no esta instalado o no esta en el PATH" -ForegroundColor Red
        Write-Host "Asegurate de tener cwebp instalado y accesible desde la linea de comandos" -ForegroundColor Yellow
        return $false
    }
    return $false
}

function Mostrar-GuiaCompresion {
    Write-Host ""
    Write-Host "GUIA DE NIVELES DE COMPRESION RECOMENDADOS:" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NIVEL 0:" -ForegroundColor White
    Write-Host "  - Sin perdida (lossless)" -ForegroundColor Gray
    Write-Host "  - Calidad perfecta, archivos mas grandes" -ForegroundColor Gray
    Write-Host "  - Recomendado para: imagenes tecnicas, logos, graficos" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NIVEL 25:" -ForegroundColor White
    Write-Host "  - Alta calidad, compresion ligera" -ForegroundColor Gray
    Write-Host "  - Perdida minima de calidad" -ForegroundColor Gray
    Write-Host "  - Recomendado para: fotografias profesionales, portfolios" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NIVEL 50:" -ForegroundColor White
    Write-Host "  - Calidad media, buen balance" -ForegroundColor Gray
    Write-Host "  - Balance entre calidad y tamaño" -ForegroundColor Gray
    Write-Host "  - Recomendado para: uso general, sitios web" -ForegroundColor Gray
    Write-Host ""
    Write-Host "NIVEL 75:" -ForegroundColor White
    Write-Host "  - Calidad aceptable, alta compresion" -ForegroundColor Gray
    Write-Host "  - Buena reduccion de tamaño, calidad visible" -ForegroundColor Gray
    Write-Host "  - Recomendado para: redes sociales, blogs (MAS USADO)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "NIVEL 90:" -ForegroundColor White
    Write-Host "  - Baja calidad, maxima compresion" -ForegroundColor Gray
    Write-Host "  - Archivos muy pequeños, perdida notable de calidad" -ForegroundColor Gray
    Write-Host "  - Recomendado para: miniaturas, vistas previas" -ForegroundColor Gray
    Write-Host ""
}

function Obtener-RutaCarpeta {
    param([string]$RutaInicial)
    
    if ($RutaInicial -and (Test-Path $RutaInicial)) {
        return $RutaInicial
    }
    
    do {
        Write-Host ""
        Write-Host "Ingrese la ruta de la carpeta que contiene las imagenes a comprimir:" -ForegroundColor Yellow
        Write-Host "(Ejemplo: C:\Imagenes o .\fotos)" -ForegroundColor Gray
        $ruta = Read-Host "Ruta"
        
        if ([string]::IsNullOrWhiteSpace($ruta)) {
            Write-Host "La ruta no puede estar vacia" -ForegroundColor Red
            continue
        }
        
        $rutaCompleta = Resolve-Path -Path $ruta -ErrorAction SilentlyContinue
        if ($rutaCompleta -and (Test-Path $rutaCompleta)) {
            return $rutaCompleta.Path
        } else {
            Write-Host "La ruta '$ruta' no existe. Intente nuevamente." -ForegroundColor Red
        }
    } while ($true)
}

function Obtener-NivelCompresion {
    param([int]$NivelInicial)
    
    if ($NivelInicial -ge 0 -and $NivelInicial -le 100) {
        return $NivelInicial
    }
    
    # Mostrar guia de compresion
    Mostrar-GuiaCompresion
    
    do {
        Write-Host "Seleccione el nivel de compresion (0-100):" -ForegroundColor Yellow
        Write-Host "Para ver la guia nuevamente escriba 'ayuda'" -ForegroundColor Gray
        
        $input = Read-Host "Nivel de compresion (recomendado: 75)"
        
        if ($input -eq "ayuda" -or $input -eq "help") {
            Mostrar-GuiaCompresion
            continue
        }
        
        if ([string]::IsNullOrWhiteSpace($input)) {
            return 75  # Valor por defecto
        }
        
        $nivel = 0
        if ([int]::TryParse($input, [ref]$nivel) -and $nivel -ge 0 -and $nivel -le 100) {
            return $nivel
        } else {
            Write-Host "Por favor, ingrese un numero entre 0 y 100" -ForegroundColor Red
        }
    } while ($true)
}

function Crear-CarpetaOptimizada {
    param([string]$RutaBase)
    
    $carpetaOptimizada = Join-Path $RutaBase "optimizadas"
    
    if (!(Test-Path $carpetaOptimizada)) {
        New-Item -ItemType Directory -Path $carpetaOptimizada -Force | Out-Null
        Write-Host "Carpeta 'optimizadas' creada en: $carpetaOptimizada" -ForegroundColor Green
    } else {
        Write-Host "Usando carpeta existente: $carpetaOptimizada" -ForegroundColor Green
    }
    
    return $carpetaOptimizada
}

function Comprimir-Imagen {
    param(
        [string]$ArchivoOrigen,
        [string]$ArchivoDestino,
        [int]$Calidad
    )
    
    try {
        if ($Calidad -eq 0) {
            # Compresion sin perdida (lossless)
            & cwebp -lossless -z 9 "$ArchivoOrigen" -o "$ArchivoDestino" 2>$null
        } else {
            # Compresion con perdida
            & cwebp -q $Calidad "$ArchivoOrigen" -o "$ArchivoDestino" 2>$null
        }
        
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Obtener-TamanoArchivo {
    param([string]$Ruta)
    
    if (Test-Path $Ruta) {
        return (Get-Item $Ruta).Length
    }
    return 0
}

function Formatear-Tamano {
    param([long]$Bytes)
    
    if ($Bytes -ge 1MB) {
        return "{0:N2} MB" -f ($Bytes / 1MB)
    } elseif ($Bytes -ge 1KB) {
        return "{0:N2} KB" -f ($Bytes / 1KB)
    } else {
        return "$Bytes bytes"
    }
}

# PROGRAMA PRINCIPAL
try {
    Mostrar-Banner
    
    # Verificar que cwebp este disponible
    if (!(Verificar-Cwebp)) {
        exit 1
    }
    
    # Obtener ruta de la carpeta
    $rutaCarpeta = Obtener-RutaCarpeta -RutaInicial $RutaCarpeta
    Write-Host "Carpeta seleccionada: $rutaCarpeta" -ForegroundColor Green
    
    # Obtener nivel de compresion
    $nivelCompresion = Obtener-NivelCompresion -NivelInicial $NivelCompresion
    Write-Host "Nivel de compresion: $nivelCompresion" -ForegroundColor Green
    
    # Crear carpeta de destino
    $carpetaDestino = Crear-CarpetaOptimizada -RutaBase $rutaCarpeta
    
    # Buscar archivos de imagen
    $extensionesImagen = @("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif", "*.gif")
    $archivosImagen = @()
    
    foreach ($extension in $extensionesImagen) {
        $archivosImagen += Get-ChildItem -Path $rutaCarpeta -Filter $extension -File
    }
    
    if ($archivosImagen.Count -eq 0) {
        Write-Host "No se encontraron archivos de imagen en la carpeta especificada." -ForegroundColor Yellow
        Write-Host "Extensiones soportadas: jpg, jpeg, png, bmp, tiff, tif, gif" -ForegroundColor Gray
        exit 0
    }
    
    Write-Host ""
    Write-Host "Se encontraron $($archivosImagen.Count) archivo(s) de imagen" -ForegroundColor Cyan
    Write-Host "Iniciando proceso de optimizacion..." -ForegroundColor Cyan
    Write-Host ""
    
    $procesados = 0
    $exitosos = 0
    $tamanoOriginalTotal = 0
    $tamanoOptimizadoTotal = 0
    
    foreach ($archivo in $archivosImagen) {
        $procesados++
        $nombreSinExtension = [System.IO.Path]::GetFileNameWithoutExtension($archivo.Name)
        $archivoDestino = Join-Path $carpetaDestino ($nombreSinExtension + ".webp")
        
        Write-Host "[$procesados/$($archivosImagen.Count)] Procesando: $($archivo.Name)" -ForegroundColor White
        
        $tamanoOriginal = Obtener-TamanoArchivo -Ruta $archivo.FullName
        $tamanoOriginalTotal += $tamanoOriginal
        
        if (Comprimir-Imagen -ArchivoOrigen $archivo.FullName -ArchivoDestino $archivoDestino -Calidad $nivelCompresion) {
            $tamanoOptimizado = Obtener-TamanoArchivo -Ruta $archivoDestino
            $tamanoOptimizadoTotal += $tamanoOptimizado
            
            $porcentajeReduccion = if ($tamanoOriginal -gt 0) { 
                [math]::Round(((($tamanoOriginal - $tamanoOptimizado) / $tamanoOriginal) * 100), 1) 
            } else { 0 }
            
            Write-Host "  EXITO - $(Formatear-Tamano $tamanoOriginal) -> $(Formatear-Tamano $tamanoOptimizado) (-$porcentajeReduccion%)" -ForegroundColor Green
            $exitosos++
        } else {
            Write-Host "  ERROR al procesar el archivo" -ForegroundColor Red
        }
    }
    
    # Mostrar resumen
    Write-Host ""
    Write-Host "============== RESUMEN ==============" -ForegroundColor Cyan
    Write-Host "Archivos procesados: $procesados" -ForegroundColor White
    Write-Host "Archivos exitosos: $exitosos" -ForegroundColor Green
    Write-Host "Archivos con error: $($procesados - $exitosos)" -ForegroundColor Red
    
    if ($tamanoOriginalTotal -gt 0) {
        $reduccionTotal = [math]::Round(((($tamanoOriginalTotal - $tamanoOptimizadoTotal) / $tamanoOriginalTotal) * 100), 1)
        Write-Host "Tamano original total: $(Formatear-Tamano $tamanoOriginalTotal)" -ForegroundColor White
        Write-Host "Tamano optimizado total: $(Formatear-Tamano $tamanoOptimizadoTotal)" -ForegroundColor White
        Write-Host "Reduccion total: $reduccionTotal%" -ForegroundColor Green
        Write-Host "Espacio ahorrado: $(Formatear-Tamano ($tamanoOriginalTotal - $tamanoOptimizadoTotal))" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Archivos optimizados guardados en: $carpetaDestino" -ForegroundColor Yellow
    Write-Host "Los archivos originales se mantuvieron sin cambios." -ForegroundColor Gray
    
} catch {
    Write-Host "Error inesperado: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}