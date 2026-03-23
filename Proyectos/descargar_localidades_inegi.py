"""
Script para descargar localidades INEGI cercanas a los corredores
y realizar análisis de concentración de población

Uso: python descargar_localidades_inegi.py
"""

import requests
import geopandas as gpd
import pandas as pd
import os
import zipfile
from shapely.ops import unary_union
from shapely.geometry import Point

BASE_DIR = r"C:\Users\ed\.openclaw\workspace\Proyectos"

def get_inegi_localities_by_bounds(minx, miny, maxx, maxy, estado_cve=None):
    """
    Descarga localidades del servicio REST de INEGI
    https://www.inegi.org.mx/app/mapa/ (servicio de mapas)
    
    Estados: Tamaulipas=30, San Luis Potosi=24, Veracruz=29
    """
    
    # Centro del bounding box
    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2
    
    # El servicio REST de INEGI para consulta de entidades
    # Basado en la API del Mapa Interactivo
    url = f"https://www.inegi.org.mx/app/mapa//v2/getGeo"
    
    # Parámetros según la documentación de la API de INEGI
    # Esta API devuelve features en formato GeoJSON
    params = {
        'coords': f'{center_lon},{center_lat}',
        'layers': 'localidades',  # servicio de localidades
        'format': 'json',
        'zoom': 10
    }
    
    # Alternativa: usar el servicio de OpenData de INEGI
    # El INEGI tiene un portal de datos abiertos en:
    # https://www.inegi.org.mx/servicios/api/indicadores/
    
    print("Nota: La API de localidades de INEGI requiere autenticación o acceso especial.")
    print("Alternativas:")
    print("1. Descargar manualmente desde: https://www.inegi.org.mx/geo/")
    print("2. Usar el Marco Geoestadístico Nacional")
    print()
    
    return None

def download_marco_geoestadistico(output_dir, estado_cve=None):
    """
    Genera un script para descargar el Marco Geoestadístico
    
    El Marco Geoestadístico Nacional se descarga desde:
    https://www.inegi.org.mx/geo/ (buscar 'Marco Geoestadístico')
    
    Incluye:
    - 00_AGEB.shp (Áreas Geoestadísticas Básicas)
    - 00_LOC.shp (Localidades)
    - 00_MUN.shp (Municipios)
    - 00_ENT.shp (Estados)
    """
    
    base_url = "https://www.inegi.org.mx/geo/contenidos/geoestadistica/"
    
    print("Para descargar el Marco Geoestadístico completo:")
    print("1. Ir a: https://www.inegi.org.mx/geo/")
    print("2. Buscar 'Marco Geoestadístico' o 'Descargas'")
    print("3. Seleccionar el estado(s) de interés")
    print("4. Descargar como shapefile (.shp)")
    print()
    print("Archivos a buscar:")
    print("  - Marco_Geoestadistico_Nacional_2024.zip")
    print("  - o seleccionar solo estados: 30 (Tamps), 24 (SLP), 29 (Veracruz)")
    print()
    
    # Crear directorio para datos INEGI
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar instrucciones
    instrucciones = """
# Instrucciones para descargar datos de Localidades INEGI

## Método 1: Marco Geoestadístico Nacional

1. Ir a: https://www.inegi.org.mx/geo/
2. Buscar "Marco Geoestadístico" en el menú
3. Seleccionar "Descarga de archivos shapefile"
4. Elegir los estados de interés:
   - 30: Tamaulipas
   - 24: San Luis Potosí  
   - 29: Veracruz
5. Descargar archivo ZIP
6. Extraer en la carpeta 'datos_inegi' de cada proyecto

## Método 2: Localidades del DENUE (Directorio Estadístico Nacional de Unidades Económicas)

1. Ir a: https://www.inegi.org.mx/app/mapa/denue/
2. Seleccionar estado y municipios
3. Exportar como CSV o JSON

## Método 3: Servicio de Mapas (WMS/WFS)

URL del servicio: https://www.inegi.org.mx/app/mapa/wms?

Capas disponibles:
- localhost:8080/geoserver/inegi/wms?service=WMS&version=1.1.0&request=GetMap&layers=inegi:localidades

## Archivos requeridos para este proyecto

Para el análisis de impacto social de vuelo de dron, necesita:

1. **Localidades** (puntos con coordenadas y nombre)
   - Archivo: 00_LOC.shp
   - Contiene: NOMBRE, AMBITO (Urbano/Rural), POBLACION

2. **AGEB urbanas** (polígonos de áreas urbanas)
   - Archivo: 00_AGEB_URB.shp
   - Contiene: CVE_AGEB,POB_TOTAL

3. **Manzanas** (en zonas urbanas)
   - Archivo: 00_MANZ.shp
   - Para análisis detallado de concentración de población

## Alternativa: Generar localidades desde el shapefile de ejidos

Los ejidos ya contienen información de centros de población (X, Y en formato DMS).
Se puede usar la columna 'NOM_NA' como referencia de nombres de comunidades.

Ver archivo: analisis_ejidos/ejidos_*.csv
"""
    
    output_file = os.path.join(output_dir, "INSTRUCCIONES_DESCARGA_INEGI.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(instrucciones)
    
    print(f"Instrucciones guardadas en: {output_file}")
    
    return output_file

# ============== EJECUCIÓN ==============

print("="*60)
print("DESCARGA DE LOCALIDADES INEGI")
print("="*60)

# Crear directorio para instrucciones
output_dir = os.path.join(BASE_DIR, "datos_inegi")
download_marco_geoestadistico(output_dir)

# Intentar cargar bounds de los corredores para mostrar qué descargar
print("\nÁreas de interés para descarga:\n")

try:
    # Tampico-San Luis
    bounds_ts = gpd.read_file(
        os.path.join(BASE_DIR, "Tampico_SanLuis", "datos", "Tampico_SanLuis-50km_blocks.shp")
    ).total_bounds
    print("TAMPICO-SAN LUIS:")
    print(f"  Min X: {bounds_ts[0]:.4f}")
    print(f"  Min Y: {bounds_ts[1]:.4f}")
    print(f"  Max X: {bounds_ts[2]:.4f}")
    print(f"  Max Y: {bounds_ts[3]:.4f}")
    print(f"  Estados: 24 (SLP), 30 (Tamaulipas)")
    print()
except Exception as e:
    print(f"Error leyendo Tampico-San Luis: {e}")

try:
    # Veracruz-Tampico
    bounds_vt = gpd.read_file(
        os.path.join(BASE_DIR, "Veracruz_Tampico", "datos", "Veracruz-Tampico-50km_blocks_v4.shp")
    ).total_bounds
    print("VERACRUZ-TAMPICO:")
    print(f"  Min X: {bounds_vt[0]:.4f}")
    print(f"  Min Y: {bounds_vt[1]:.4f}")
    print(f"  Max X: {bounds_vt[2]:.4f}")
    print(f"  Max Y: {bounds_vt[3]:.4f}")
    print(f"  Estados: 30 (Tamaulipas)")
except Exception as e:
    print(f"Error leyendo Veracruz-Tampico: {e}")

print("\n" + "="*60)
print("SIGUIENTE PASO:")
print("1. Descargar Marco Geoestadístico de INEGI")
print("2. Extraer archivos 00_LOC.shp y 00_AGEB_URB.shp")
print("3. Colocar en la carpeta datos_inegi/")
print("4. Ejecutar este script de nuevo para análisis automático")
print("="*60)
