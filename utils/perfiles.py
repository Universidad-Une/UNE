import pandas as pd
import json

def excel_to_js_array():
    # Leer el archivo Excel (todas las hojas)
    excel_file = pd.ExcelFile('Perfiles.xlsx')
    
    # Si hay múltiples hojas, procesar todas
    all_data = []
    
    for sheet_name in excel_file.sheet_names:
        print(f"📄 Procesando hoja: {sheet_name}")
        df = pd.read_excel('Perfiles.xlsx', sheet_name=sheet_name)
        
        # Limpiar los nombres de las columnas
        df.columns = df.columns.str.strip()
        
        # SOLUCIÓN: Propagar valores hacia abajo para celdas fusionadas
        columns_to_fill = ['CARRERA', 'INCORPORACIÓN', 'PERFIL DE INGRESO']  # Columnas que suelen estar fusionadas
        
        for col in columns_to_fill:
            if col in df.columns:
                df[col] = df[col].ffill()  # Forward fill
        
        # Reemplazar NaN con strings vacíos
        df = df.fillna('')
        
        # Filtrar filas completamente vacías
        df = df[df.astype(str).apply(lambda x: x.str.strip().ne('').any(), axis=1)]
        
        # NUEVA LÓGICA: Consolidar filas que pertenecen al mismo perfil
        consolidated_data = []
        current_group = None
        
        for _, row in df.iterrows():
            # Crear una clave única basada en CARRERA + INCORPORACIÓN + PERFIL DE INGRESO
            group_key = f"{row.get('CARRERA', '')}-{row.get('INCORPORACIÓN', '')}-{row.get('PERFIL DE INGRESO', '')}"
            
            # Si es un nuevo grupo (tiene valores en las columnas principales)
            if (row.get('CARRERA', '').strip() != '' and 
                row.get('INCORPORACIÓN', '').strip() != '' and
                current_group is None):
                
                # Iniciar un nuevo grupo
                current_group = row.to_dict()
                
            elif current_group is not None:
                # Si estamos en un grupo y encontramos continuación del PERFIL DE EGRESO
                if (row.get('CARRERA', '').strip() == current_group.get('CARRERA', '') and
                    row.get('INCORPORACIÓN', '').strip() == current_group.get('INCORPORACIÓN', '') and
                    row.get('PERFIL DE EGRESO', '').strip() != ''):
                    
                    # Concatenar el PERFIL DE EGRESO
                    current_egreso = current_group.get('PERFIL DE EGRESO', '').strip()
                    new_egreso = row.get('PERFIL DE EGRESO', '').strip()
                    
                    if current_egreso and new_egreso:
                        # Si ambos tienen contenido, concatenar con espacio
                        current_group['PERFIL DE EGRESO'] = current_egreso + ' ' + new_egreso
                    elif new_egreso:
                        # Si solo el nuevo tiene contenido, usarlo
                        current_group['PERFIL DE EGRESO'] = new_egreso
                    
                else:
                    # Terminó el grupo actual, guardarlo y empezar uno nuevo
                    if current_group:
                        consolidated_data.append(current_group.copy())
                    
                    # Si la fila actual tiene datos principales, iniciar nuevo grupo
                    if (row.get('CARRERA', '').strip() != '' and 
                        row.get('INCORPORACIÓN', '').strip() != ''):
                        current_group = row.to_dict()
                    else:
                        current_group = None
        
        # No olvidar agregar el último grupo
        if current_group:
            consolidated_data.append(current_group)
        
        # Si hay múltiples hojas, agregar el nombre de la hoja
        if len(excel_file.sheet_names) > 1:
            for record in consolidated_data:
                record['_sheet'] = sheet_name
        
        all_data.extend(consolidated_data)
    
    # Función para limpiar y formatear texto
    def clean_text(text):
        if not isinstance(text, str):
            return text
        
        # Reemplazar saltos de línea por espacios
        text = text.replace('\n', ' ')
        
        # Remover viñetas (●, •, -, *) y limpiar
        text = text.replace('●', '')
        text = text.replace('•', '')
        text = text.replace('- ', '')
        text = text.replace('* ', '')
        
        # Limpiar espacios múltiples y espacios al inicio/final
        text = ' '.join(text.split())
        
        # Limpiar comillas problemáticas y normalizarlas
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace("'", "'")
        text = text.replace("'", "'")
        
        return text.strip()
    
    # Limpiar y normalizar los datos finales
    for record in all_data:
        for key, value in record.items():
            if isinstance(value, str) and not key.startswith('_'):
                # Aplicar limpieza especial a campos de texto largo
                if key in ['PERFIL DE INGRESO', 'PERFIL DE EGRESO']:
                    record[key] = clean_text(value)
                else:
                    # Para otros campos, solo limpieza básica
                    record[key] = value.strip().replace('\n', ' ')
                    record[key] = ' '.join(record[key].split())
    
    # Crear el contenido del archivo JavaScript completo
    js_content = f"""// Array generado automáticamente desde Perfiles.xlsx
// Total de registros: {len(all_data)}
// Generado el: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

const perfiles = {json.dumps(all_data, ensure_ascii=False, indent=2)};

// Para usar en Node.js (CommonJS)
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = perfiles;
}}

// Para usar en el navegador
if (typeof window !== 'undefined') {{
    window.perfiles = perfiles;
}}

// Export por defecto para ES6 modules
export default perfiles;

// Funciones de utilidad incluidas
export const getByCarrera = (carrera) => {{
    return perfiles.filter(p => p.CARRERA && p.CARRERA.toLowerCase().includes(carrera.toLowerCase()));
}};

export const getAllCareers = () => {{
    return [...new Set(perfiles.map(p => p.CARRERA).filter(Boolean))];
}};

export const getTotalRecords = () => {{
    return perfiles.length;
}};

export const getProfilesByIncorporacion = (incorporacion) => {{
    return perfiles.filter(p => p.INCORPORACIÓN && p.INCORPORACIÓN.toLowerCase().includes(incorporacion.toLowerCase()));
}};
"""
    
    # Guardar como archivo JavaScript
    with open('perfiles.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ Archivo generado exitosamente:")
    print(f"   📄 perfiles.js")
    print(f"   📊 {len(all_data)} registros consolidados")
    print(f"   📋 {len(excel_file.sheet_names)} hoja(s) procesada(s)")
    
    # Mostrar estadísticas
    if all_data:
        print(f"\n📈 Estadísticas:")
        print(f"   🎯 Columnas encontradas: {list(all_data[0].keys())}")
        
        # Contar carreras únicas
        carreras = set(record.get('CARRERA', '') for record in all_data if record.get('CARRERA'))
        print(f"   🎓 Carreras únicas: {len(carreras)}")
        
        # Mostrar muestra del primer registro
        print(f"\n📝 Muestra del primer registro consolidado:")
        first_record = all_data[0]
        for key, value in first_record.items():
            if key.startswith('_'):  # Skip metadata fields
                continue
            preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            print(f"   {key}: {preview}")
        
        # Verificar longitud de perfiles de egreso
        egreso_lengths = [len(str(record.get('PERFIL DE EGRESO', ''))) for record in all_data]
        if egreso_lengths:
            print(f"\n📏 Longitud de perfiles de egreso:")
            print(f"   📊 Promedio: {sum(egreso_lengths)/len(egreso_lengths):.0f} caracteres")
            print(f"   📈 Máximo: {max(egreso_lengths)} caracteres")
            print(f"   📉 Mínimo: {min(egreso_lengths)} caracteres")

if __name__ == "__main__":
    try:
        excel_to_js_array()
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'Perfiles.xlsx'")
        print("   Asegúrate de que el archivo esté en la misma carpeta que este script")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()