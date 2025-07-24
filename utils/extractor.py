import openpyxl
from collections import defaultdict
import json
import re

def determinar_nivel_educativo(incorporacion, programa):
    """Determina el nivel educativo basado en la incorporación y programa"""
    
    if not incorporacion:
        incorporacion = ""
    
    incorporacion_lower = str(incorporacion).lower().strip()
    programa_lower = str(programa).lower().strip()
    
    # CASOS ESPECIALES PRIORITARIOS (verificar primero)
    
    # BIS - Bachillerato Internacional Escolarizado
    if programa_lower == "bis" or "bis" in programa_lower:
        return "Bachillerato"
    
    # Programas que típicamente son de Educación Continua (menos comunes)
    educacion_continua_programas = [
        "diplomado", "curso", "certificación", "capacitación", "continua", 
        "actualización", "especialidad médica", "especialización"
    ]
    for patron in educacion_continua_programas:
        if patron in programa_lower or patron in incorporacion_lower:
            return "Educación Continua"
    
    # Maestrías (menos comunes, verificar antes que licenciaturas)
    maestrias_palabras = ["maestría", "maestrias", "master", "mba", "magister", "posgrado"]
    for palabra in maestrias_palabras:
        if palabra in incorporacion_lower or palabra in programa_lower:
            return "Maestrías"
    
    # Doctorados
    if any(word in incorporacion_lower or word in programa_lower 
           for word in ["doctorado", "phd", "doctor"]):
        return "Doctorados"
    
    # NIVELES BÁSICOS
    if any(word in incorporacion_lower or word in programa_lower 
           for word in ["primaria", "educación básica", "elementary"]):
        return "Primaria"
    
    if any(word in incorporacion_lower or word in programa_lower 
           for word in ["secundaria", "middle school", "educación media"]):
        return "Secundaria"
    
    if any(word in incorporacion_lower or word in programa_lower 
           for word in ["bachillerato", "preparatoria", "high school", "bachiller"]):
        return "Bachillerato"
    
    # LICENCIATURAS (la mayoría de casos)
    # Lista de programas que claramente son licenciaturas
    licenciaturas_programas = [
        "derecho", "medicina", "enfermería", "psicología", "arquitectura",
        "ingeniería", "administración", "contaduría", "mercadotecnia", 
        "negocios", "comunicación", "periodismo", "diseño", "arte",
        "criminología", "criminalística", "trabajo social", "nutrición",
        "gastronomía", "turismo", "educación", "pedagogía", "filosofía",
        "historia", "sociología", "antropología", "geografía", "biología",
        "química", "física", "matemáticas", "informática", "sistemas",
        "ciencias", "terapia", "dentista", "odontología", "veterinaria",
        "farmacéutico", "farmacia", "optometría", "fisioterapia"
    ]
    
    # Si el programa contiene alguna palabra de licenciaturas
    for palabra_lic in licenciaturas_programas:
        if palabra_lic in programa_lower:
            return "Licenciaturas"
    
    # Si la incorporación menciona "UDG" o "SICYT" generalmente son licenciaturas
    if any(org in incorporacion_lower for org in ["udg", "sicyt"]):
        return "Licenciaturas"
    
    # CASOS TÉCNICOS
    if any(word in incorporacion_lower or word in programa_lower 
           for word in ["técnico", "tsu", "profesional asociado", "tecnólogo"]):
        return "Técnico Superior"
    
    # Si llegamos aquí y no hay incorporación específica, 
    # pero el programa parece académico (más de 4 caracteres), probablemente sea licenciatura
    if len(programa_lower) > 4 and not any(char.isdigit() for char in programa_lower):
        return "Licenciaturas"
    
    # Por defecto, sin clasificar
    return "Sin Clasificar"

