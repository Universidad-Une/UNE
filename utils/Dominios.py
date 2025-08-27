#!/usr/bin/env python3
"""
Quick Domain Checker - Verificador rápido de dominios
Solo verifica si el dominio responde, sin análisis detallado
"""

import requests
import concurrent.futures
from urllib3.disable_warnings import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import time
from datetime import datetime

# Desactivar advertencias SSL para dominios con certificados problemáticos
disable_warnings(InsecureRequestWarning)

def quick_check_domain(domain, timeout=10):
    """Verificación rápida de un dominio"""
    result = {
        'domain': domain,
        'status': 'unknown',
        'url': None,
        'http_code': None,
        'response_time_ms': None,
        'error': None
    }
    
    # Probar HTTPS primero, luego HTTP
    for protocol in ['https://', 'http://']:
        url = f"{protocol}{domain}"
        try:
            start_time = time.time()
            response = requests.get(
                url, 
                timeout=timeout, 
                allow_redirects=True, 
                verify=False,  # Ignorar errores SSL
                headers={'User-Agent': 'Mozilla/5.0 (compatible; DomainChecker/1.0)'}
            )
            response_time = round((time.time() - start_time) * 1000, 2)
            
            result.update({
                'status': '✅ ACTIVO',
                'url': url,
                'http_code': response.status_code,
                'response_time_ms': response_time
            })
            return result
            
        except requests.exceptions.SSLError:
            if protocol == 'https://':
                continue  # Intentar HTTP
            result.update({
                'status': '🟡 SSL_ERROR',
                'error': 'SSL Certificate Error'
            })
            
        except requests.exceptions.ConnectionError:
            result.update({
                'status': '🔴 NO_RESPONDE',
                'error': 'Connection refused or DNS not found'
            })
            
        except requests.exceptions.Timeout:
            result.update({
                'status': '🟠 TIMEOUT',
                'error': f'Timeout after {timeout}s'
            })
            
        except Exception as e:
            result.update({
                'status': '⚠️ ERROR',
                'error': str(e)
            })
    
    return result

def check_domains_batch(domains, max_workers=10, timeout=8):
    """Verifica múltiples dominios en paralelo"""
    results = []
    total = len(domains)
    
    print(f"🚀 Verificando {total} dominios...")
    print(f"⚙️  Usando {max_workers} workers, timeout {timeout}s\n")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todas las tareas
        future_to_domain = {
            executor.submit(quick_check_domain, domain, timeout): domain 
            for domain in domains
        }
        
        # Recoger resultados conforme van completándose
        for i, future in enumerate(concurrent.futures.as_completed(future_to_domain), 1):
            domain = future_to_domain[future]
            try:
                result = future.result()
                results.append(result)
                
                # Mostrar progreso
                status_symbol = result['status'].split()[0]
                print(f"{i:3d}/{total} {status_symbol} {domain:<40} {result.get('response_time_ms', 0):>6}ms")
                
            except Exception as e:
                error_result = {
                    'domain': domain,
                    'status': '❌ EXCEPCION',
                    'error': str(e)
                }
                results.append(error_result)
                print(f"{i:3d}/{total} ❌ {domain:<40} ERROR: {str(e)}")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Completado en {elapsed:.1f} segundos")
    
    return results

def generate_summary(results):
    """Genera un resumen de los resultados"""
    total = len(results)
    activos = len([r for r in results if '✅' in r['status']])
    no_responden = len([r for r in results if '🔴' in r['status']])
    ssl_errors = len([r for r in results if '🟡' in r['status']])
    timeouts = len([r for r in results if '🟠' in r['status']])
    errors = len([r for r in results if '⚠️' in r['status'] or '❌' in r['status']])
    
    print(f"\n📊 RESUMEN:")
    print(f"{'='*50}")
    print(f"Total dominios:     {total}")
    print(f"✅ Activos:          {activos:3d} ({activos/total*100:5.1f}%)")
    print(f"🔴 No responden:     {no_responden:3d} ({no_responden/total*100:5.1f}%)")
    print(f"🟡 Errores SSL:      {ssl_errors:3d} ({ssl_errors/total*100:5.1f}%)")
    print(f"🟠 Timeouts:         {timeouts:3d} ({timeouts/total*100:5.1f}%)")
    print(f"⚠️  Otros errores:    {errors:3d} ({errors/total*100:5.1f}%)")
    
    return {
        'total': total,
        'activos': activos,
        'no_responden': no_responden,
        'ssl_errors': ssl_errors,
        'timeouts': timeouts,
        'errors': errors
    }

