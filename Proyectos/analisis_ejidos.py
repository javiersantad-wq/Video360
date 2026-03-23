"""
Análisis de Ejidos para Proyectos de Vuelo de Dron
Corredores: Tampico-San Luis y Veracruz-Tampico
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
import os

# Rutas
BASE_DIR = r"C:\Users\ed\.openclaw\workspace\Proyectos"
EJIDOS_PATH = os.path.join(BASE_DIR, "ejidos_temp", "ejidos_wgs84_geo.shp")
OUTPUT_DIR = os.path.join(BASE_DIR, "analisis_ejidos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cargar ejidos
print("Cargando ejidos (esto puede tardar un momento)...")
ejidos = gpd.read_file(EJIDOS_PATH)
print(f"Total de ejidos en México: {len(ejidos):,}")

# Función para encontrar ejidos cercanos a un corredor
def encontrar_ejidos_cercanos(corredor_gdf, ejidos_gdf, buffer_km=2):
    """
    Encuentra ejidos que intersectan o están cerca de un corredor.
    
    Args:
        corredor_gdf: GeoDataFrame con líneas del corredor
        ejidos_gdf: GeoDataFrame con polígonos de ejidos
        buffer_km: Distancia en km para considerar 'cercano'
    
    Returns:
        GeoDataFrame con ejidos encontrados
    """
    # Unir todas las líneas del corredor en una sola geometría
    corredor_union = unary_union(corredor_gdf.geometry)
    
    # Crear buffer alrededor del corredor (en grados, aproxima 1 grado = 111 km)
    buffer_degrees = buffer_km / 111.0
    
    # Find ejidos that intersect with buffer
    mask = ejidos_gdf.geometry.intersects(corredor_union.buffer(buffer_degrees))
    ejidos_cercanos = ejidos_gdf[mask].copy()
    
    # Calculate distance to corridor for each ejido
    ejidos_cercanos['distancia_km'] = ejidos_cercanos.geometry.centroid.distance(corredor_union) * 111
    
    return ejidos_cercanos

# Cargar corredores
print("\n" + "="*60)
print("PROYECTO 1: TAMPICO - SAN LUIS")
print("="*60)

corredor_ts = gpd.read_file(
    r"C:\Users\ed\.openclaw\workspace\Proyectos\Tampico_SanLuis\datos\Tampico_SanLuis-50km_blocks.shp"
)
print(f"Bloques en corredor: {len(corredor_ts)}")
print(f"Extensión: {corredor_ts.total_bounds}")

# Encontrar ejidos - primero filtrar por estado (Tamaulipas ~ CVE_ESTADO 28, San Luis Potosi ~ 24)
# Pero primero veamos qué estados cubren los bloques
print("\nBloques disponibles:")
for idx, row in corredor_ts.iterrows():
    print(f"  - {row['Name']} ({row['km']:.1f} km, bloque {row['bloque']})")

print("\nBuscando ejidos cercanos...")
ejidos_ts = encontrar_ejidos_cercanos(corredor_ts, ejidos, buffer_km=2)
print(f"Ejidos encontrados a 2km: {len(ejidos_ts)}")

if len(ejidos_ts) > 0:
    print("\nPrimeros 10 ejidos:")
    cols = ['NOMBRE', 'CVE_ESTADO', 'CVE_MPIO', 'Hectares', 'distancia_km', 'NOM_NA']
    print(ejidos_ts[cols].head(10).to_string())
    
    # Guardar
    output_ts = os.path.join(OUTPUT_DIR, "ejidos_Tampico_SanLuis.geojson")
    ejidos_ts.to_file(output_ts, driver='GeoJSON')
    print(f"\nGuardado: {output_ts}")
    
    # CSV para Excel
    csv_ts = os.path.join(OUTPUT_DIR, "ejidos_Tampico_SanLuis.csv")
    ejidos_ts[cols].to_csv(csv_ts, index=False)
    print(f"Guardado: {csv_ts}")

print("\n" + "="*60)
print("PROYECTO 2: VERACRUZ - TAMPICO")
print("="*60)

corredor_vt = gpd.read_file(
    r"C:\Users\ed\.openclaw\workspace\Proyectos\Veracruz_Tampico\datos\Veracruz-Tampico-50km_blocks_v4.shp"
)
print(f"Bloques en corredor: {len(corredor_vt)}")
print(f"Extensión: {corredor_vt.total_bounds}")

print("\nBloques disponibles:")
for idx, row in corredor_vt.iterrows():
    print(f"  - {row['Name']} ({row['km']:.1f} km, bloque {row['bloque']})")

print("\nBuscando ejidos cercanos...")
ejidos_vt = encontrar_ejidos_cercanos(corredor_vt, ejidos, buffer_km=2)
print(f"Ejidos encontrados a 2km: {len(ejidos_vt)}")

if len(ejidos_vt) > 0:
    print("\nPrimeros 10 ejidos:")
    cols = ['NOMBRE', 'CVE_ESTADO', 'CVE_MPIO', 'Hectareas', 'distancia_km', 'NOM_NA']
    cols_to_show = ['NOMBRE', 'CVE_ESTADO', 'CVE_MPIO', 'distancia_km', 'NOM_NA']
    if 'Hectareas' in ejidos_vt.columns:
        cols_to_show.insert(4, 'Hectareas')
    elif 'Hectares' in ejidos_vt.columns:
        cols_to_show.insert(4, 'Hectares')
    print(ejidos_vt[cols_to_show].head(10).to_string())
    
    # Guardar
    output_vt = os.path.join(OUTPUT_DIR, "ejidos_Veracruz_Tampico.geojson")
    ejidos_vt.to_file(output_vt, driver='GeoJSON')
    print(f"\nGuardado: {output_vt}")
    
    # CSV para Excel
    csv_vt = os.path.join(OUTPUT_DIR, "ejidos_Veracruz_Tampico.csv")
    ejidos_vt[cols_to_show].to_csv(csv_vt, index=False)
    print(f"Guardado: {csv_vt}")

# Resumen por estado
print("\n" + "="*60)
print("RESUMEN DE ESTADOS")
print("="*60)

if len(ejidos_ts) > 0:
    print("\nEstados cubiertos por proyecto Tampico-San Luis:")
    print(ejidos_ts['CVE_ESTADO'].value_counts().head(10))

if len(ejidos_vt) > 0:
    print("\nEstados cubiertos por proyecto Veracruz-Tampico:")
    print(ejidos_vt['CVE_ESTADO'].value_counts().head(10))

print("\n¡Análisis completado!")
