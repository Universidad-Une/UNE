#!/usr/bin/env python3
"""
Script de auditoría completa para proyecto Astro usando Selenium
Ejecuta desde el directorio utils del proyecto
VERSIÓN COMPATIBLE CON SELENIUM 4+
"""

import time
import json
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Intentar importar los servicios modernos, con fallback a versiones anteriores
try:
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    SELENIUM_4 = True
except ImportError:
    SELENIUM_4 = False

class AstroAuditor:
    def __init__(self, base_url="http://localhost:4321"):
        """
        Inicializa el auditor para proyecto Astro
        
        Args:
            base_url (str): URL base del proyecto Astro (por defecto puerto 4321)
        """
        self.base_url = base_url
        self.driver = None
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "pages_tested": [],
            "performance": {},
            "accessibility": {},
            "seo": {},
            "errors": [],
            "warnings": []
        }
        
    def find_chrome_executable(self):
        """Busca el ejecutable de Chrome en ubicaciones comunes de Windows"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.environ.get('USERNAME', '')),
            r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def find_edge_executable(self):
        """Busca el ejecutable de Edge en ubicaciones comunes de Windows"""
        possible_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
        
    def setup_driver(self, headless=False, browser_preference="chrome"):
        """Configura el driver con detección automática de navegador"""
        print(f"🔍 Configurando driver del navegador (Selenium {4 if SELENIUM_4 else 3})...")
        
        # Intentar Chrome primero (si es la preferencia)
        if browser_preference == "chrome":
            chrome_path = self.find_chrome_executable()
            if chrome_path:
                try:
                    return self._setup_chrome_driver(headless, chrome_path)
                except Exception as e:
                    print(f"⚠️ Error configurando Chrome: {e}")
                    print("🔄 Intentando con Edge...")
        
        # Intentar Edge como alternativa
        edge_path = self.find_edge_executable()
        if edge_path:
            try:
                return self._setup_edge_driver(headless, edge_path)
            except Exception as e:
                print(f"⚠️ Error configurando Edge: {e}")
        
        # Si Chrome era la segunda opción, intentarlo ahora
        if browser_preference != "chrome":
            chrome_path = self.find_chrome_executable()
            if chrome_path:
                try:
                    return self._setup_chrome_driver(headless, chrome_path)
                except Exception as e:
                    print(f"⚠️ Error configurando Chrome: {e}")
        
        # Si todo falla, mostrar error detallado
        raise Exception("❌ No se pudo configurar ningún navegador. Verifica la instalación de Selenium y los drivers.")
    
    def _setup_chrome_driver(self, headless, chrome_path):
        """Configura específicamente Chrome"""
        print(f"🌐 Configurando Chrome desde: {chrome_path}")
        
        chrome_options = ChromeOptions()
        chrome_options.binary_location = chrome_path
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Opciones para mejor rendimiento y compatibilidad
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        
        try:
            if SELENIUM_4:
                # Selenium 4+ con Service
                from webdriver_manager.chrome import ChromeDriverManager
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Selenium 3 sin Service
                from webdriver_manager.chrome import ChromeDriverManager
                chrome_driver_path = ChromeDriverManager().install()
                self.driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
            
            self.driver.implicitly_wait(10)
            print("✅ Chrome configurado correctamente")
            return True
            
        except Exception as e:
            print(f"Error detallado con Chrome: {str(e)}")
            raise e
    
    def _setup_edge_driver(self, headless, edge_path):
        """Configura específicamente Edge"""
        print(f"🌐 Configurando Edge desde: {edge_path}")
        
        edge_options = EdgeOptions()
        edge_options.binary_location = edge_path
        
        if headless:
            edge_options.add_argument("--headless")
        
        # Opciones para mejor rendimiento y compatibilidad
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument("--disable-plugins")
        edge_options.add_argument("--disable-web-security")
        edge_options.add_argument("--allow-running-insecure-content")
        edge_options.add_argument("--ignore-certificate-errors")
        edge_options.add_argument("--disable-logging")
        edge_options.add_argument("--log-level=3")
        
        try:
            if SELENIUM_4:
                # Selenium 4+ con Service
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=edge_options)
            else:
                # Selenium 3 sin Service
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                edge_driver_path = EdgeChromiumDriverManager().install()
                self.driver = webdriver.Edge(executable_path=edge_driver_path, options=edge_options)
            
            self.driver.implicitly_wait(10)
            print("✅ Edge configurado correctamente")
            return True
            
        except Exception as e:
            print(f"Error detallado con Edge: {str(e)}")
            raise e
        
    def check_server_running(self):
        """Verifica que el servidor Astro esté ejecutándose"""
        try:
            self.driver.get(self.base_url)
            return True
        except Exception as e:
            self.audit_results["errors"].append({
                "type": "server_connection",
                "message": f"No se puede conectar a {self.base_url}: {str(e)}",
                "suggestion": "Ejecuta 'npm run dev' para iniciar el servidor Astro"
            })
            return False
    
    def audit_page_performance(self, url):
        """Audita el rendimiento de una página específica"""
        try:
            start_time = time.time()
            self.driver.get(url)
            
            # Esperar a que la página cargue completamente
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            load_time = time.time() - start_time
            
            # Obtener métricas de rendimiento del navegador
            performance = self.driver.execute_script("""
                return {
                    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    firstPaint: performance.getEntriesByType('paint')[0] ? performance.getEntriesByType('paint')[0].startTime : null,
                    resources: performance.getEntriesByType('resource').length
                }
            """)
            
            return {
                "url": url,
                "selenium_load_time": round(load_time, 2),
                "browser_metrics": performance,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    def audit_seo_basics(self, url):
        """Audita elementos básicos de SEO"""
        seo_results = {"url": url}
        
        try:
            self.driver.get(url)
            
            # Título de la página
            title = self.driver.title
            seo_results["title"] = {
                "content": title,
                "length": len(title),
                "status": "good" if 10 <= len(title) <= 60 else "warning"
            }
            
            # Meta descripción
            try:
                meta_desc = self.driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
                desc_content = meta_desc.get_attribute("content")
                seo_results["meta_description"] = {
                    "content": desc_content,
                    "length": len(desc_content),
                    "status": "good" if 120 <= len(desc_content) <= 160 else "warning"
                }
            except:
                seo_results["meta_description"] = {"status": "missing"}
            
            # Encabezados H1
            h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
            seo_results["h1_tags"] = {
                "count": len(h1_elements),
                "texts": [h1.text for h1 in h1_elements],
                "status": "good" if len(h1_elements) == 1 else "warning"
            }
            
            # Imágenes sin alt
            images = self.driver.find_elements(By.TAG_NAME, "img")
            images_without_alt = [img.get_attribute("src") for img in images if not img.get_attribute("alt")]
            seo_results["images"] = {
                "total": len(images),
                "without_alt": len(images_without_alt),
                "missing_alt_srcs": images_without_alt[:5]  # Primeras 5
            }
            
        except Exception as e:
            seo_results["error"] = str(e)
            
        return seo_results
    
    def check_astro_specific_features(self, url):
        """Verifica características específicas de Astro"""
        astro_results = {"url": url}
        
        try:
            self.driver.get(url)
            
            # Verificar si hay componentes Astro hidratados
            astro_components = self.driver.execute_script("""
                return Array.from(document.querySelectorAll('[data-astro-cid]')).length;
            """)
            astro_results["astro_components"] = astro_components
            
            # Verificar scripts de hidratación
            astro_scripts = self.driver.execute_script("""
                return Array.from(document.querySelectorAll('script[type="module"]')).length;
            """)
            astro_results["hydration_scripts"] = astro_scripts
            
            # Verificar enlaces internos
            internal_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/'], a[href^='./'], a[href^='../']")
            astro_results["internal_links"] = len(internal_links)
            
        except Exception as e:
            astro_results["error"] = str(e)
            
        return astro_results
    
    def discover_pages(self):
        """Descubre páginas disponibles en el proyecto Astro"""
        pages = ["/"]  # Siempre incluir la página principal
        
        try:
            # Buscar en el directorio src/pages si existe
            src_pages_path = "../src/pages"
            if os.path.exists(src_pages_path):
                for root, dirs, files in os.walk(src_pages_path):
                    for file in files:
                        if file.endswith(('.astro', '.md', '.mdx')):
                            # Convertir ruta de archivo a ruta web
                            relative_path = os.path.relpath(os.path.join(root, file), src_pages_path)
                            web_path = "/" + relative_path.replace("\\", "/").replace("index.astro", "").replace(".astro", "").replace(".md", "").replace(".mdx", "")
                            if web_path != "/" and web_path not in pages:
                                pages.append(web_path.rstrip("/"))
            
            # También buscar enlaces en la página principal
            try:
                self.driver.get(self.base_url)
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/'], a[href^='./']")
                for link in links:
                    href = link.get_attribute("href")
                    if href and href.startswith(self.base_url):
                        path = href.replace(self.base_url, "")
                        if path and path not in pages:
                            pages.append(path)
            except:
                pass
                
        except Exception as e:
            self.audit_results["warnings"].append(f"Error discovering pages: {str(e)}")
        
        return pages
    
    def run_complete_audit(self, headless=False, browser_preference="chrome"):
        """Ejecuta una auditoría completa del proyecto Astro"""
        print("🚀 Iniciando auditoría completa del proyecto Astro...")
        
        # Configurar driver
        try:
            self.setup_driver(headless, browser_preference)
        except Exception as e:
            print(f"❌ Error configurando navegador: {str(e)}")
            self.audit_results["errors"].append({
                "type": "browser_setup",
                "message": str(e)
            })
            return self.audit_results
        
        try:
            # Verificar que el servidor esté ejecutándose
            if not self.check_server_running():
                print("❌ Error: El servidor Astro no está ejecutándose.")
                print("   Ejecuta 'npm run dev' en otra terminal antes de continuar.")
                return self.audit_results
            
            print("✅ Servidor Astro detectado y funcionando")
            
            # Descubrir páginas
            print("🔍 Descubriendo páginas...")
            pages = self.discover_pages()
            print(f"📄 Encontradas {len(pages)} páginas: {pages}")
            
            # Auditar cada página
            for page in pages:
                full_url = self.base_url + page
                print(f"\n🔎 Auditando: {full_url}")
                
                page_result = {
                    "url": full_url,
                    "path": page
                }
                
                # Auditoría de rendimiento
                print("  ⚡ Analizando rendimiento...")
                page_result["performance"] = self.audit_page_performance(full_url)
                
                # Auditoría SEO
                print("  🎯 Verificando SEO...")
                page_result["seo"] = self.audit_seo_basics(full_url)
                
                # Características específicas de Astro
                print("  🌟 Verificando componentes Astro...")
                page_result["astro"] = self.check_astro_specific_features(full_url)
                
                self.audit_results["pages_tested"].append(page_result)
                print(f"  ✅ Página {page} auditada")
            
            print(f"\n🎉 Auditoría completada. {len(pages)} páginas analizadas.")
            
        except Exception as e:
            self.audit_results["errors"].append({
                "type": "audit_error",
                "message": str(e)
            })
            
        finally:
            if self.driver:
                self.driver.quit()
        
        return self.audit_results
    
    def generate_report(self, output_file="audit_report.json"):
        """Genera reportes de la auditoría en JSON y TXT"""
        # Generar reporte JSON
        json_path = os.path.join("../", output_file)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        
        # Generar reporte TXT más legible
        txt_path = os.path.join("../", output_file.replace(".json", ".txt"))
        self.generate_text_report(txt_path)
        
        print(f"\n📊 Reportes guardados:")
        print(f"   📄 Texto legible: {txt_path}")
        print(f"   🔧 Datos técnicos: {json_path}")
        
        # Mostrar resumen en consola
        self.print_summary()
    
    def generate_text_report(self, output_path):
        """Genera un reporte de texto fácil de leer"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("📋 REPORTE DE AUDITORÍA - PROYECTO ASTRO\n")
            f.write("="*80 + "\n\n")
            
            # Información general
            f.write(f"🕒 Fecha y hora: {self.audit_results['timestamp']}\n")
            f.write(f"🌐 URL base: {self.audit_results['base_url']}\n")
            f.write(f"📄 Páginas analizadas: {len(self.audit_results['pages_tested'])}\n")
            f.write(f"❌ Errores encontrados: {len(self.audit_results['errors'])}\n")
            f.write(f"⚠️ Advertencias: {len(self.audit_results['warnings'])}\n\n")
            
            # Resumen ejecutivo
            f.write("-"*80 + "\n")
            f.write("📊 RESUMEN EJECUTIVO\n")
            f.write("-"*80 + "\n\n")
            
            if self.audit_results["pages_tested"]:
                # Calcular promedios
                total_pages = len(self.audit_results["pages_tested"])
                avg_load_time = 0
                seo_issues = 0
                
                for page in self.audit_results["pages_tested"]:
                    perf = page.get("performance", {})
                    if "selenium_load_time" in perf:
                        avg_load_time += perf["selenium_load_time"]
                    
                    seo = page.get("seo", {})
                    if seo.get("title", {}).get("status") == "warning":
                        seo_issues += 1
                    if seo.get("meta_description", {}).get("status") in ["warning", "missing"]:
                        seo_issues += 1
                
                avg_load_time = avg_load_time / total_pages if total_pages > 0 else 0
                
                f.write(f"⚡ Tiempo promedio de carga: {avg_load_time:.2f} segundos\n")
                f.write(f"🎯 Problemas de SEO detectados: {seo_issues}\n")
                f.write(f"🌟 Estado general: {'✅ Bueno' if avg_load_time < 2 and seo_issues < 3 else '⚠️ Necesita atención'}\n\n")
            
            # Análisis por página
            f.write("-"*80 + "\n")
            f.write("📄 ANÁLISIS DETALLADO POR PÁGINA\n")
            f.write("-"*80 + "\n\n")
            
            for i, page in enumerate(self.audit_results["pages_tested"], 1):
                f.write(f"{i}. PÁGINA: {page['path']}\n")
                f.write(f"   URL: {page['url']}\n")
                f.write("-" * 40 + "\n")
                
                # Rendimiento
                perf = page.get("performance", {})
                f.write("⚡ RENDIMIENTO:\n")
                if perf.get("status") == "completed":
                    load_time = perf.get("selenium_load_time", "N/A")
                    f.write(f"   • Tiempo de carga: {load_time}s ")
                    if isinstance(load_time, (int, float)):
                        if load_time < 1:
                            f.write("🟢 Excelente\n")
                        elif load_time < 2:
                            f.write("🟡 Bueno\n")
                        else:
                            f.write("🔴 Lento\n")
                    else:
                        f.write("\n")
                    
                    browser_metrics = perf.get("browser_metrics", {})
                    if browser_metrics.get("resources"):
                        f.write(f"   • Recursos cargados: {browser_metrics['resources']}\n")
                else:
                    f.write(f"   • Error: {perf.get('error', 'Desconocido')}\n")
                
                # SEO
                seo = page.get("seo", {})
                f.write("\n🎯 SEO:\n")
                
                # Título
                title_info = seo.get("title", {})
                if title_info:
                    title_status = "🟢" if title_info.get("status") == "good" else "🟡"
                    f.write(f"   • Título: {title_status} \"{title_info.get('content', 'N/A')[:50]}...\"\n")
                    f.write(f"     Longitud: {title_info.get('length', 'N/A')} caracteres ")
                    if title_info.get('length'):
                        if 10 <= title_info['length'] <= 60:
                            f.write("(Óptimo)\n")
                        else:
                            f.write("(Fuera del rango ideal: 10-60)\n")
                    else:
                        f.write("\n")
                
                # Meta descripción
                meta_info = seo.get("meta_description", {})
                if meta_info.get("status") == "missing":
                    f.write("   • Meta descripción: 🔴 FALTANTE\n")
                elif meta_info.get("content"):
                    status = "🟢" if meta_info.get("status") == "good" else "🟡"
                    f.write(f"   • Meta descripción: {status} \"{meta_info['content'][:50]}...\"\n")
                    f.write(f"     Longitud: {meta_info.get('length', 'N/A')} caracteres ")
                    if meta_info.get('length'):
                        if 120 <= meta_info['length'] <= 160:
                            f.write("(Óptimo)\n")
                        else:
                            f.write("(Fuera del rango ideal: 120-160)\n")
                    else:
                        f.write("\n")
                
                # H1
                h1_info = seo.get("h1_tags", {})
                if h1_info:
                    h1_status = "🟢" if h1_info.get("status") == "good" else "🟡"
                    f.write(f"   • Etiquetas H1: {h1_status} {h1_info.get('count', 0)} encontrada(s)\n")
                    if h1_info.get("texts"):
                        for h1_text in h1_info["texts"]:
                            f.write(f"     - \"{h1_text[:40]}...\"\n")
                
                # Imágenes
                img_info = seo.get("images", {})
                if img_info:
                    total_imgs = img_info.get("total", 0)
                    without_alt = img_info.get("without_alt", 0)
                    if without_alt == 0:
                        f.write(f"   • Imágenes: 🟢 {total_imgs} imágenes, todas con atributo alt\n")
                    else:
                        f.write(f"   • Imágenes: 🟡 {without_alt} de {total_imgs} sin atributo alt\n")
                
                # Características Astro
                astro = page.get("astro", {})
                f.write("\n🌟 ASTRO:\n")
                if not astro.get("error"):
                    f.write(f"   • Componentes Astro: {astro.get('astro_components', 0)}\n")
                    f.write(f"   • Scripts de hidratación: {astro.get('hydration_scripts', 0)}\n")
                    f.write(f"   • Enlaces internos: {astro.get('internal_links', 0)}\n")
                else:
                    f.write(f"   • Error: {astro['error']}\n")
                
                f.write("\n")
            
            # Errores y advertencias
            if self.audit_results["errors"]:
                f.write("-"*80 + "\n")
                f.write("❌ ERRORES ENCONTRADOS\n")
                f.write("-"*80 + "\n\n")
                for i, error in enumerate(self.audit_results["errors"], 1):
                    f.write(f"{i}. {error.get('message', 'Error desconocido')}\n")
                    if error.get('suggestion'):
                        f.write(f"   Solución: {error['suggestion']}\n")
                    f.write("\n")
            
            if self.audit_results["warnings"]:
                f.write("-"*80 + "\n")
                f.write("⚠️ ADVERTENCIAS\n")
                f.write("-"*80 + "\n\n")
                for i, warning in enumerate(self.audit_results["warnings"], 1):
                    f.write(f"{i}. {warning}\n\n")
            
            # Recomendaciones
            f.write("-"*80 + "\n")
            f.write("💡 RECOMENDACIONES\n")
            f.write("-"*80 + "\n\n")
            
            recommendations = []
            
            # Analizar problemas comunes
            slow_pages = []
            seo_issues = []
            
            for page in self.audit_results["pages_tested"]:
                perf = page.get("performance", {})
                if perf.get("selenium_load_time", 0) > 2:
                    slow_pages.append(page["path"])
                
                seo = page.get("seo", {})
                if seo.get("meta_description", {}).get("status") == "missing":
                    seo_issues.append(f"Agregar meta descripción a {page['path']}")
                if seo.get("title", {}).get("status") == "warning":
                    seo_issues.append(f"Optimizar título en {page['path']}")
            
            if slow_pages:
                recommendations.append(f"🚀 Optimizar velocidad de carga en: {', '.join(slow_pages)}")
            
            if seo_issues:
                recommendations.extend([f"🎯 {issue}" for issue in seo_issues[:3]])  # Primeras 3
            
            if not recommendations:
                recommendations.append("✅ ¡Tu sitio está en buen estado! Continúa monitoreando regularmente.")
            
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("🔚 FIN DEL REPORTE\n")
            f.write("="*80 + "\n")
    
    def print_summary(self):
        """Imprime un resumen de los resultados"""
        print("\n" + "="*60)
        print("📋 RESUMEN DE AUDITORÍA")
        print("="*60)
        
        total_pages = len(self.audit_results["pages_tested"])
        print(f"Páginas analizadas: {total_pages}")
        print(f"Errores encontrados: {len(self.audit_results['errors'])}")
        print(f"Advertencias: {len(self.audit_results['warnings'])}")
        
        if self.audit_results["pages_tested"]:
            print("\n🚀 RENDIMIENTO:")
            for page in self.audit_results["pages_tested"]:
                perf = page.get("performance", {})
                if "selenium_load_time" in perf:
                    print(f"  {page['path']}: {perf['selenium_load_time']}s")
            
            print("\n🎯 SEO:")
            for page in self.audit_results["pages_tested"]:
                seo = page.get("seo", {})
                title_status = seo.get("title", {}).get("status", "unknown")
                print(f"  {page['path']}: Título {title_status}")
        
        if self.audit_results["errors"]:
            print("\n❌ ERRORES:")
            for error in self.audit_results["errors"]:
                print(f"  - {error.get('message', 'Error desconocido')}")

    def check_system_requirements(self):
        """Verifica los requisitos del sistema"""
        print("🔍 Verificando requisitos del sistema...")
        print(f"🐍 Python: {sys.version}")
        
        # Verificar Selenium
        try:
            import selenium
            print(f"🔧 Selenium: {selenium.__version__}")
        except ImportError:
            print("❌ Selenium no instalado")
            return False
        
        # Verificar Chrome
        chrome_path = self.find_chrome_executable()
        if chrome_path:
            print(f"✅ Chrome encontrado en: {chrome_path}")
        else:
            print("⚠️ Chrome no encontrado")
        
        # Verificar Edge
        edge_path = self.find_edge_executable()
        if edge_path:
            print(f"✅ Edge encontrado en: {edge_path}")
        else:
            print("⚠️ Edge no encontrado")
        
        if not chrome_path and not edge_path:
            print("❌ No se encontró ningún navegador compatible.")
            print("   Instala Google Chrome o Microsoft Edge para continuar.")
            return False
        
        return True