def save_results_simple(results, filename_prefix="quick_check"):
    """Guarda resultados en formato simple"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("VERIFICACIÓN RÁPIDA DE DOMINIOS UNE\n")
        f.write("=" * 50 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total dominios: {len(results)}\n\n")
        
        # Agrupar por estado
        activos = [r for r in results if '✅' in r['status']]
        no_responden = [r for r in results if '🔴' in r['status']]
        ssl_errors = [r for r in results if '🟡' in r['status']]
        timeouts = [r for r in results if '🟠' in r['status']]
        errors = [r for r in results if '⚠️' in r['status'] or '❌' in r['status']]
        
        if activos:
            f.write(f"✅ DOMINIOS ACTIVOS ({len(activos)}):\n")
            f.write("-" * 30 + "\n")
            for r in sorted(activos, key=lambda x: x['response_time_ms'] or 0):
                f.write(f"{r['domain']:<40} {r['http_code']} {r['response_time_ms']}ms {r['url']}\n")
            f.write("\n")
        
        if ssl_errors:
            f.write(f"🟡 ERRORES SSL ({len(ssl_errors)}):\n")
            f.write("-" * 20 + "\n")
            for r in ssl_errors:
                f.write(f"{r['domain']}\n")
            f.write("\n")
        
        if no_responden:
            f.write(f"🔴 NO RESPONDEN ({len(no_responden)}):\n")
            f.write("-" * 20 + "\n")
            for r in no_responden:
                f.write(f"{r['domain']}\n")
            f.write("\n")
        
        if timeouts:
            f.write(f"🟠 TIMEOUTS ({len(timeouts)}):\n")
            f.write("-" * 15 + "\n")
            for r in timeouts:
                f.write(f"{r['domain']}\n")
            f.write("\n")
        
        if errors:
            f.write(f"⚠️ ERRORES ({len(errors)}):\n")
            f.write("-" * 15 + "\n")
            for r in errors:
                f.write(f"{r['domain']:<40} {r.get('error', 'Unknown error')}\n")
    
    print(f"📁 Resultados guardados en: {filename}")
    return filename

def load_domains_from_txt(filename):
    """Carga dominios desde tu archivo dominios_reales.txt"""
    domains = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar líneas que contengan dominios .com
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Si la línea tiene numeración, extraer la parte después del número
            if '. ' in line and line[0].isdigit():
                domain = line.split('. ', 1)[1].strip()
            else:
                domain = line
            
            # Verificar que sea un dominio válido .com
            if '.com' in domain and not domain.startswith('_') and not domain.startswith('default.'):
                # Remover posibles caracteres extra
                domain = domain.split()[0] if ' ' in domain else domain
                if domain not in domains:
                    domains.append(domain)
                    
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {filename}")
        return []
    except Exception as e:
        print(f"❌ Error leyendo {filename}: {e}")
        return []
    
    return domains

def main():
    """Función principal"""
    # Intentar cargar desde tu archivo
    domains = load_domains_from_txt("dominios_reales.txt")
    
    if not domains:
        print("⚠️  No se pudieron cargar dominios desde el archivo")
        print("Usando dominios de ejemplo...")
        domains = [
            "une-enlinea.com",
            "universidad-une.com", 
            "vivetuuniversidad.com",
            "moodle.une-enlinea.com",
            "virtual.une-enlinea.com",
            "admin.universidad-une.com"
        ]
    
    print(f"📋 Dominios cargados: {len(domains)}")
    
    # Si hay muchos dominios, preguntar confirmación
    if len(domains) > 50:
        response = input(f"\n🤔 Se van a verificar {len(domains)} dominios. ¿Continuar? (s/n): ")
        if response.lower() not in ['s', 'si', 'y', 'yes']:
            print("Operación cancelada.")
            return
    
    # Ejecutar verificación
    results = check_domains_batch(
        domains, 
        max_workers=8,  # Ajustar según tu conexión
        timeout=10      # Timeout por dominio
    )
    
    # Mostrar resumen
    generate_summary(results)
    
    # Guardar resultados
    save_results_simple(results)
    
    # Mostrar algunos dominios activos como ejemplo
    activos = [r for r in results if '✅' in r['status']]
    if activos:
        print(f"\n🎯 Primeros dominios activos encontrados:")
        for r in activos[:5]:
            print(f"   {r['domain']} → {r['url']}")
        if len(activos) > 5:
            print(f"   ... y {len(activos)-5} más")

if __name__ == "__main__":
    main()