def procesar_hoja_mejorada(ws, nombre_hoja):
    """Procesa una hoja específica del archivo Excel con mejor detección de estructura"""
    resultados_hoja = defaultdict(list)
    
    plantel_actual = None
    incorporacion_actual = None
    modalidad_actual = None
    
    # Encontrar inicio de los datos
    start_row = None
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        if row and len(row) > 0 and row[0] and "Plantel" in str(row[0]):
            start_row = i + 1
            break
    
    if start_row is None:
        print(f"⚠️  No se encontró encabezado 'Plantel' en la hoja {nombre_hoja}")
        return resultados_hoja
    
    print(f"📊 Procesando desde la fila {start_row} en {nombre_hoja}")
    
    # Recorrer desde el inicio real
    for i in range(start_row, ws.max_row + 1):
        try:
            row = [cell.value if cell.value is not None else "" for cell in ws[i]]
            
            # Asegurar que tenemos al menos 4 columnas
            while len(row) < 4:
                row.append("")
            
            # Detectar nuevo plantel (columna A) - el plantel se extiende verticalmente
            if row[0] and str(row[0]).strip() and str(row[0]).strip() not in ["Plantel", ""]:
                plantel_candidato = str(row[0]).strip()
                # Verificar que no sea un programa o dato erróneo
                if len(plantel_candidato) > 2 and not plantel_candidato.lower() in ['udg', 'sicyt']:
                    plantel_actual = plantel_candidato
                    print(f"🏫 Nuevo plantel detectado: {plantel_actual}")
            
            # Detectar nueva incorporación (columna B)
            if row[1] and str(row[1]).strip():
                incorporacion_candidata = str(row[1]).strip()
                # Solo actualizar si parece ser una incorporación válida
                if incorporacion_candidata not in ["", "Incorporación"] and len(incorporacion_candidata) > 2:
                    incorporacion_actual = incorporacion_candidata
                    print(f"📜 Nueva incorporación: {incorporacion_actual}")
            
            # Detectar modalidad (columna D)
            if row[3] and str(row[3]).strip():
                modalidad_candidata = str(row[3]).strip()
                if modalidad_candidata not in ["", "Modalidad"] and len(modalidad_candidata) > 2:
                    modalidad_actual = modalidad_candidata
            
            # Extraer programa (columna C)
            programa = row[2]
            if programa and str(programa).strip() and plantel_actual:
                programa_str = str(programa).strip()
                # Limpiar el programa
                programa_str = ' '.join(programa_str.split())
                
                # Verificar que no sea un encabezado
                if programa_str not in ["Programa", ""] and len(programa_str) > 2:
                    # Determinar nivel educativo
                    nivel_educativo = determinar_nivel_educativo(incorporacion_actual, programa_str)
                    
                    # Debug: mostrar clasificación para casos problemáticos
                    if not incorporacion_actual or incorporacion_actual == "No especificada":
                        print(f"    🔍 Programa sin incorporación: '{programa_str}' → Clasificado como: {nivel_educativo}")
                    
                    programa_info = {
                        "programa": programa_str,
                        "incorporacion": incorporacion_actual or "No especificada",
                        "modalidad": modalidad_actual or "No especificada",
                        "hoja": nombre_hoja,
                        "nivel_educativo": nivel_educativo
                    }
                    
                    resultados_hoja[plantel_actual].append(programa_info)
                    print(f"  📚 Programa agregado: {programa_str} ({nivel_educativo})")
        
        except Exception as e:
            print(f"⚠️  Error procesando fila {i}: {e}")
            continue
    
    return resultados_hoja

# Función corregida (había un typo en el nombre)
def determiner_nivel_educativo(incorporacion, programa):
    return determinar_nivel_educativo(incorporacion, programa)

