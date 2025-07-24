import openpyxl
from collections import defaultdict
import json

def procesar_hoja(ws, nombre_hoja):
    """Procesa una hoja específica del archivo Excel"""
    resultados_hoja = defaultdict(list)
    
    plantel_actual = None
    incorporacion_actual = None
    modalidad_actual = None
    
    # Encontrar inicio de los datos (fila donde están los encabezados)
    start_row = None
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if row[0] and "Plantel" in str(row[0]):
            start_row = i + 1
            break
    
    if start_row is None:
        print(f"⚠️  No se encontró encabezado 'Plantel' en la hoja {nombre_hoja}")
        return resultados_hoja
    
    # Recorrer desde el inicio real
    for i in range(start_row, ws.max_row):
        row = [cell.value for cell in ws[i]]
        
        # Detectar nuevo plantel (columna A)
        if row[0] and row[0] not in ["Plantel", ""]:
            plantel_actual = str(row[0]).strip()
            # Validar que no sea None después del strip
            if not plantel_actual:
                plantel_actual = None
        
        # Detectar nueva incorporación (columna B)
        if row[1]:
            incorporacion_actual = str(row[1]).strip()
        
        # Detectar modalidad (columna D)
        if row[3]:
            modalidad_actual = str(row[3]).strip()
        
        # Extraer programa (columna C) - PRESERVAR NOMBRE COMPLETO
        programa = row[2]
        if programa and plantel_actual:  # Solo agregar si tenemos plantel válido
            # Convertir a string y hacer strip, pero preservar espacios internos
            programa_str = str(programa).strip()
            # Reemplazar múltiples espacios internos por uno solo, pero mantener el nombre completo
            programa_str = ' '.join(programa_str.split())
            
            if programa_str:  # Solo si el programa no está vacío
                resultados_hoja[plantel_actual].append({
                    "programa": programa_str,
                    "incorporacion": incorporacion_actual or "No especificada",
                    "modalidad": modalidad_actual or "No especificada",
                    "hoja": nombre_hoja
                })
    
    return resultados_hoja

# Cargar el archivo Excel
wb = openpyxl.load_workbook("oferta.xlsx")

# Nombres de las hojas a procesar
hojas = ["GDL", "VALLARTA", "TEPA"]

# Diccionario para almacenar todos los resultados
todos_resultados = defaultdict(list)

# Procesar cada hoja
for nombre_hoja in hojas:
    if nombre_hoja in wb.sheetnames:
        print(f"📄 Procesando hoja: {nombre_hoja}")
        ws = wb[nombre_hoja]
        resultados_hoja = procesar_hoja(ws, nombre_hoja)
        
        # Agregar los resultados de esta hoja al diccionario general
        for plantel, programas in resultados_hoja.items():
            todos_resultados[plantel].extend(programas)
    else:
        print(f"⚠️  Hoja '{nombre_hoja}' no encontrada en el archivo")

# Reorganizar por programa académico y luego por plantel
programas_por_plantel = defaultdict(lambda: defaultdict(list))

for plantel, programas in todos_resultados.items():
    # Filtrar planteles None o vacíos
    if plantel is None or str(plantel).strip() == "":
        continue
        
    for programa_info in programas:
        programa = programa_info["programa"]
        if programa is None or str(programa).strip() == "":
            continue
        
        # Asegurar que el programa mantenga su formato original
        programa_limpio = ' '.join(str(programa).split())
        
        programas_por_plantel[programa_limpio][plantel].append({
            "incorporacion": programa_info["incorporacion"],
            "modalidad": programa_info["modalidad"],
            "hoja": programa_info["hoja"]
        })

# Generar archivo de texto con formato mejorado
with open("programas_por_plantel.txt", "w", encoding="utf-8") as archivo:
    archivo.write("PROGRAMAS ACADÉMICOS POR PLANTEL\n")
    archivo.write("=" * 50 + "\n\n")
    
    # Ordenar programas alfabéticamente (filtrar None)
    programas_validos = [p for p in programas_por_plantel.keys() if p is not None and str(p).strip()]
    
    for programa in sorted(programas_validos):
        # Escribir el programa completo sin cortes
        archivo.write(f"🎓 PROGRAMA: {programa}\n")
        archivo.write("-" * (len(programa) + 12) + "\n")
        
        # Ordenar planteles alfabéticamente (filtrar None)
        planteles_validos = [p for p in programas_por_plantel[programa].keys() if p is not None and str(p).strip()]
        
        for plantel in sorted(planteles_validos):
            modalidades = programas_por_plantel[programa][plantel]
            archivo.write(f"  📍 Plantel: {plantel}\n")
            
            # Mostrar modalidades únicas para este plantel
            modalidades_unicas = {}
            for mod_info in modalidades:
                # Preservar modalidad completa
                modalidad_completa = ' '.join(str(mod_info["modalidad"]).split())
                incorporacion_completa = ' '.join(str(mod_info["incorporacion"]).split())
                key = (modalidad_completa, incorporacion_completa)
                if key not in modalidades_unicas:
                    modalidades_unicas[key] = mod_info["hoja"]
            
            for (modalidad, incorporacion), hoja in modalidades_unicas.items():
                archivo.write(f"    • Modalidad: {modalidad}\n")
                archivo.write(f"      Incorporación: {incorporacion}\n")
                archivo.write(f"      Fuente: Hoja {hoja}\n")
            
            archivo.write("\n")
        archivo.write("\n")

