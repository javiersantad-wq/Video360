"""
Generador de Líneas de Vuelo para Levantamiento LiDAR

Basado en los corredores de los proyectos:
- Tampico_SanLuis
- Veracruz_Tampico

Uso:
python generar_lineas_vuelo.py
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
import os

BASE_DIR = r"C:\Users\ed\.openclaw\workspace\Proyectos"

def generate_flight_lines(corridor_gdf, buffer_m=20, altitude_m=80, overlap=0.3, line_spacing_m=None):
    """
    Genera líneas de vuelo paralelas a un corredor lineal.
    
    Parámetros:
    - corridor_gdf: GeoDataFrame con el corredor
    - buffer_m: Buffer a cada lado del corredor (metros)
    - altitude_m: Altura de vuelo (metros sobre terreno)
    - overlap: Sobreposición lateral (0.3 = 30%)
    - line_spacing_m: Espaciado entre líneas (calculado automáticamente si None)
    
    Retorna:
    - GeoDataFrame con las líneas de vuelo
    """
    
    # Unir todas las geometrías del corredor
    corridor_union = unary_union(corridor_gdf.geometry)
    
    # Buffer para definir el área de cobertura
    buffer_deg = buffer_m / 111000  # Conversión aproximada metros a grados
    
    # Ancho efectivo de cobertura (asumiendo escaneo a 90°)
    # A 80m de altura, cobertura ~120m
    swath_width_m = altitude_m * 1.5  # Factor de escaneo típico
    swath_width_deg = swath_width_m / 111000
    
    # Espaciado entre líneas
    if line_spacing_m is None:
        effective_width = swath_width_deg * (1 - overlap)
        line_spacing_deg = effective_width
    
    # Crear líneas paralelas
    flight_lines = []
    
    # Obtener bounds del corredor
    minx, miny, maxx, maxy = corridor_gdf.total_bounds
    
    # Número de líneas basado en el ancho del corredor + buffer
    corridor_width_deg = maxx - minx
    corridor_height_deg = maxy - miny
    
    # Para corredores lineales, generar líneas perpendiculares al corredor
    # Usarapproach de líneas paralelas desplazadas
    
    # Simplificar el corredor a una línea central
    if corridor_union.geom_type == 'MultiLineString':
        # Unir en una línea media (promedio de puntos)
        all_coords = []
        for line in corridor_union.geoms:
            all_coords.extend(list(line.coords))
        center_line = LineString(all_coords[::10])  # Sample cada 10 puntos
    else:
        center_line = corridor_union
    
    # Generar líneas paralelas perpendiculares
    num_lines = int((buffer_deg * 2) / line_spacing_deg) + 1
    
    for i in range(num_lines):
        offset = -buffer_deg + (i * line_spacing_deg)
        
        # Crear línea paralela desplazada
        try:
            parallel = center_line.parallel_offset(offset * 111000, 'left')
            if parallel.geom_type == 'MultiLineString':
                parallel = parallel.geoms[0]
            flight_lines.append({
                'line_id': f'FL_{i+1:03d}',
                'type': 'flight_line',
                'altitude_m': altitude_m,
                'geometry': parallel
            })
        except:
            pass
    
    return gpd.GeoDataFrame(flight_lines, crs='EPSG:4326')


def analyze_block_for_flight(block_name, block_geom, corridor_gdf):
    """
    Analiza un bloque individual y sugiere parámetros de vuelo.
    """
    # Calcular longitud
    length_m = block_geom.length * 111000  # Grados a metros
    
    # Estimar área
    bounds = block_geom.bounds
    area_approx = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) * 111000 * 111000
    
    # Tiempo estimado de vuelo (minutos)
    flight_time_min = (area_approx / 10000) / 0.3456 + 10  # Coverage rate
    
    return {
        'block_name': block_name,
        'length_m': length_m,
        'area_ha': area_approx / 10000,
        'est_flight_time_min': flight_time_min,
        'batteries_needed': int(np.ceil(flight_time_min / 25)) + 1
    }


def generate_block_summary(corridor_path, output_dir, project_name):
    """
    Genera un resumen de flight planning por bloque.
    """
    
    print(f"Analizando proyecto: {project_name}")
    print("="*60)
    
    # Cargar corredor
    gdf = gpd.read_file(corridor_path)
    
    results = []
    
    for idx, row in gdf.iterrows():
        block_name = row.get('Name', f'Block_{idx}')
        block_num = row.get('bloque', idx)
        km = row.get('km', 0)
        
        # Análisis por bloque
        analysis = analyze_block_for_flight(block_name, row.geometry, gdf)
        analysis['block_num'] = block_num
        analysis['km'] = km
        results.append(analysis)
    
    # Crear DataFrame
    df = pd.DataFrame(results)
    
    # Guardar CSV
    csv_path = os.path.join(output_dir, f'{project_name}_flight_summary.csv')
    df.to_csv(csv_path, index=False)
    print(f"Resumen guardado: {csv_path}")
    
    # Resumen por bloque
    print(f"\nTotal de bloques: {len(df)}")
    print(f"Longitud total: {df['length_m'].sum()/1000:.1f} km")
    print(f"Área total: {df['area_ha'].sum():.1f} ha")
    print(f"Tiempo total estimado: {df['est_flight_time_min'].sum()/60:.1f} horas")
    print(f"Baterías totales estimadas: {df['batteries_needed'].sum()}")
    
    # Por número de bloque
    print("\n" + "="*60)
    print("RESUMEN POR BLOQUE:")
    print("="*60)
    print(f"{'Bloque':<8} {'Nombre':<35} {'km':<8} {'min':<8} {'bat':<5}")
    print("-"*60)
    
    for _, row in df.iterrows():
        name = str(row['block_name'])[:33]
        print(f"{int(row['block_num']):<8} {name:<35} {row['km']:<8.1f} {row['est_flight_time_min']:<8.0f} {row['batteries_needed']:<5}")
    
    return df


def generate_flight_plan_for_project(corridor_path, output_dir, project_name):
    """
    Genera un plan de vuelo completo para un proyecto.
    """
    
    # Cargar corredor
    gdf = gpd.read_file(corridor_path)
    
    # Generar flight lines para todo el corredor
    print(f"\nGenerando líneas de vuelo para {project_name}...")
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar summary
    df = generate_block_summary(corridor_path, output_dir, project_name)
    
    # Generar líneas de vuelo por bloque
    print(f"\nGenerando líneas de vuelo por bloque...")
    
    all_lines = []
    
    for idx, row in gdf.iterrows():
        block_name = row.get('Name', f'Block_{idx}').replace(' ', '_').replace('/', '_')
        block_num = row.get('bloque', idx)
        
        try:
            # Generar líneas para este bloque
            lines = generate_flight_lines(
                gdf.iloc[[idx]],
                buffer_m=30,  # 30m a cada lado
                altitude_m=80,
                overlap=0.3
            )
            
            lines['block_name'] = block_name
            lines['block_num'] = block_num
            all_lines.append(lines)
            
        except Exception as e:
            print(f"  Error en bloque {idx}: {e}")
    
    # Combinar todas las líneas
    if all_lines:
        all_lines_gdf = pd.concat(all_lines, ignore_index=True)
        
        # Guardar como GeoJSON
        geojson_path = os.path.join(output_dir, f'{project_name}_flight_lines.geojson')
        all_lines_gdf.to_file(geojson_path, driver='GeoJSON')
        print(f"Líneas de vuelo guardadas: {geojson_path}")
        
        # Guardar como shapefile
        shp_path = os.path.join(output_dir, f'{project_name}_flight_lines.shp')
        all_lines_gdf.to_file(shp_path)
        print(f"Shapefile guardado: {shp_path}")
        
        return all_lines_gdf
    
    return None


# ============== MAIN ==============

if __name__ == "__main__":
    
    print("="*70)
    print("GENERADOR DE PLANES DE VUELO PARA LEVANTAMIENTO LiDAR")
    print("="*70)
    
    # Proyecto 1: Tampico - San Luis
    corredor_ts = os.path.join(BASE_DIR, "Tampico_SanLuis", "datos", "Tampico_SanLuis-50km_blocks.shp")
    output_ts = os.path.join(BASE_DIR, "Tampico_SanLuis", "datos")
    
    print("\n" + "="*70)
    print("PROYECTO 1: TAMPICO - SAN LUIS")
    print("="*70)
    
    try:
        lines_ts = generate_flight_plan_for_project(corredor_ts, output_ts, "Tampico_SanLuis")
        print(f"\n✓ Proyecto 1 completado: {len(lines_ts) if lines_ts is not None else 0} líneas generadas")
    except Exception as e:
        print(f"\n✗ Error en proyecto 1: {e}")
    
    # Proyecto 2: Veracruz - Tampico
    corredor_vt = os.path.join(BASE_DIR, "Veracruz_Tampico", "datos", "Veracruz-Tampico-50km_blocks_v4.shp")
    output_vt = os.path.join(BASE_DIR, "Veracruz_Tampico", "datos")
    
    print("\n" + "="*70)
    print("PROYECTO 2: VERACRUZ - TAMPICO")
    print("="*70)
    
    try:
        lines_vt = generate_flight_plan_for_project(corredor_vt, output_vt, "Veracruz_Tampico")
        print(f"\n✓ Proyecto 2 completado: {len(lines_vt) if lines_vt is not None else 0} líneas generadas")
    except Exception as e:
        print(f"\n✗ Error en proyecto 2: {e}")
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)
    print("\nArchivos generados:")
    print("  - *_flight_summary.csv: Resumen por bloque")
    print("  - *_flight_lines.geojson: Líneas de vuelo (para GIS)")
    print("  - *_flight_lines.shp: Shapefile de líneas de vuelo")
    print("\nNota: Las líneas son aproximaciones. Para flight planning real,")
    print("      usar software especializado como UGCS o QGroundControl.")
