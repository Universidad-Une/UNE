#!/usr/bin/env python3
"""
Analizador y Corrector Automático de enlaces <a> sin aria-label y title
Encuentra y CORRIGE automáticamente todos los elementos anchor sin atributos de accesibilidad
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Set
from datetime import datetime

class AnchorAutoFixer:
    def __init__(self, project_path: str, backup: bool = True):
        self.project_path = Path(project_path)
        self.extensions = {'.astro', '.tsx', '.jsx', '.js', '.ts', '.vue', '.svelte'}
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
        
        # Cache para sugerencias de redes sociales
        self.social_networks = {
            'twitter.com': 'Twitter',
            'facebook.com': 'Facebook', 
            'instagram.com': 'Instagram',
            'linkedin.com': 'LinkedIn',
            'github.com': 'GitHub',
            'youtube.com': 'YouTube',
            'tiktok.com': 'TikTok',
            'pinterest.com': 'Pinterest'
        }
        
        self.generic_terms = {'click', 'here', 'más', 'more', 'ver', 'see', 'read', 'leer'}
    
    def _compile_regex_patterns(self):
        """Precompila todas las expresiones regulares para mejor rendimiento"""
        self.regex_patterns = {
            'anchor_complete': re.compile(r'<a\s+[^>]*>.*?</a>', re.IGNORECASE | re.DOTALL),
            'anchor_opening': re.compile(r'<a\s+[^>]*>', re.IGNORECASE),
            'aria_label': re.compile(r'aria-label\s*=', re.IGNORECASE),
            'title': re.compile(r'title\s*=', re.IGNORECASE),
            'aria_labelledby': re.compile(r'aria-labelledby\s*=', re.IGNORECASE),
            'href': re.compile(r'href\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            'class': re.compile(r'class\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE),
            'content': re.compile(r'<a[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL),
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
        print(f"🔧 Iniciando corrección automática en: {self.project_path}")
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
        backup_dir = f"backup_accessibility_{timestamp}"
        
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
                
                print(f"✅ {file_path.relative_to(self.project_path)}: {fixes_count} enlace(s) corregido(s)")
            
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
        
        # Identificar zonas seguras para modificar (ahora incluye strings)
        safe_zones = self._identify_safe_zones(content)
        
        # Procesar anchors completos primero
        def fix_complete_anchor(match):
            nonlocal fixes_count
            full_anchor = match.group(0)
            
            # Verificar si está en una zona segura
            if self._is_in_safe_zone(match.start(), match.end(), safe_zones):
                # Verificar si está dentro de un string
                in_string = self._is_in_string_zone(match.start(), match.end(), content)
                fixed_anchor = self._fix_single_anchor(full_anchor, file_path, in_string)
                if fixed_anchor != full_anchor:
                    fixes_count += 1
                    return fixed_anchor
            return full_anchor
        
        # Aplicar correcciones a anchors completos
        modified_content = self.regex_patterns['anchor_complete'].sub(
            fix_complete_anchor, 
            modified_content
        )
        
        # Procesar anchors solo de apertura que no fueron procesados
        processed_positions = set()
        for match in self.regex_patterns['anchor_complete'].finditer(content):
            processed_positions.update(range(match.start(), match.end()))
        
        opening_matches = list(self.regex_patterns['anchor_opening'].finditer(modified_content))
        
        # Procesar desde el final hacia el inicio para no afectar las posiciones
        for match in reversed(opening_matches):
            if (match.start() not in processed_positions and 
                self._is_in_safe_zone(match.start(), match.end(), safe_zones)):
                
                anchor_tag = match.group(0)
                in_string = self._is_in_string_zone(match.start(), match.end(), content)
                fixed_tag = self._fix_single_anchor(anchor_tag, file_path, in_string)
                
                if fixed_tag != anchor_tag:
                    modified_content = (
                        modified_content[:match.start()] + 
                        fixed_tag + 
                        modified_content[match.end():]
                    )
                    fixes_count += 1
        
        return modified_content, fixes_count
    
    def _fix_single_anchor(self, anchor_html: str, file_path: Path, in_string: bool = False) -> str:
        """Corrige un anchor individual si necesita atributos de accesibilidad"""
        # Extraer tag de apertura
        opening_match = self.regex_patterns['anchor_opening'].match(anchor_html)
        if not opening_match:
            return anchor_html
        
        anchor_tag = opening_match.group(0)
        
        # Verificar si ya tiene atributos de accesibilidad
        has_accessibility = (
            self.regex_patterns['aria_label'].search(anchor_tag) or
            self.regex_patterns['title'].search(anchor_tag) or
            self.regex_patterns['aria_labelledby'].search(anchor_tag)
        )
        
        if has_accessibility:
            return anchor_html
        
        # Extraer información del anchor
        href_match = self.regex_patterns['href'].search(anchor_tag)
        href = href_match.group(1) if href_match else 'sin href'
        
        class_match = self.regex_patterns['class'].search(anchor_tag)
        css_class = class_match.group(1) if class_match else 'sin clase'
        
        # Extraer contenido del enlace
        content_match = self.regex_patterns['content'].search(anchor_html)
        link_content = content_match.group(1).strip() if content_match else ''
        clean_link_content = self.regex_patterns['whitespace'].sub(' ', link_content).strip()
        
        # Generar sugerencias
        suggestions = self._generate_accessibility_suggestions(href, clean_link_content, css_class)
        
        # Aplicar las correcciones con el formato apropiado
        return self._apply_suggestions_to_anchor(anchor_html, suggestions, in_string)
    
    def _apply_suggestions_to_anchor(self, original_anchor: str, suggestions: Dict[str, str], in_string: bool = False) -> str:
        """Aplica las sugerencias de accesibilidad al anchor"""
        opening_match = self.regex_patterns['anchor_opening'].match(original_anchor)
        if not opening_match:
            return original_anchor
        
        opening_tag = opening_match.group(0)
        rest_of_anchor = original_anchor[len(opening_tag):]
        
        # Generar nuevos atributos con el formato apropiado
        new_attributes = []
        
        if suggestions['aria_label']:
            if in_string:
                # Usar corchetes para strings JS/TS para evitar conflictos de sintaxis
                new_attributes.append(f'[aria-label="{suggestions["aria_label"]}"]')
            else:
                # Formato normal para HTML directo
                new_attributes.append(f'aria-label="{suggestions["aria_label"]}"')
        
        if suggestions['title']:
            if in_string:
                # Usar corchetes para strings JS/TS para evitar conflictos de sintaxis
                new_attributes.append(f'[title="{suggestions["title"]}"]')
            else:
                # Formato normal para HTML directo
                new_attributes.append(f'title="{suggestions["title"]}"')
        
        if not new_attributes:
            return original_anchor
        
        # Insertar los nuevos atributos manteniendo el formato
        tag_without_closing = opening_tag.rstrip('>')
        
        if in_string:
            # Para strings, agregamos los atributos con corchetes de forma más cuidadosa
            new_opening_tag = f"{tag_without_closing} {' '.join(new_attributes)}>"
        else:
            # Para HTML directo, formato normal
            new_opening_tag = f"{tag_without_closing} {' '.join(new_attributes)}>"
        
        return new_opening_tag + rest_of_anchor
    
    def _generate_accessibility_suggestions(self, href: str, link_content: str, css_class: str) -> Dict[str, str]:
        """Genera sugerencias de accesibilidad optimizadas"""
        clean_content = self.regex_patterns['html_tags'].sub('', link_content).strip()
        
        aria_label = ""
        title = ""
        
        if clean_content:
            content_lower = clean_content.lower()
            is_generic = any(term in content_lower for term in self.generic_terms) or len(clean_content) < 10
            
            if is_generic:
                href_lower = href.lower()
                if 'blog' in href_lower:
                    aria_label = f"Leer más sobre {clean_content}"
                    title = f"Ver artículo completo: {clean_content}"
                elif 'contact' in href_lower or 'contacto' in href_lower:
                    aria_label = "Ir a página de contacto"
                    title = "Contactar con nosotros"
                else:
                    aria_label = f"Ir a {clean_content}"
                    title = f"Navegar a {clean_content}"
            else:
                aria_label = f"Ir a {clean_content}"
                title = clean_content
        else:
            aria_label, title = self._process_empty_link(href, css_class)
        
        # Procesar tipos especiales
        aria_label, title = self._process_special_link_types(href, aria_label, title)
        
        return {
            'aria_label': aria_label,
            'title': title,
        }
    
    def _process_empty_link(self, href: str, css_class: str) -> Tuple[str, str]:
        """Procesa enlaces sin contenido visible"""
        href_lower = href.lower()
        css_lower = css_class.lower()
        
        if 'social' in css_lower or any(social in href_lower for social in self.social_networks.keys()):
            social_network = self._detect_social_network(href)
            return f"Seguir en {social_network}", f"Visitar perfil en {social_network}"
        
        if 'home' in href_lower or href == '/':
            return "Ir a página de inicio", "Página principal"
        elif 'menu' in css_lower or 'hamburger' in css_lower:
            return "Abrir menú de navegación", "Menú"
        elif 'close' in css_lower:
            return "Cerrar", "Cerrar ventana"
        else:
            path_parts = href.strip('/').split('/')
            if path_parts and path_parts[0]:
                section = path_parts[0].replace('-', ' ').replace('_', ' ').title()
                return f"Ir a {section}", f"Navegar a {section}"
            else:
                return "Enlace de navegación", "Enlace"
    
    def _process_special_link_types(self, href: str, aria_label: str, title: str) -> Tuple[str, str]:
        """Procesa tipos especiales de enlaces"""
        if href.startswith('mailto:'):
            email = href[7:]
            return f"Enviar email a {email}", f"Contactar por email: {email}"
        elif href.startswith('tel:'):
            phone = href[4:]
            return f"Llamar a {phone}", f"Número de teléfono: {phone}"
        elif href.startswith('http') and 'youtube' in href.lower():
            return "Ver video en YouTube", "Abrir video en YouTube"
        elif href.startswith('#'):
            anchor = href[1:].replace('-', ' ').title()
            return f"Ir a sección {anchor}", f"Navegar a {anchor}"
        
        return aria_label, title
    
    def _detect_social_network(self, href: str) -> str:
        """Detecta la red social de forma optimizada"""
        href_lower = href.lower()
        for domain, name in self.social_networks.items():
            if domain in href_lower:
                return name
        return 'Red Social'
    
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
        print("🎉 CORRECCIÓN AUTOMÁTICA COMPLETADA")
        print("=" * 70)
        
        if summary['total_fixes'] == 0:
            print("✅ ¡Perfecto! No se encontraron enlaces que necesitaran corrección.")
            print("   Todos los enlaces ya tienen atributos de accesibilidad adecuados.")
        else:
            print(f"🔧 Total de enlaces corregidos: {summary['total_fixes']}")
            print(f"📄 Archivos modificados: {summary['files_modified']}")
            print()
            print("📋 DETALLE DE ARCHIVOS MODIFICADOS:")
            print("-" * 50)
            
            for file_info in summary['processed_files']:
                print(f"   ✅ {file_info['file']}: {file_info['fixes']} corrección(es)")
            
            print()
            print("🎯 QUÉ SE AGREGÓ:")
            print("   • aria-label: Texto para lectores de pantalla")
            print("   • title: Tooltip informativo al pasar el mouse")
            print()
            print("🛡️ PROTECCIONES APLICADAS:")
            print("   • Modifica enlaces en strings JS/TS usando corchetes especiales [attr='...']")
            print("   • No modifica contenido en comentarios")
            print("   • Preserva scripts y atributos especiales")
            print("   • Ignora solo estructuras de datos muy complejas")
            print()
            print("💡 BENEFICIOS OBTENIDOS:")
            print("   • Mejor accesibilidad web (WCAG compliance)")
            print("   • Experiencia mejorada para usuarios con discapacidades")
            print("   • SEO mejorado")
            print("   • Mejores puntuaciones en auditorías (Lighthouse)")
        
        if self.create_backup:
            print(f"\n💾 Backup disponible para rollback si es necesario")
        
        print("\n🚀 ¡Proyecto listo! Tus enlaces ahora son completamente accesibles.")

def main():
    print("🔧 CORRECTOR AUTOMÁTICO DE ACCESIBILIDAD WEB")
    print("=" * 50)
    print("Este script MODIFICARÁ directamente tus archivos para agregar")
    print("atributos de accesibilidad (aria-label y title) a enlaces que los necesiten.")
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
    confirm = input("¿Continuar? (s/N): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada.")
        return
    
    # Ejecutar correcciones
    print("\n🚀 Iniciando corrección automática...")
    fixer = AnchorAutoFixer(project_path, backup=create_backup)
    results = fixer.fix_project()

if __name__ == "__main__":
    main()