# Función para determinar el nivel educativo basado en el programa y la incorporación
def determinar_nivel_educativo(programa, incorporacion):
    """Determina el nivel educativo basado en el programa y la columna de incorporación"""
    programa_lower = programa.lower().strip()
    incorporacion_lower = incorporacion.lower().strip() if incorporacion else ""
    
    # Exclusiones - estos no son licenciaturas
    exclusiones = ['bis', 'bachillerato general', 'primaria']
    if any(excl in programa_lower for excl in exclusiones):
        if 'bis' in programa_lower:
            return "Bachillerato Internacional"
        elif 'bachillerato' in programa_lower:
            return "Bachillerato"
        elif 'primaria' in programa_lower:
            return "Educación Básica"
        else:
            return "Otros Programas"
    
    # Si en la columna B (incorporación) dice "MAESTRÍAS" o similar, es maestría
    if any(keyword in incorporacion_lower for keyword in ['maestría', 'maestrias', 'master', 'mba']):
        return "Maestrías"
    
    # Si en la columna B dice "DOCTORADO" o similar, es doctorado
    if any(keyword in incorporacion_lower for keyword in ['doctorado', 'phd']):
        return "Doctorados"
    
    # Si en la columna B dice "ESPECIALIDAD" o similar
    if any(keyword in incorporacion_lower for keyword in ['especialidad', 'especialización']):
        return "Especialidades"
    
    # Si en la columna B dice "DIPLOMADO" o similar
    if any(keyword in incorporacion_lower for keyword in ['diplomado', 'curso', 'certificación']):
        return "Diplomados y Cursos"
    
    # Si en la columna B dice "TÉCNICO" o similar
    if any(keyword in incorporacion_lower for keyword in ['técnico', 'tsu', 'profesional asociado']):
        return "Técnico Superior"
    
    # Por defecto, todo lo demás (que no esté en exclusiones) es Licenciatura
    return "Licenciaturas"

# Generar archivo JSON estructurado por nivel educativo
datos_por_nivel = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for programa in programas_por_plantel:
    programa_completo = ' '.join(str(programa).split())
    
    for plantel in programas_por_plantel[programa]:
        plantel_completo = ' '.join(str(plantel).split())
        modalidades_unicas = {}
        
        for mod_info in programas_por_plantel[programa][plantel]:
            modalidad_completa = ' '.join(str(mod_info["modalidad"]).split())
            incorporacion_completa = ' '.join(str(mod_info["incorporacion"]).split())
            
            # Determinar nivel educativo usando programa e incorporación
            nivel_educativo = determinar_nivel_educativo(programa_completo, incorporacion_completa)
            
            key = (modalidad_completa, incorporacion_completa)
            if key not in modalidades_unicas:
                modalidades_unicas[key] = (mod_info["hoja"], nivel_educativo)
        
        for (modalidad, incorporacion), (hoja, nivel) in modalidades_unicas.items():
            datos_por_nivel[nivel][programa_completo][plantel_completo].append({
                "modalidad": modalidad,
                "incorporacion": incorporacion,
                "hoja_fuente": hoja
            })

# Convertir a diccionario regular para el JSON
datos_estructurados = {}
for nivel in sorted(datos_por_nivel.keys()):
    datos_estructurados[nivel] = {}
    for programa in sorted(datos_por_nivel[nivel].keys()):
        datos_estructurados[nivel][programa] = dict(datos_por_nivel[nivel][programa])

# Guardar JSON con nombres completos
with open("programas_estructura.json", "w", encoding="utf-8") as archivo_json:
    json.dump(datos_estructurados, archivo_json, ensure_ascii=False, indent=2)

print("✅ Procesamiento completado!")
print("📄 Archivo generado: programas_por_plantel.txt")
print("📄 Archivo JSON generado: programas_estructura.json")

# Mostrar resumen por nivel educativo
print(f"\n📊 RESUMEN:")
programas_validos = [p for p in programas_por_plantel.keys() if p is not None and str(p).strip()]
print(f"Total de programas únicos: {len(programas_validos)}")
print(f"Total de planteles únicos: {len([p for p in set(todos_resultados.keys()) if p is not None and str(p).strip()])}")

print("\n🎓 Programas por nivel educativo:")
for nivel in sorted(datos_estructurados.keys()):
    programas_nivel = len(datos_estructurados[nivel])
    print(f"\n📚 {nivel}: {programas_nivel} programa{'s' if programas_nivel > 1 else ''}")
    
    # Mostrar algunos ejemplos de programas por nivel
    programas_ejemplos = list(datos_estructurados[nivel].keys())[:3]
    for programa in programas_ejemplos:
        planteles_count = len(datos_estructurados[nivel][programa])
        print(f"   • {programa} (en {planteles_count} plantel{'es' if planteles_count > 1 else ''})")
    
    if len(datos_estructurados[nivel]) > 3:
        print(f"   ... y {len(datos_estructurados[nivel]) - 3} más")

# Ejemplo de consulta específica
print("\n🔍 Ejemplo de estructura del JSON:")
if "Licenciaturas" in datos_estructurados:
    primer_programa = list(datos_estructurados["Licenciaturas"].keys())[0]
    print(f"📖 Nivel: Licenciaturas")
    print(f"   📋 Programa: {primer_programa}")
    
    for plantel, modalidades in datos_estructurados["Licenciaturas"][primer_programa].items():
        print(f"      🏫 Plantel: {plantel}")
        for modalidad_info in modalidades:
            print(f"         📍 Modalidad: {modalidad_info['modalidad']}")
            print(f"         📝 Incorporación: {modalidad_info['incorporacion']}")
        break  # Solo mostrar el primer plantel como ejemplo