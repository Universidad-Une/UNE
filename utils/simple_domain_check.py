#!/usr/bin/env python3
"""
Simple Domain Check - Solo verifica cuáles dominios están activos
"""

import requests
import warnings

# Desactivar advertencias SSL
warnings.filterwarnings('ignore')

def is_domain_active(domain, timeout=8):
    """Verifica si un dominio está activo"""
    for protocol in ['https://', 'http://']:
        try:
            url = f"{protocol}{domain}"
            response = requests.get(
                url, 
                timeout=timeout, 
                allow_redirects=True, 
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; Checker/1.0)'}
            )
            if response.status_code == 200:
                return True, url, response.status_code
        except:
            continue
    return False, None, None

def load_domains_from_file(filename):
    """Carga dominios desde el archivo"""
    domains = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '.com' in line:
                    # Extraer dominio de líneas numeradas
                    if '. ' in line and line[0].isdigit():
                        domain = line.split('. ', 1)[1].strip()
                    else:
                        domain = line.strip()
                    
                    # Limpiar el dominio
                    if domain and not domain.startswith('_'):
                        domain = domain.split()[0]  # Solo la primera parte
                        if domain not in domains:
                            domains.append(domain)
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return []
    
    return domains

def main():
    # Cargar dominios
    domains = load_domains_from_file("dominios_reales.txt")
    
    if not domains:
        print("❌ No se pudieron cargar dominios")
        return
    
    print(f"🔍 Verificando {len(domains)} dominios...")
    print("=" * 50)
    
    activos = []
    
    for i, domain in enumerate(domains, 1):
        print(f"{i:3d}. Verificando {domain}...", end=" ")
        
        is_active, url, status_code = is_domain_active(domain)
        
        if is_active:
            activos.append((domain, url, status_code))
            print(f"✅ ACTIVO ({status_code}) - {url}")
        else:
            print("❌ No responde")
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN:")
    print(f"Total verificados: {len(domains)}")
    print(f"Activos: {len(activos)}")
    print(f"Inactivos: {len(domains) - len(activos)}")
    
    if activos:
        print(f"\n✅ DOMINIOS ACTIVOS ({len(activos)}):")
        print("-" * 40)
        for domain, url, status in activos:
            print(f"   {domain} → {url}")
        
        # Guardar activos en archivo
        with open("dominios_activos.txt", "w", encoding="utf-8") as f:
            f.write("DOMINIOS ACTIVOS UNE\n")
            f.write("==================\n\n")
            for domain, url, status in activos:
                f.write(f"{domain} → {url} (HTTP {status})\n")
        
        print(f"\n📁 Lista guardada en: dominios_activos.txt")

if __name__ == "__main__":
    main()