def generar_estructura_educativa(todos_resultados):
    """Genera estructura organizada por nivel educativo > programa > plantel"""
    estructura = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for plantel, programas in todos_resultados.items():
        if not plantel or str(plantel).strip() == "":
            continue
            
        plantel_limpio = str(plantel).strip()
        
        for programa_info in programas:
            programa = programa_info["programa"]
            nivel = programa_info["nivel_educativo"]
            
            if not programa or str(programa).strip() == "":
                continue
            
            programa_limpio = ' '.join(str(programa).split())
            
            # Evitar duplicados usando una clave única
            modalidad_incorporacion = f"{programa_info['modalidad']}|{programa_info['incorporacion']}"
            
            # Verificar si ya existe esta combinación
            existe = False
            for item in estructura[nivel][programa_limpio][plantel_limpio]:
                item_key = f"{item['modalidad']}|{item['incorporacion']}"
                if item_key == modalidad_incorporacion:
                    existe = True
                    break
            
            if not existe:
                estructura[nivel][programa_limpio][plantel_limpio].append({
                    "modalidad": programa_info["modalidad"],
                    "incorporacion": programa_info["incorporacion"],
                    "hoja_fuente": programa_info["hoja"]
                })
    
    return estructura

# EJECUCIÓN PRINCIPAL
print("🚀 Iniciando procesamiento del archivo Excel...")

# Cargar el archivo Excel
try:
    wb = openpyxl.load_workbook("oferta.xlsx")
    print("✅ Archivo Excel cargado correctamente")
except FileNotFoundError:
    print("❌ Error: No se encontró el archivo 'oferta.xlsx'")
    exit(1)

# Nombres de las hojas a procesar
hojas = ["GDL", "VALLARTA", "TEPA"]

# Diccionario para almacenar todos los resultados
todos_resultados = defaultdict(list)

# Procesar cada hoja
for nombre_hoja in hojas:
    if nombre_hoja in wb.sheetnames:
        print(f"\n📄 Procesando hoja: {nombre_hoja}")
        ws = wb[nombre_hoja]
        resultados_hoja = procesar_hoja_mejorada(ws, nombre_hoja)
        
        # Agregar los resultados de esta hoja al diccionario general
        for plantel, programas in resultados_hoja.items():
            todos_resultados[plantel].extend(programas)
            
        print(f"✅ Hoja {nombre_hoja} procesada: {len(resultados_hoja)} planteles encontrados")
    else:
        print(f"⚠️  Hoja '{nombre_hoja}' no encontrada en el archivo")

# Generar estructura educativa
print("\n🏗️  Generando estructura educativa...")
estructura_educativa = generar_estructura_educativa(todos_resultados)

# Convertir a diccionario regular para el JSON
estructura_final = {}
for nivel in sorted(estructura_educativa.keys()):
    estructura_final[nivel] = {}
    for programa in sorted(estructura_educativa[nivel].keys()):
        estructura_final[nivel][programa] = {}
        for plantel in sorted(estructura_educativa[nivel][programa].keys()):
            estructura_final[nivel][programa][plantel] = estructura_educativa[nivel][programa][plantel]

# Guardar JSON estructurado
with open("estructura_educativa.json", "w", encoding="utf-8") as archivo_json:
    json.dump(estructura_final, archivo_json, ensure_ascii=False, indent=2)

# Generar archivo de texto legible
with open("estructura_educativa.txt", "w", encoding="utf-8") as archivo_txt:
    archivo_txt.write("ESTRUCTURA EDUCATIVA - PROGRAMAS POR NIVEL\n")
    archivo_txt.write("=" * 60 + "\n\n")
    
    for nivel in sorted(estructura_final.keys()):
        archivo_txt.write(f"🎓 NIVEL: {nivel.upper()}\n")
        archivo_txt.write("=" * (len(nivel) + 10) + "\n")
        
        for programa in sorted(estructura_final[nivel].keys()):
            archivo_txt.write(f"\n📚 Programa: {programa}\n")
            archivo_txt.write("-" * (len(programa) + 12) + "\n")
            
            for plantel in sorted(estructura_final[nivel][programa].keys()):
                archivo_txt.write(f"  🏫 Plantel: {plantel}\n")
                
                for info in estructura_final[nivel][programa][plantel]:
                    archivo_txt.write(f"    📍 Modalidad: {info['modalidad']}\n")
                    archivo_txt.write(f"    📜 Incorporación: {info['incorporacion']}\n")
                    archivo_txt.write(f"    📄 Fuente: {info['hoja_fuente']}\n")
                    archivo_txt.write("    " + "-" * 30 + "\n")
                archivo_txt.write("\n")
        archivo_txt.write("\n" + "=" * 60 + "\n\n")

