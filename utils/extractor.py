#!/usr/bin/env python3
"""
Analizador y Corrector Automático de botones sin nombres accesibles
Encuentra y CORRIGE automáticamente todos los elementos button sin atributos de accesibilidad
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Set
from datetime import datetime

class ButtonAutoFixer:
    def __init__(self, project_path: str, backup: bool = True):
        self.project_path = Path(project_path)
        self.extensions = {'.astro', '.tsx', '.jsx', '.js', '.ts', '.vue', '.svelte', '.html'}
        self.excluded_dirs = {
            'node_modules', '.git', 'dist', '.astro', '.vscode', 
            '__pycache__', '.next', '.nuxt', 'build', 'coverage',
            '.svelte-kit', 'venv', 'env', '.env'
        }
        self.create_backup = backup
        self.processed_files = []
        self.total_fixes = 0
        
        # Compilar expresiones regulares una sola vez
        self._compile_regex_patterns()
        
        # Compilar patrones adicionales para zonas seguras
        self._compile_safe_zone_patterns()
        
        # Cache para sugerencias comunes de botones
        self.common_button_actions = {
            'submit': {'aria_label': 'Enviar formulario', 'title': 'Enviar datos del formulario'},
            'send': {'aria_label': 'Enviar', 'title': 'Enviar información'},
            'save': {'aria_label': 'Guardar cambios', 'title': 'Guardar la información'},
            'delete': {'aria_label': 'Eliminar elemento', 'title': 'Eliminar este elemento'},
            'edit': {'aria_label': 'Editar elemento', 'title': 'Editar este elemento'},
            'close': {'aria_label': 'Cerrar ventana', 'title': 'Cerrar esta ventana'},
            'cancel': {'aria_label': 'Cancelar acción', 'title': 'Cancelar operación actual'},
            'next': {'aria_label': 'Siguiente', 'title': 'Ir al siguiente elemento'},
            'prev': {'aria_label': 'Anterior', 'title': 'Ir al elemento anterior'},
            'play': {'aria_label': 'Reproducir', 'title': 'Reproducir contenido multimedia'},
            'pause': {'aria_label': 'Pausar', 'title': 'Pausar reproducción'},
            'stop': {'aria_label': 'Detener', 'title': 'Detener reproducción'},
            'search': {'aria_label': 'Buscar', 'title': 'Realizar búsqueda'},
            'filter': {'aria_label': 'Filtrar contenido', 'title': 'Aplicar filtros'},
            'sort': {'aria_label': 'Ordenar elementos', 'title': 'Cambiar orden de elementos'},
            'menu': {'aria_label': 'Abrir menú', 'title': 'Mostrar opciones del menú'},
            'toggle': {'aria_label': 'Alternar opción', 'title': 'Cambiar estado de la opción'},
        }
        
        self.icon_patterns = {
            'fa-search': {'aria_label': 'Buscar', 'title': 'Realizar búsqueda'},
            'fa-times': {'aria_label': 'Cerrar', 'title': 'Cerrar ventana'},
            'fa-edit': {'aria_label': 'Editar', 'title': 'Editar elemento'},
            'fa-trash': {'aria_label': 'Eliminar', 'title': 'Eliminar elemento'},
            'fa-save': {'aria_label': 'Guardar', 'title': 'Guardar cambios'},
            'fa-play': {'aria_label': 'Reproducir', 'title': 'Reproducir contenido'},
            'fa-pause': {'aria_label': 'Pausar', 'title': 'Pausar reproducción'},
            'fa-stop': {'aria_label': 'Detener', 'title': 'Detener reproducción'},
            'fa-menu': {'aria_label': 'Menú', 'title': 'Abrir menú de opciones'},
            'fa-bars': {'aria_label': 'Menú', 'title': 'Mostrar menú de navegación'},
            'fa-user': {'aria_label': 'Perfil de usuario', 'title': 'Acceder al perfil'},
            'fa-heart': {'aria_label': 'Me gusta', 'title': 'Marcar como favorito'},
            'fa-share': {'aria_label': 'Compartir', 'title': 'Compartir contenido'},
            'fa-download': {'aria_label': 'Descargar', 'title': 'Descargar archivo'},
            'fa-upload': {'aria_label': 'Subir archivo', 'title': 'Cargar archivo'},
        }
    
    def _compile_regex_patterns(self):
        """Precompila todas las expresiones regulares para mejor rendimiento"""
        self.regex_patterns = {
            # Patrones para botones completos
            'button_complete': re.compile(r'<button\s+[^>]*>.*?</button>', re.IGNORECASE | re.DOTALL),
            'button_self_closing': re.compile(r'<button\s+[^>]*/?>', re.IGNORECASE),
            'button_opening': re.compile(r'<button\s+[^>]*>', re.IGNORECASE),
            
            # Patrones para input type="button", "submit", "reset"
            'input_button': re.compile(r'<input\s+[^>]*type\s*=\s*["\'](?:button|submit|reset)["\'][^>]*/?>', re.IGNORECASE),
            
            # Atributos de accesibilidad
            'aria_label': re.compile(r'aria-label\s*=', re.IGNORECASE),
            'aria_labelledby': re.compile(r'aria-labelledby\s*=', re.IGNORECASE),
            'title': re.compile(r'title\s*=', re.IGNORECASE),
            
            # Otros atributos útiles
            'type': re.compile(r'type\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            'class': re.compile(r'class\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            'id': re.compile(r'id\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            'value': re.compile(r'value\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            'onclick': re.compile(r'onclick\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            
            # Contenido del botón
            'button_content': re.compile(r'<button[^>]*>(.*?)</button>', re.IGNORECASE | re.DOTALL),
            'html_tags': re.compile(r'<[^>]+>'),
            'whitespace': re.compile(r'\s+'),
        }
    
    def _compile_safe_zone_patterns(self):
        """Compila patrones para identificar zonas seguras donde modificar HTML"""
        self.safe_zone_patterns = {
            # Strings en JavaScript/TypeScript (comillas simples y dobles)
            'js_strings_double': re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"', re.DOTALL),
            'js_strings_single': re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'", re.DOTALL),
            'js_template_literals': re.compile(r'`[^`\\]*(?:\\.[^`\\]*)*`', re.DOTALL),
            
            # Estructuras de datos (arrays y objetos)
            'array_brackets': re.compile(r'\[[^\[\]]*\]', re.DOTALL),
            'object_braces': re.compile(r'\{[^{}]*\}', re.DOTALL),
            
            # Comentarios
            'js_line_comments': re.compile(r'//.*$', re.MULTILINE),
            'js_block_comments': re.compile(r'/\*.*?\*/', re.DOTALL),
            'html_comments': re.compile(r'<!--.*?-->', re.DOTALL),
            
            # Script tags completos
            'script_tags': re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            
            # Atributos que contienen HTML (como v-html, innerHTML, etc.)
            'html_attributes': re.compile(r'(?:v-html|innerHTML|dangerouslySetInnerHTML)\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        }
    
    def _identify_safe_zones(self, content: str) -> List[Tuple[int, int]]:
        """Identifica zonas donde es seguro modificar HTML (excluir solo algunas estructuras específicas)"""
        unsafe_zones = []
        
        # Solo excluir comentarios, scripts y atributos especiales (NO strings)
        patterns_to_exclude = ['js_line_comments', 'js_block_comments', 'html_comments', 'script_tags', 'html_attributes']
        
        for pattern_name in patterns_to_exclude:
            if pattern_name in self.safe_zone_patterns:
                pattern = self.safe_zone_patterns[pattern_name]
                for match in pattern.finditer(content):
                    unsafe_zones.append((match.start(), match.end()))
        
        # Manejar solo estructuras de datos anidadas (objetos/arrays complejos)
        unsafe_zones.extend(self._find_complex_nested_structures(content))
        
        # Ordenar y fusionar zonas solapadas
        unsafe_zones.sort()
        merged_unsafe = self._merge_overlapping_ranges(unsafe_zones)
        
        # Convertir a zonas seguras (invertir las zonas inseguras)
        safe_zones = []
        last_end = 0
        
        for start, end in merged_unsafe:
            if start > last_end:
                safe_zones.append((last_end, start))
            last_end = max(last_end, end)
        
        # Agregar zona final si queda contenido
        if last_end < len(content):
            safe_zones.append((last_end, len(content)))
        
        return safe_zones
    
    def _find_complex_nested_structures(self, content: str) -> List[Tuple[int, int]]:
        """Encuentra solo estructuras anidadas complejas, no simples objetos con HTML"""
        nested_zones = []
        
        # Solo buscar estructuras muy anidadas (3+ niveles) que probablemente no contengan HTML
        brace_depth = 0
        complex_start = None
        
        for i, char in enumerate(content):
            if char == '{':
                if brace_depth == 0:
                    complex_start = i
                brace_depth += 1
            elif char == '}':
                brace_depth -= 1
                if brace_depth == 0 and complex_start is not None:
                    # Solo considerar complejo si tiene más de 3 niveles o es muy largo
                    section = content[complex_start:i+1]
                    if section.count('{') >= 3 or len(section) > 500:
                        nested_zones.append((complex_start, i + 1))
                    complex_start = None
        
        return nested_zones
    
    def _merge_overlapping_ranges(self, ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Fusiona rangos que se solapan"""
        if not ranges:
            return []
        
        merged = [ranges[0]]
        for current_start, current_end in ranges[1:]:
            last_start, last_end = merged[-1]
            
            if current_start <= last_end:
                # Hay solapamiento, fusionar
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                # No hay solapamiento, agregar como nuevo rango
                merged.append((current_start, current_end))
        
        return merged
    
    def _is_in_safe_zone(self, start: int, end: int, safe_zones: List[Tuple[int, int]]) -> bool:
        """Verifica si una posición está en una zona segura para modificar"""
        for zone_start, zone_end in safe_zones:
            if zone_start <= start and end <= zone_end:
                return True
        return False
    
    def _is_in_string_zone(self, start: int, end: int, content: str) -> bool:
        """Verifica si una posición está dentro de un string de JavaScript/TypeScript"""
        string_zones = []
        
        # Buscar strings con comillas dobles
        for match in self.safe_zone_patterns['js_strings_double'].finditer(content):
            string_zones.append((match.start(), match.end()))
        
        # Buscar strings con comillas simples
        for match in self.safe_zone_patterns['js_strings_single'].finditer(content):
            string_zones.append((match.start(), match.end()))
        
        # Buscar template literals
        for match in self.safe_zone_patterns['js_template_literals'].finditer(content):
            string_zones.append((match.start(), match.end()))
        
        # Verificar si está dentro de algún string
        for zone_start, zone_end in string_zones:
            if zone_start <= start and end <= zone_end:
                return True
        return False
    
    def fix_project(self) -> Dict:
        """Analiza y corrige todo el proyecto automáticamente"""
        print(f"🔧 Iniciando corrección automática de botones en: {self.project_path}")
        print(f"📁 Extensiones a procesar: {', '.join(self.extensions)}")
        
        if self.create_backup:
            backup_dir = self._create_backup()
            print(f"💾 Backup creado en: {backup_dir}")
        
        print("-" * 70)
        
        files = self._get_files_to_analyze()
        
        for file_path in files:
            fixes_count = self._fix_file(file_path)
            if fixes_count > 0:
                self.processed_files.append({
                    'file': str(file_path.relative_to(self.project_path)),
                    'fixes': fixes_count
                })
                self.total_fixes += fixes_count
        
        return self._generate_summary()
    
    def _create_backup(self) -> str:
        """Crea un backup del proyecto antes de hacer modificaciones"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_button_accessibility_{timestamp}"
        
        try:
            shutil.copytree(
                self.project_path, 
                backup_dir,
                ignore=shutil.ignore_patterns(
                    'node_modules', '.git', 'dist', '.astro', 
                    '__pycache__', 'build', 'coverage'
                )
            )
            return backup_dir
        except Exception as e:
            print(f"⚠️  No se pudo crear backup: {e}")
            print("Continuando sin backup...")
            return "No creado"
    
    def _get_files_to_analyze(self) -> List[Path]:
        """Obtiene todos los archivos relevantes del proyecto"""
        files = []
        
        print(f"🔍 Buscando archivos a procesar...")
        
        for file_path in self.project_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in self.extensions and
                not any(excluded_dir in file_path.parts for excluded_dir in self.excluded_dirs)):
                files.append(file_path)
        
        print(f"📁 Archivos encontrados: {len(files)}")
        return files
    
    def _fix_file(self, file_path: Path) -> int:
        """Corrige un archivo específico y retorna el número de correcciones"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
            
            # Aplicar correcciones
            fixed_content, fixes_count = self._apply_fixes_to_content(original_content, file_path)
            
            # Solo escribir si hubo cambios
            if fixes_count > 0:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(fixed_content)
                
                print(f"✅ {file_path.relative_to(self.project_path)}: {fixes_count} botón(es) corregido(s)")
            
            return fixes_count
                
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"⚠️  No se pudo procesar: {file_path} - {str(e)}")
            return 0
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {str(e)}")
            return 0
    
    def _apply_fixes_to_content(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Aplica las correcciones al contenido y retorna el contenido modificado"""
        fixes_count = 0
        modified_content = content
        
        # Identificar zonas seguras para modificar
        safe_zones = self._identify_safe_zones(content)
        
        # Procesar botones completos
        def fix_complete_button(match):
            nonlocal fixes_count
            full_button = match.group(0)
            
            # Verificar si está en una zona segura
            if self._is_in_safe_zone(match.start(), match.end(), safe_zones):
                # Verificar si está dentro de un string
                in_string = self._is_in_string_zone(match.start(), match.end(), content)
                fixed_button = self._fix_single_button(full_button, file_path, in_string)
                if fixed_button != full_button:
                    fixes_count += 1
                    return fixed_button
            return full_button
        
        # Aplicar correcciones a botones completos
        modified_content = self.regex_patterns['button_complete'].sub(
            fix_complete_button, 
            modified_content
        )
        
        # Procesar input buttons
        def fix_input_button(match):
            nonlocal fixes_count
            input_button = match.group(0)
            
            # Verificar si está en una zona segura
            if self._is_in_safe_zone(match.start(), match.end(), safe_zones):
                in_string = self._is_in_string_zone(match.start(), match.end(), content)
                fixed_input = self._fix_input_button(input_button, file_path, in_string)
                if fixed_input != input_button:
                    fixes_count += 1
                    return fixed_input
            return input_button
        
        # Aplicar correcciones a input buttons
        modified_content = self.regex_patterns['input_button'].sub(
            fix_input_button,
            modified_content
        )
        
        return modified_content, fixes_count
    
    def _fix_single_button(self, button_html: str, file_path: Path, in_string: bool = False) -> str:
        """Corrige un botón individual si necesita atributos de accesibilidad"""
        # Extraer tag de apertura
        opening_match = self.regex_patterns['button_opening'].match(button_html)
        if not opening_match:
            return button_html
        
        button_tag = opening_match.group(0)
        
        # Verificar si ya tiene atributos de accesibilidad
        has_accessibility = (
            self.regex_patterns['aria_label'].search(button_tag) or
            self.regex_patterns['title'].search(button_tag) or
            self.regex_patterns['aria_labelledby'].search(button_tag)
        )
        
        if has_accessibility:
            return button_html
        
        # Extraer información del botón
        type_match = self.regex_patterns['type'].search(button_tag)
        button_type = type_match.group(1) if type_match else 'button'
        
        class_match = self.regex_patterns['class'].search(button_tag)
        css_class = class_match.group(1) if class_match else ''
        
        id_match = self.regex_patterns['id'].search(button_tag)
        button_id = id_match.group(1) if id_match else ''
        
        onclick_match = self.regex_patterns['onclick'].search(button_tag)
        onclick = onclick_match.group(1) if onclick_match else ''
        
        # Extraer contenido del botón
        content_match = self.regex_patterns['button_content'].search(button_html)
        button_content = content_match.group(1).strip() if content_match else ''
        clean_button_content = self.regex_patterns['whitespace'].sub(' ', button_content).strip()
        
        # Generar sugerencias
        suggestions = self._generate_button_accessibility_suggestions(
            button_type, clean_button_content, css_class, button_id, onclick
        )
        
        # Aplicar las correcciones con el formato apropiado
        return self._apply_suggestions_to_button(button_html, suggestions, in_string)
    
    def _fix_input_button(self, input_html: str, file_path: Path, in_string: bool = False) -> str:
        """Corrige un input button si necesita atributos de accesibilidad"""
        # Verificar si ya tiene atributos de accesibilidad
        has_accessibility = (
            self.regex_patterns['aria_label'].search(input_html) or
            self.regex_patterns['title'].search(input_html) or
            self.regex_patterns['aria_labelledby'].search(input_html)
        )
        
        if has_accessibility:
            return input_html
        
        # Extraer información del input
        type_match = self.regex_patterns['type'].search(input_html)
        input_type = type_match.group(1) if type_match else 'button'
        
        value_match = self.regex_patterns['value'].search(input_html)
        input_value = value_match.group(1) if value_match else ''
        
        class_match = self.regex_patterns['class'].search(input_html)
        css_class = class_match.group(1) if class_match else ''
        
        id_match = self.regex_patterns['id'].search(input_html)
        input_id = id_match.group(1) if id_match else ''
        
        # Generar sugerencias basadas en el tipo y valor del input
        suggestions = self._generate_input_button_accessibility_suggestions(
            input_type, input_value, css_class, input_id
        )
        
        # Aplicar las correcciones
        return self._apply_suggestions_to_input(input_html, suggestions, in_string)
    
    def _apply_suggestions_to_button(self, original_button: str, suggestions: Dict[str, str], in_string: bool = False) -> str:
        """Aplica las sugerencias de accesibilidad al botón"""
        opening_match = self.regex_patterns['button_opening'].match(original_button)
        if not opening_match:
            return original_button
        
        opening_tag = opening_match.group(0)
        rest_of_button = original_button[len(opening_tag):]
        
        # Generar nuevos atributos con el formato apropiado
        new_attributes = []
        
        if suggestions['aria_label']:
            if in_string:
                new_attributes.append(f'[aria-label="{suggestions["aria_label"]}"]')
            else:
                new_attributes.append(f'aria-label="{suggestions["aria_label"]}"')
        
        if suggestions['title']:
            if in_string:
                new_attributes.append(f'[title="{suggestions["title"]}"]')
            else:
                new_attributes.append(f'title="{suggestions["title"]}"')
        
        if not new_attributes:
            return original_button
        
        # Insertar los nuevos atributos
        tag_without_closing = opening_tag.rstrip('>')
        new_opening_tag = f"{tag_without_closing} {' '.join(new_attributes)}>"
        
        return new_opening_tag + rest_of_button
    
    def _apply_suggestions_to_input(self, original_input: str, suggestions: Dict[str, str], in_string: bool = False) -> str:
        """Aplica las sugerencias de accesibilidad al input button"""
        # Generar nuevos atributos
        new_attributes = []
        
        if suggestions['aria_label']:
            if in_string:
                new_attributes.append(f'[aria-label="{suggestions["aria_label"]}"]')
            else:
                new_attributes.append(f'aria-label="{suggestions["aria_label"]}"')
        
        if suggestions['title']:
            if in_string:
                new_attributes.append(f'[title="{suggestions["title"]}"]')
            else:
                new_attributes.append(f'title="{suggestions["title"]}"')
        
        if not new_attributes:
            return original_input
        
        # Insertar los nuevos atributos
        tag_without_closing = original_input.rstrip('/>')
        if original_input.endswith('/>'):
            new_input_tag = f"{tag_without_closing} {' '.join(new_attributes)}/>"
        else:
            new_input_tag = f"{tag_without_closing} {' '.join(new_attributes)}>"
        
        return new_input_tag
    
    def _generate_button_accessibility_suggestions(self, button_type: str, button_content: str, css_class: str, button_id: str, onclick: str) -> Dict[str, str]:
        """Genera sugerencias de accesibilidad para botones"""
        clean_content = self.regex_patterns['html_tags'].sub('', button_content).strip()
        
        aria_label = ""
        title = ""
        
        # 1. Si tiene contenido de texto visible, usarlo
        if clean_content and len(clean_content.strip()) > 0:
            # Contenido descriptivo suficiente
            if len(clean_content) > 3:
                aria_label = clean_content
                title = clean_content
            else:
                # Contenido muy corto, intentar expandir
                aria_label, title = self._expand_short_button_text(clean_content, button_type, css_class)
        else:
            # 2. Sin contenido visible, analizar otros atributos
            aria_label, title = self._analyze_button_context(button_type, css_class, button_id, onclick)
        
        # 3. Procesar iconos en las clases
        icon_suggestion = self._detect_icon_in_classes(css_class)
        if icon_suggestion:
            if not aria_label or len(aria_label) < 5:
                aria_label = icon_suggestion['aria_label']
                title = icon_suggestion['title']
        
        # 4. Fallback si no se encontró nada
        if not aria_label:
            aria_label = f"Botón de {button_type}" if button_type != 'button' else "Botón de acción"
            title = aria_label
        
        return {
            'aria_label': aria_label,
            'title': title,
        }
    
    def _generate_input_button_accessibility_suggestions(self, input_type: str, input_value: str, css_class: str, input_id: str) -> Dict[str, str]:
        """Genera sugerencias de accesibilidad para input buttons"""
        aria_label = ""
        title = ""
        
        # 1. Usar el valor del input si existe
        if input_value and len(input_value.strip()) > 0:
            clean_value = input_value.strip()
            if len(clean_value) > 3:
                aria_label = clean_value
                title = clean_value
            else:
                aria_label, title = self._expand_short_button_text(clean_value, input_type, css_class)
        else:
            # 2. Basarse en el tipo de input
            if input_type == 'submit':
                aria_label = "Enviar formulario"
                title = "Enviar datos del formulario"
            elif input_type == 'reset':
                aria_label = "Restablecer formulario"
                title = "Limpiar todos los campos del formulario"
            else:
                # 3. Analizar contexto
                aria_label, title = self._analyze_button_context(input_type, css_class, input_id, '')
        
        # 4. Detectar iconos
        icon_suggestion = self._detect_icon_in_classes(css_class)
        if icon_suggestion and (not aria_label or len(aria_label) < 5):
            aria_label = icon_suggestion['aria_label']
            title = icon_suggestion['title']
        
        # 5. Fallback
        if not aria_label:
            type_labels = {
                'submit': 'Enviar',
                'reset': 'Restablecer',
                'button': 'Acción'
            }
            aria_label = f"Botón {type_labels.get(input_type, 'de acción')}"
            title = aria_label
        
        return {
            'aria_label': aria_label,
            'title': title,
        }
    
    def _expand_short_button_text(self, text: str, button_type: str, css_class: str) -> Tuple[str, str]:
        """Expande textos muy cortos de botones para hacerlos más descriptivos"""
        text_lower = text.lower()
        
        # Mapeo de textos cortos comunes
        expansions = {
            'ok': ('Confirmar acción', 'Confirmar y continuar'),
            'go': ('Continuar', 'Proceder con la acción'),
            'x': ('Cerrar', 'Cerrar ventana'),
            '+': ('Agregar elemento', 'Añadir nuevo elemento'),
            '-': ('Eliminar elemento', 'Quitar elemento'),
            '✓': ('Confirmar', 'Confirmar selección'),
            '✗': ('Cancelar', 'Cancelar acción'),
            '⋮': ('Más opciones', 'Mostrar más opciones'),
            '☰': ('Menú', 'Abrir menú de navegación'),
            '🔍': ('Buscar', 'Realizar búsqueda'),
            '❤': ('Me gusta', 'Marcar como favorito'),
            '⭐': ('Favorito', 'Agregar a favoritos'),
            'en': ('Enviar', 'Enviar información'),
            'si': ('Confirmar', 'Confirmar acción'),
            'no': ('Rechazar', 'Rechazar acción'),
        }
        
        if text_lower in expansions:
            return expansions[text_lower]
        
        # Expansiones basadas en tipo de botón
        if button_type == 'submit':
            return (f'Enviar {text}', f'Enviar {text}')
        elif 'search' in css_class.lower():
            return (f'Buscar {text}', f'Buscar {text}')
        elif 'save' in css_class.lower():
            return (f'Guardar {text}', f'Guardar {text}')
        
        # Expansión genérica
        return (f'Botón {text}', f'Ejecutar acción: {text}')
    
    def _analyze_button_context(self, button_type: str, css_class: str, button_id: str, onclick: str) -> Tuple[str, str]:
        """Analiza el contexto del botón para generar labels apropiados"""
        css_lower = css_class.lower()
        id_lower = button_id.lower()
        onclick_lower = onclick.lower()
        
        # Analizar clases CSS comunes
        for action, labels in self.common_button_actions.items():
            if (action in css_lower or action in id_lower or action in onclick_lower):
                return (labels['aria_label'], labels['title'])
        
        # Patrones específicos en clases
        class_patterns = {
            'modal': ('Abrir ventana modal', 'Mostrar ventana emergente'),
            'dropdown': ('Mostrar opciones', 'Desplegar menú de opciones'),
            'collapse': ('Expandir contenido', 'Mostrar/ocultar contenido'),
            'accordion': ('Alternar sección', 'Expandir o colapsar sección'),
            'tab': ('Cambiar pestaña', 'Activar esta pestaña'),
            'slide': ('Cambiar diapositiva', 'Ir a siguiente elemento'),
            'carousel': ('Navegar carrusel', 'Cambiar elemento del carrusel'),
            'tooltip': ('Mostrar información', 'Ver información adicional'),
            'popup': ('Abrir ventana emergente', 'Mostrar ventana popup'),
            'lightbox': ('Abrir galería', 'Ver imagen en pantalla completa'),
        }
        
        for pattern, labels in class_patterns.items():
            if pattern in css_lower:
                return labels
        
        # Analizar ID
        id_patterns = {
            'btn': 'Botón de acción',
            'submit': 'Enviar formulario',
            'cancel': 'Cancelar acción',
            'confirm': 'Confirmar acción',
            'login': 'Iniciar sesión',
            'logout': 'Cerrar sesión',
            'register': 'Registrarse',
            'download': 'Descargar archivo',
            'upload': 'Subir archivo',
        }
        
        for pattern, label in id_patterns.items():
            if pattern in id_lower:
                return (label, label)
        
        # Analizar onclick
        if onclick:
            if 'alert' in onclick_lower:
                return ('Mostrar alerta', 'Mostrar mensaje de alerta')
            elif 'confirm' in onclick_lower:
                return ('Confirmar acción', 'Confirmar operación')
            elif 'submit' in onclick_lower:
                return ('Enviar formulario', 'Enviar datos del formulario')
        
        # Basarse en el tipo de botón
        type_defaults = {
            'submit': ('Enviar formulario', 'Enviar datos del formulario'),
            'reset': ('Restablecer formulario', 'Limpiar campos del formulario'),
            'button': ('Ejecutar acción', 'Realizar acción')
        }
        
        return type_defaults.get(button_type, ('Botón de acción', 'Ejecutar acción'))
    
    def _detect_icon_in_classes(self, css_class: str) -> Dict[str, str]:
        """Detecta iconos en las clases CSS y sugiere labels apropiados"""
        if not css_class:
            return None
        
        css_lower = css_class.lower()
        
        # Buscar patrones de iconos específicos
        for icon_class, suggestion in self.icon_patterns.items():
            if icon_class in css_lower:
                return suggestion
        
        # Patrones genéricos de iconos
        generic_icon_patterns = {
            'icon-search': {'aria_label': 'Buscar', 'title': 'Realizar búsqueda'},
            'icon-close': {'aria_label': 'Cerrar', 'title': 'Cerrar ventana'},
            'icon-menu': {'aria_label': 'Menú', 'title': 'Abrir menú'},
            'icon-home': {'aria_label': 'Inicio', 'title': 'Ir a página de inicio'},
            'icon-user': {'aria_label': 'Usuario', 'title': 'Perfil de usuario'},
            'icon-settings': {'aria_label': 'Configuración', 'title': 'Abrir configuración'},
            'icon-help': {'aria_label': 'Ayuda', 'title': 'Obtener ayuda'},
            'icon-info': {'aria_label': 'Información', 'title': 'Ver más información'},
            'icon-warning': {'aria_label': 'Advertencia', 'title': 'Ver advertencia'},
            'icon-error': {'aria_label': 'Error', 'title': 'Ver error'},
            'icon-success': {'aria_label': 'Éxito', 'title': 'Operación exitosa'},
        }
        
        for pattern, suggestion in generic_icon_patterns.items():
            if pattern in css_lower:
                return suggestion
        
        # Detectar clases de Bootstrap Icons, Heroicons, etc.
        if any(prefix in css_lower for prefix in ['bi-', 'hero-', 'lucide-', 'tabler-']):
            # Extraer el nombre del icono
            parts = css_class.split()
            for part in parts:
                part_lower = part.lower()
                if any(part_lower.startswith(prefix) for prefix in ['bi-', 'hero-', 'lucide-', 'tabler-']):
                    icon_name = part_lower.split('-', 1)[1] if '-' in part_lower else 'acción'
                    return {
                        'aria_label': f'Botón {icon_name.replace("-", " ")}',
                        'title': f'Ejecutar {icon_name.replace("-", " ")}'
                    }
        
        return None
    
    def _generate_summary(self) -> Dict:
        """Genera un resumen de las correcciones realizadas"""
        summary = {
            'total_fixes': self.total_fixes,
            'files_modified': len(self.processed_files),
            'processed_files': self.processed_files
        }
        
        self._print_summary(summary)
        return summary
    
    def _print_summary(self, summary: Dict):
        """Imprime el resumen de correcciones"""
        print("\n" + "=" * 70)
        print("🎉 CORRECCIÓN AUTOMÁTICA DE BOTONES COMPLETADA")
        print("=" * 70)
        
        if summary['total_fixes'] == 0:
            print("✅ ¡Perfecto! No se encontraron botones que necesitaran corrección.")
            print("   Todos los botones ya tienen nombres accesibles adecuados.")
        else:
            print(f"🔧 Total de botones corregidos: {summary['total_fixes']}")
            print(f"📄 Archivos modificados: {summary['files_modified']}")
            print()
            print("📋 DETALLE DE ARCHIVOS MODIFICADOS:")
            print("-" * 50)
            
            for file_info in summary['processed_files']:
                print(f"   ✅ {file_info['file']}: {file_info['fixes']} botón(es) corregido(s)")
            
            print()
            print("🎯 QUÉ SE AGREGÓ A LOS BOTONES:")
            print("   • aria-label: Nombre accesible para lectores de pantalla")
            print("   • title: Información adicional al pasar el mouse")
            print()
            print("🔍 TIPOS DE BOTONES PROCESADOS:")
            print("   • <button>: Botones estándar")
            print("   • <input type='button'>: Botones de entrada")
            print("   • <input type='submit'>: Botones de envío")
            print("   • <input type='reset'>: Botones de reseteo")
            print()
            print("🛡️ PROTECCIONES APLICADAS:")
            print("   • Modifica botones en strings JS/TS usando corchetes especiales [attr='...']")
            print("   • No modifica contenido en comentarios")
            print("   • Preserva scripts y atributos especiales")
            print("   • Ignora estructuras de datos complejas")
            print()
            print("🎨 DETECCIÓN INTELIGENTE:")
            print("   • Reconoce iconos de FontAwesome, Bootstrap Icons, etc.")
            print("   • Analiza clases CSS para determinar la función")
            print("   • Procesa contenido de texto visible")
            print("   • Identifica patrones comunes (submit, cancel, etc.)")
            print()
            print("💡 BENEFICIOS OBTENIDOS:")
            print("   • Botones accesibles para lectores de pantalla")
            print("   • Cumplimiento con estándares WCAG")
            print("   • Mejor experiencia para usuarios con discapacidades")
            print("   • Mejores puntuaciones en auditorías de accesibilidad")
        
        if self.create_backup:
            print(f"\n💾 Backup disponible para rollback si es necesario")
        
        print("\n🚀 ¡Proyecto listo! Tus botones ahora tienen nombres accesibles.")

def main():
    print("🔧 CORRECTOR AUTOMÁTICO DE BOTONES SIN NOMBRES ACCESIBLES")
    print("=" * 60)
    print("Este script MODIFICARÁ directamente tus archivos para agregar")
    print("nombres accesibles (aria-label y title) a botones que los necesiten.")
    print()
    print("🎯 BOTONES QUE SE PROCESARÁN:")
    print("   • <button>: Botones estándar")
    print("   • <input type='button'>: Botones de entrada")
    print("   • <input type='submit'>: Botones de envío")
    print("   • <input type='reset'>: Botones de reseteo")
    print()
    
    # Configuración
    project_path = input("📂 Ruta de tu proyecto (Enter para usar '../'): ").strip()
    if not project_path:
        project_path = "../"
    
    if not os.path.exists(project_path):
        print(f"❌ Error: La ruta '{project_path}' no existe.")
        return
    
    # Confirmar antes de proceder
    backup_option = input("💾 ¿Crear backup antes de modificar? (s/N): ").strip().lower()
    create_backup = backup_option in ['s', 'si', 'sí', 'y', 'yes']
    
    print(f"\n⚠️  IMPORTANTE: Se van a modificar archivos en '{project_path}'")
    print("Los botones sin nombres accesibles recibirán atributos aria-label y title.")
    confirm = input("¿Continuar? (s/N): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada.")
        return
    
    # Ejecutar correcciones
    print("\n🚀 Iniciando corrección automática de botones...")
    fixer = ButtonAutoFixer(project_path, backup=create_backup)
    results = fixer.fix_project()

if __name__ == "__main__":
    main()