def main():
    """Función principal para ejecutar la auditoría"""
    print("🔧 Auditor de Proyectos Astro con Selenium")
    print("VERSIÓN COMPATIBLE - Selenium 3 y 4")
    print("-" * 50)
    
    # Crear auditor para verificar requisitos
    temp_auditor = AstroAuditor()
    if not temp_auditor.check_system_requirements():
        print("\n💡 Para solucionar problemas de dependencias, ejecuta:")
        print("   pip install --upgrade selenium webdriver-manager")
        return
    
    # Configuración
    base_url = input("\nURL base del proyecto (por defecto http://localhost:4321): ").strip()
    if not base_url:
        base_url = "http://localhost:4321"
    
    headless = input("¿Ejecutar en modo headless? (y/N): ").lower().startswith('y')
    
    browser_choice = input("¿Preferir Chrome o Edge? (chrome/edge, por defecto chrome): ").lower()
    if browser_choice not in ['chrome', 'edge']:
        browser_choice = 'chrome'
    
    # Crear y ejecutar auditor
    auditor = AstroAuditor(base_url)
    results = auditor.run_complete_audit(headless=headless, browser_preference=browser_choice)
    
    # Generar reporte si no hubo errores críticos
    if auditor.audit_results["pages_tested"]:
        auditor.generate_report()
        print("\n✨ Auditoría completada. Revisa el archivo audit_report.json para detalles completos.")
    else:
        print("\n❌ La auditoría no pudo completarse debido a errores.")
        print("\n💡 Consejos para solucionar:")
        print("   1. Actualizar Selenium: pip install --upgrade selenium")
        print("   2. Instalar webdriver-manager: pip install webdriver-manager")
        print("   3. Verificar que Chrome/Edge esté actualizado")

if __name__ == "__main__":
    main()