# Mostrar resumen final
print("\n📊 RESUMEN FINAL:")
print("=" * 50)

total_programas = 0
total_planteles = set()

for nivel in sorted(estructura_final.keys()):
    programas_nivel = len(estructura_final[nivel])
    total_programas += programas_nivel
    
    planteles_nivel = set()
    for programa in estructura_final[nivel]:
        for plantel in estructura_final[nivel][programa]:
            planteles_nivel.add(plantel)
            total_planteles.add(plantel)
    
    print(f"\n🎓 {nivel}: {programas_nivel} programa{'s' if programas_nivel > 1 else ''}")
    print(f"   📍 Disponible en {len(planteles_nivel)} plantel{'es' if len(planteles_nivel) > 1 else ''}")
    
    # Mostrar algunos ejemplos
    ejemplos = list(estructura_final[nivel].keys())[:3]
    for programa in ejemplos:
        planteles_programa = len(estructura_final[nivel][programa])
        print(f"   • {programa} ({planteles_programa} plantel{'es' if planteles_programa > 1 else ''})")
    
    if len(estructura_final[nivel]) > 3:
        print(f"   ... y {len(estructura_final[nivel]) - 3} programa{'s' if len(estructura_final[nivel]) - 3 > 1 else ''} más")

# Mostrar casos especiales detectados
print(f"\n🔍 CASOS ESPECIALES DETECTADOS:")
casos_especiales = defaultdict(list)

for nivel in sorted(estructura_final.keys()):
    for programa in estructura_final[nivel]:
        for plantel in estructura_final[nivel][programa]:
            for info in estructura_final[nivel][programa][plantel]:
                if info['incorporacion'] == "No especificada":
                    casos_especiales[nivel].append(f"{programa} (en {plantel})")

if casos_especiales:
    for nivel, programas in casos_especiales.items():
        print(f"\n📋 {nivel} sin incorporación especificada:")
        for programa in programas[:5]:  # Mostrar solo los primeros 5
            print(f"   • {programa}")
        if len(programas) > 5:
            print(f"   ... y {len(programas) - 5} más")
else:
    print("   ✅ Todos los programas tienen incorporación especificada")

print(f"\n📈 TOTALES:")
print(f"   🎓 Total de programas únicos: {total_programas}")
print(f"   🏫 Total de planteles únicos: {len(total_planteles)}")
print(f"   📚 Total de niveles educativos: {len(estructura_final)}")

print(f"\n✅ Procesamiento completado!")
print(f"📄 Archivos generados:")
print(f"   • estructura_educativa.json - Datos estructurados")
print(f"   • estructura_educativa.txt - Reporte legible")

# Ejemplo de consulta
print(f"\n🔍 EJEMPLO DE USO:")
if "Licenciaturas" in estructura_final and estructura_final["Licenciaturas"]:
    primer_programa = list(estructura_final["Licenciaturas"].keys())[0]
    primer_plantel = list(estructura_final["Licenciaturas"][primer_programa].keys())[0]
    
    print(f"Para consultar '{primer_programa}' en '{primer_plantel}':")
    print(f"estructura_final['Licenciaturas']['{primer_programa}']['{primer_plantel}']")
    
    ejemplo_info = estructura_final["Licenciaturas"][primer_programa][primer_plantel][0]
    print(f"Resultado: Modalidad '{ejemplo_info['modalidad']}', Incorporación '{ejemplo_info['incorporacion']}'")