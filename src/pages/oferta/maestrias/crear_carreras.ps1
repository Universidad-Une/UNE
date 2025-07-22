# Ruta base del archivo modelo
$origen = "C:\Users\UNE\Documents\VSCode\UNE\src\pages\oferta\licenciaturas\cirujano_dentista.astro"
$destinoDir = "C:\Users\UNE\Documents\VSCode\UNE\src\pages\oferta\maestrias"

# Crear el directorio si no existe
if (-not (Test-Path $destinoDir)) {
    New-Item -ItemType Directory -Path $destinoDir
}

# Lista de maestrías
$maestrias = @(
    "maestria_educacion",
    "mst_administracion_negocios",
    "mst_finanzas_estrategicas",
    "mst_terapia_familiar_sistemica"
)

# Crear archivos .astro para cada maestría
foreach ($maestria in $maestrias) {
    $nuevoArchivo = Join-Path $destinoDir "$maestria.astro"
    Copy-Item $origen $nuevoArchivo -Force
    Write-Output "Creado: $nuevoArchivo"
}
