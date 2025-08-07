#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas End-to-End simplificadas para proyecto Astro usando Selenium
"""

import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class AstroE2ETester:
    def __init__(self, base_url="http://localhost:4321", project_root="./"):
        self.base_url = base_url
        self.project_root = Path(project_root).resolve()
        self.pages_dir = self.project_root / "src" / "pages"
        self.driver = None
        self.results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pages_tested': 0,
            'links_tested': 0,
            'links_working': 0,
            'links_broken': 0,
            'errors': [],
            'page_results': {}
        }
    
    def discover_pages(self):
        """Descubre páginas recursivamente en src/pages"""
        print(f"🔍 Buscando páginas en: {self.pages_dir}")
        
        if not self.pages_dir.exists():
            print(f"❌ No existe: {self.pages_dir}")
            return []
        
        pages = []
        extensions = ['.astro', '.md', '.mdx']
        
        for ext in extensions:
            for file_path in self.pages_dir.rglob(f"*{ext}"):
                if self._is_valid_page(file_path):
                    relative_path = file_path.relative_to(self.pages_dir)
                    web_path = self._file_to_url(relative_path)
                    if web_path and web_path not in pages:
                        pages.append(web_path)
        
        pages.sort()
        print(f"✅ Encontradas {len(pages)} páginas:")
        for page in pages:
            print(f"   📄 {page}")
        
        return pages
    
    def _is_valid_page(self, file_path):
        """Verifica si un archivo es una página válida"""
        name = file_path.name
        path_str = str(file_path)
        
        # Ignorar archivos privados, componentes, layouts
        ignore_patterns = [
            name.startswith('_'),
            name.startswith('.'),
            '/components/' in path_str,
            '/layouts/' in path_str,
        ]
        
        return not any(ignore_patterns)
    
    def _file_to_url(self, file_path):
        """Convierte ruta de archivo a URL web"""
        path_str = str(file_path).replace('\\', '/')
        
        # Remover extensiones
        for ext in ['.astro', '.md', '.mdx']:
            if path_str.endswith(ext):
                path_str = path_str[:-len(ext)]
                break
        
        # Manejar index
        if path_str.endswith('/index') or path_str == 'index':
            path_str = path_str.replace('/index', '').replace('index', '')
        
        # Agregar slash inicial
        if path_str and not path_str.startswith('/'):
            path_str = '/' + path_str
        
        return path_str or '/'
    
    def setup_driver(self):
        """Configura Chrome WebDriver"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            
            print("✅ Chrome driver configurado")
            return True
        except Exception as e:
            print(f"❌ Error configurando driver: {e}")
            return False
    
    def test_page(self, url):
        """Prueba carga de una página"""
        try:
            print(f"   🌐 Cargando: {url}")
            start_time = time.time()
            self.driver.get(url)
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            load_time = round(time.time() - start_time, 2)
            title = self.driver.title
            
            return {
                'success': True,
                'load_time': load_time,
                'title': title,
                'url': self.driver.current_url
            }
        except TimeoutException:
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_links(self):
        """Obtiene enlaces internos de la página"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            links = []
            
            for element in elements:
                href = element.get_attribute('href')
                text = element.text.strip() or '[Sin texto]'
                
                # Solo enlaces internos
                if (href and 
                    (href.startswith('/') or self.base_url in href) and
                    not href.startswith('#') and 
                    not href.startswith('mailto:')):
                    links.append({'url': href, 'text': text})
            
            return links
        except Exception as e:
            print(f"   ⚠️ Error obteniendo enlaces: {e}")
            return []
    
    def test_link(self, link):
        """Prueba un enlace específico"""
        url = link['url']
        try:
            if url.startswith('/'):
                full_url = urljoin(self.base_url, url)
            else:
                full_url = url
            
            original_url = self.driver.current_url
            self.driver.get(full_url)
            
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            result = {'status': 'success', 'final_url': self.driver.current_url}
            
            # Volver a página original
            self.driver.get(original_url)
            return result
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def run_tests(self, max_pages=10, max_links=5):
        """Ejecuta las pruebas"""
        if not self.setup_driver():
            return False
        
        try:
            print(f"🚀 Probando: {self.base_url}")
            
            pages = self.discover_pages()
            if not pages:
                print("❌ No hay páginas para probar")
                return False
            
            # Limitar páginas en evaluación rápida
            pages_to_test = pages[:max_pages]
            if len(pages) > max_pages:
                print(f"⚡ Probando {max_pages} de {len(pages)} páginas")
            
            for i, page_path in enumerate(pages_to_test, 1):
                page_url = urljoin(self.base_url, page_path)
                print(f"\n📄 [{i}/{len(pages_to_test)}] {page_path}")
                
                # Probar página
                result = self.test_page(page_url)
                
                if result['success']:
                    print(f"   ✅ OK ({result['load_time']}s) - {result['title']}")
                    
                    # Probar enlaces
                    links = self.get_links()[:max_links]
                    if links:
                        print(f"   🔗 Probando {len(links)} enlaces:")
                        
                        link_results = []
                        for link in links:
                            link_result = self.test_link(link)
                            link_results.append({'link': link, 'result': link_result})
                            
                            if link_result['status'] == 'success':
                                self.results['links_working'] += 1
                                print(f"     ✅ {link['text'][:40]}")
                            else:
                                self.results['links_broken'] += 1
                                print(f"     ❌ {link['text'][:40]} - {link_result.get('message', 'Error')}")
                            
                            self.results['links_tested'] += 1
                        
                        self.results['page_results'][page_path] = {
                            'load_result': result,
                            'link_results': link_results
                        }
                    else:
                        print("   📝 Sin enlaces internos")
                        self.results['page_results'][page_path] = {
                            'load_result': result,
                            'link_results': []
                        }
                else:
                    print(f"   ❌ Error: {result.get('error', 'Desconocido')}")
                    self.results['errors'].append(f"{page_path}: {result.get('error')}")
                
                self.results['pages_tested'] += 1
                time.sleep(1)  # Pausa entre páginas
            
            return True
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🏁 Driver cerrado")
    
    def generate_report(self, filename="test_report2.md"):
        """Genera reporte en Markdown"""
        success_rate = (self.results['links_working'] / max(self.results['links_tested'], 1)) * 100
        
        report = f"""# 🧪 Reporte E2E - Astro

