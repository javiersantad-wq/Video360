"""
Descarga localidades de OpenStreetMap para los corredores de proyectos
y genera archivos shapefile para ArcMap
"""

import requests
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os
from shapely.ops import unary_union

BASE_DIR = r"C:\Users\ed\.openclaw\workspace\Proyectos"
OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

def get_osm_localities(bbox, timeout=120):
    """
    Obtiene localidades de OpenStreetMap dentro de un bounding box
    
    bbox: (south, west, north, east) en grados
    """
    south, west, north, east = bbox
    
    query = f'[out:json][timeout:{timeout}];'
    query += f'(node[place=city]({south},{west},{north},{east});'
    query += f'node[place=town]({south},{west},{north},{east});'
    query += f'node[place=village]({south},{west},{north},{east});'
    query += f'node[place=hamlet]({south},{west},{north},{east});'
    query += f'node[place=suburb]({south},{west},{north},{east});'
    query += f'node[place=neighbourhood]({south},{west},{north},{east});'
    query += f'node[place=locality]({south},{west},{north},{east});'
    query += ');out body;'
    
    print(f'  Consultando OSM: bbox=({south},{west},{north},{east})')
    
    r = requests.post(OVERPASS_URL, data={'data': query}, timeout=timeout+10)
    r.raise_for_status()
    
    data = r.json()
    elements = data.get('elements', [])
    print(f'  Encontradas: {len(elements)} localidades')
    
    return elements

def elements_to_gdf(elements):
    """Convierte elementos OSM a GeoDataFrame"""
    records = []
    for el in elements:
        tags = el.get('tags', {})
        geom = Point(el['lon'], el['lat'])
        records.append({
            'osm_id': el['id'],
            'name': tags.get('name', 'Sin nombre'),
            'place': tags.get('place', 'N/A'),
            'population': tags.get('population', None),
            'municipality': tags.get('admin_level', None),
            'state': tags.get('is_in:state', None),
            'country': tags.get('is_in:country', None),
            'geometry': geom
        })
    
    gdf = gpd.GeoDataFrame(records, crs='EPSG:4326')
    return gdf

def filter_by_distance_to_corridor(localities_gdf, corridor_path, buffer_km=5):
    """Filtra localidades cercanas al corredor"""
    from shapely.ops import unary_union
    import numpy as np
    
    # Cargar corredor
    corridor = gpd.read_file(corridor_path)
    corridor_union = unary_union(corridor.geometry)
    
    # Buffer around corridor (in degrees)
    buffer_deg = buffer_km / 111.0
    
    # Calculate distance and filter
    localities_gdf['dist_to_corridor_km'] = localities_gdf.geometry.apply(
        lambda p: p.distance(corridor_union) * 111 if p.is_valid else np.nan
    )
    
    nearby = localities_gdf[localities_gdf['dist_to_corridor_km'] <= buffer_km].copy()
    return nearby, corridor_union

# ============== MAIN ==============

print("="*60)
print("DESCARGA DE LOCALIDADES DESDE OPENSTREETMAP")
print("="*60)

# Definir bounding boxes para cada corredor
# Tamps-SLP corredor: -100.95 a -97.87, 21.85 a 22.28
bbox_ts = (21.5, -101.5, 22.8, -97.5)

# Veracruz-Tamps corredor: -97.95 a -96.22, 19.14 a 22.28
bbox_vt = (18.5, -98.5, 22.8, -96.0)

# paths
corredor_ts = os.path.join(BASE_DIR, "Tampico_SanLuis", "datos", "Tampico_SanLuis-50km_blocks.shp")
corredor_vt = os.path.join(BASE_DIR, "Veracruz_Tampico", "datos", "Veracruz-Tampico-50km_blocks_v4.shp")

# ---- PROYECTO TAMPICO-SAN LUIS ----
print("\n" + "="*40)
print("PROYECTO: TAMPICO - SAN LUIS")
print("="*40)

print("Descargando localidades OSM...")
elements_ts = get_osm_localities(bbox_ts)
gdf_ts = elements_to_gdf(elements_ts)
print(f"Total OSM: {len(gdf_ts)} localidades")

# Filtrar por cercanía al corredor
print("Filtrando por distancia al corredor (5km)...")
nearby_ts, _ = filter_by_distance_to_corridor(gdf_ts, corredor_ts, buffer_km=5)
print(f"Cercanas al corredor: {len(nearby_ts)} localidades")

# Guardar CSV
csv_ts = os.path.join(BASE_DIR, "Tampico_SanLuis", "analisis", "localidades_cercanas.csv")
nearby_ts.drop(columns=['geometry']).to_csv(csv_ts, index=False)
print(f"CSV guardado: {csv_ts}")

# Guardar shapefile
shp_ts = os.path.join(BASE_DIR, "Tampico_SanLuis", "datos", "localidades_osm.shp")
nearby_ts.to_file(shp_ts)
print(f"Shapefile guardado: {shp_ts}")

# ---- PROYECTO VERACRUZ-TAMPICO ----
print("\n" + "="*40)
print("PROYECTO: VERACRUZ - TAMPICO")
print("="*40)

print("Descargando localidades OSM...")
elements_vt = get_osm_localities(bbox_vt)
gdf_vt = elements_to_gdf(elements_vt)
print(f"Total OSM: {len(gdf_vt)} localidades")

# Filtrar por cercanía al corredor
print("Filtrando por distancia al corredor (5km)...")
nearby_vt, _ = filter_by_distance_to_corridor(gdf_vt, corredor_vt, buffer_km=5)
print(f"Cercanas al corredor: {len(nearby_vt)} localidades")

# Guardar CSV
csv_vt = os.path.join(BASE_DIR, "Veracruz_Tampico", "analisis", "localidades_cercanas.csv")
nearby_vt.drop(columns=['geometry']).to_csv(csv_vt, index=False)
print(f"CSV guardado: {csv_vt}")

# Guardar shapefile
shp_vt = os.path.join(BASE_DIR, "Veracruz_Tampico", "datos", "localidades_osm.shp")
nearby_vt.to_file(shp_vt)
print(f"Shapefile guardado: {shp_vt}")

# ---- RESUMEN ----
print("\n" + "="*60)
print("RESUMEN")
print("="*60)
print(f"Tampico-San Luis: {len(nearby_ts)} localidades a 5km del corredor")
print(f"Veracruz-Tampico: {len(nearby_vt)} localidades a 5km del corredor")
print()
print("Archivos generados:")
print(f"  {shp_ts}")
print(f"  {shp_vt}")
print(f"  {csv_ts}")
print(f"  {csv_vt}")
print()
print("¡Listo para cargar en ArcMap!")