**Fecha:** {self.results['timestamp']}  
**URL:** {self.base_url}

## 📊 Resumen

- **Páginas probadas:** {self.results['pages_tested']}
- **Enlaces probados:** {self.results['links_tested']}
- **Enlaces OK:** {self.results['links_working']} ✅
- **Enlaces rotos:** {self.results['links_broken']} ❌
- **Éxito:** {success_rate:.1f}%

## 📄 Resultados

"""
        
        for page, data in self.results['page_results'].items():
            load_result = data['load_result']
            report += f"### {page}\n\n"
            
            if load_result['success']:
                report += f"- ✅ Cargado en {load_result['load_time']}s\n"
                report += f"- 📋 Título: {load_result['title']}\n\n"
                
                if data['link_results']:
                    report += "**Enlaces:**\n"
                    for item in data['link_results']:
                        link = item['link']
                        result = item['result']
                        icon = "✅" if result['status'] == 'success' else "❌"
                        report += f"- {icon} {link['text']} → `{link['url']}`\n"
                    report += "\n"
            else:
                report += f"- ❌ Error: {load_result.get('error')}\n\n"
        
        if self.results['errors']:
            report += "## ⚠️ Errores\n\n"
            for error in self.results['errors']:
                report += f"- {error}\n"
        
        report += "\n---\n*Generado automáticamente*"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Reporte: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
            return None
    
    def show_pages_only(self):
        """Solo muestra las páginas encontradas"""
        pages = self.discover_pages()
        if pages:
            print(f"\n🌐 URLs que se probarían:")
            for i, page in enumerate(pages, 1):
                print(f"   {i:2d}. {urljoin(self.base_url, page)}")
        return pages


def main():
    """Función principal"""
    print("=" * 60)
    print("🧪 ASTRO E2E TESTER")
    print("=" * 60)
    
    # Configuración
    BASE_URL = "http://localhost:4321"
    PROJECT_ROOT = "../"
    
    tester = AstroE2ETester(BASE_URL, PROJECT_ROOT)
    
    # Menú simple
    print("\n🔧 Opciones:")
    print("1. 👀 Ver páginas encontradas")
    print("2. ⚡ Ejecutar pruebas rápidas")
    print("3. 🔍 Ejecutar pruebas completas")
    
    try:
        choice = input("\nSelecciona (1-3) [1]: ").strip() or "1"
        
        if choice == "1":
            print("\n" + "="*40)
            tester.show_pages_only()
            
        elif choice == "2":
            print("\n" + "="*40)
            print("⚡ EJECUTANDO PRUEBAS RÁPIDAS...")
            print("="*40)
            
            if tester.run_tests(max_pages=5, max_links=3):
                print("\n✅ PRUEBAS COMPLETADAS")
                tester.generate_report("quick_report.md")
            
        elif choice == "3":
            print("\n" + "="*40)
            print("🔍 EJECUTANDO PRUEBAS COMPLETAS...")
            print("="*40)
            
            if tester.run_tests(max_pages=999, max_links=10):
                print("\n✅ PRUEBAS COMPLETADAS")
                tester.generate_report("full_report.md")
        
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()