"""
ShapefileGenerator - Genera shapefiles con detecciones georreferenciadas
=========================================================================
Crea shapefiles (SHP, GeoJSON) con las detecciones YOLO y sus recortes.
"""

import os
import json
import math
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import tempfile
import shutil

# Intentar importar bibliotecas GIS
try:
    import geopandas as gpd
    from shapely.geometry import Point, box, Polygon
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("Advertencia: geopandas no instalado. Instalar con: pip install geopandas shapely")

try:
    from osgeo import ogr, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False


@dataclass
class DetectionFeature:
    """Feature para agregar al shapefile."""
    geometry: Point
    properties: Dict


class ShapefileGenerator:
    """
    Genera shapefiles con detecciones georreferenciadas.
    
    Parámetros:
    -----------
    output_dir : str
        Directorio de salida
    crs : str
        Sistema de referencia de coordenadas (default: 'EPSG:4326')
    detection_radius : float
        Radio de las detecciones en metros (default: 10)
    """
    
    def __init__(self, 
                 output_dir: str = "./shapefile_output",
                 crs: str = "EPSG:4326",
                 detection_radius: float = 10.0):
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.crs = crs
        self.detection_radius = detection_radius
        
        self.features: List[Dict] = []
        self.crops_dir = self.output_dir / "crops"
        self.crops_dir.mkdir(exist_ok=True)
    
    def add_detection(self, detection: Dict):
        """Agrega una detección al shapefile."""
        if not detection.get('geo_position'):
            return
        
        geo = detection['geo_position']
        
        # Copiar crop si existe
        crop_path = detection.get('crop_path')
        rel_crop_path = None
        
        if crop_path and os.path.exists(crop_path):
            # Copiar a directorio de crops
            crop_filename = os.path.basename(crop_path)
            dest_crop = self.crops_dir / crop_filename
            shutil.copy2(crop_path, dest_crop)
            rel_crop_path = f"crops/{crop_filename}"
        
        # Crear feature
        feature = {
            'geometry': {
                'type': 'Point',
                'coordinates': [geo['lon'], geo['lat']]
            },
            'properties': {
                'id': len(self.features),
                'class_id': detection.get('class_id'),
                'class_name': detection.get('class_name'),
                'confidence': round(detection.get('confidence', 0), 3),
                'frame_idx': detection.get('frame_index'),
                'frame_file': os.path.basename(detection.get('frame_path', '')),
                'lat': round(geo.get('lat', 0), 7),
                'lon': round(geo.get('lon', 0), 7),
                'alt_m': round(geo.get('alt', 0), 2),
                'dist_m': round(geo.get('distance_m', 0), 2),
                'bearing_deg': round(geo.get('bearing_deg', 0), 2),
                'azimuth': round(geo.get('azimuth_pixel', 0), 2),
                'elevation': round(geo.get('elevation', 0), 2),
                'crop_path': rel_crop_path or '',
                'timestamp': detection.get('timestamp_str', '')
            }
        }
        
        self.features.append(feature)
    
    def add_detections(self, detections: List[Dict]):
        """Agrega múltiples detecciones."""
        for det in detections:
            self.add_detection(det)
    
    def create_point_shapefile(self, filename: str = "detections_points.shp") -> str:
        """Crea shapefile de puntos."""
        if not GEOPANDAS_AVAILABLE:
            return self._create_shapefile_ogr(filename, as_points=True)
        
        features = []
        
        for f in self.features:
            geom = Point(f['geometry']['coordinates'])
            features.append({
                'geometry': geom,
                **f['properties']
            })
        
        if not features:
            print("No hay features para crear shapefile")
            return ""
        
        gdf = gpd.GeoDataFrame(features, crs=self.crs)
        
        output_path = self.output_dir / filename
        gdf.to_file(output_path)
        
        print(f"Shapefile de puntos creado: {output_path}")
        return str(output_path)
    
    def create_buffer_shapefile(self, filename: str = "detections_buffer.shp") -> str:
        """Crea shapefile con polígonos buffer (círculos de 10m)."""
        if not GEOPANDAS_AVAILABLE:
            return ""
        
        features = []
        
        for f in self.features:
            geom = Point(f['geometry']['coordinates'])
            # Buffer de 10 metros
            buffer = geom.buffer(self.detection_radius)
            features.append({
                'geometry': buffer,
                **f['properties']
            })
        
        if not features:
            return ""
        
        gdf = gpd.GeoDataFrame(features, crs=self.crs)
        
        output_path = self.output_dir / filename
        gdf.to_file(output_path)
        
        print(f"Shapefile con buffer creado: {output_path}")
        return str(output_path)
    
    def create_geojson(self, filename: str = "detections.geojson") -> str:
        """Crea archivo GeoJSON."""
        if not GEOPANDAS_AVAILABLE:
            return self._create_geojson_manual(filename)
        
        features = []
        
        for f in self.features:
            # Convertir Point a coordenadas
            coords = [f['geometry']['coordinates'][0], f['geometry']['coordinates'][1]]
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': coords
                },
                'properties': f['properties']
            })
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"GeoJSON creado: {output_path}")
        return str(output_path)
    
    def _create_shapefile_ogr(self, filename: str, as_points: bool = True) -> str:
        """Crea shapefile usando GDAL/OGR directamente."""
        if not GDAL_AVAILABLE:
            print("ERROR: Se requiere geopandas o GDAL para crear shapefile")
            return ""
        
        output_path = self.output_dir / filename
        
        # Driver
        driver = ogr.GetDriverByName('ESRI Shapefile')
        
        # Crear datasource
        if os.path.exists(str(output_path)):
            driver.DeleteDataSource(str(output_path))
        
        ds = driver.CreateDataSource(str(output_path))
        
        # Spatial reference
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        
        # Layer
        layer = ds.CreateLayer('detections', srs, ogr.wkbPoint)
        
        # Campos
        fields = [
            ('id', ogr.OFTInteger),
            ('class_id', ogr.OFTInteger),
            ('class_name', ogr.OFTString),
            ('confidence', ogr.OFTReal),
            ('lat', ogr.OFTReal),
            ('lon', ogr.OFTReal),
            ('alt_m', ogr.OFTReal),
            ('dist_m', ogr.OFTReal),
            ('bearing', ogr.OFTReal),
            ('crop_path', ogr.OFTString)
        ]
        
        for name, ftype in fields:
            layer.CreateField(ogr.FieldDefn(name, ftype))
        
        # Features
        for f in self.features:
            props = f['properties']
            geom = ogr.CreateGeometryFromWkt(
                f"POINT({props['lon']} {props['lat']})"
            )
            
            feat = ogr.Feature(layer.GetLayerDefn())
            feat.SetGeometry(geom)
            feat.SetField('id', props['id'])
            feat.SetField('class_id', props['class_id'])
            feat.SetField('class_name', props['class_name'])
            feat.SetField('confidence', props['confidence'])
            feat.SetField('lat', props['lat'])
            feat.SetField('lon', props['lon'])
            feat.SetField('alt_m', props['alt_m'])
            feat.SetField('dist_m', props['dist_m'])
            feat.SetField('bearing', props['bearing_deg'])
            feat.SetField('crop_path', props.get('crop_path', ''))
            
            layer.CreateFeature(feat)
        
        ds = None
        print(f"Shapefile creado: {output_path}")
        return str(output_path)
    
    def _create_geojson_manual(self, filename: str) -> str:
        """Crea GeoJSON manualmente (sin dependencias GIS)."""
        features = []
        
        for f in self.features:
            features.append({
                'type': 'Feature',
                'geometry': f['geometry'],
                'properties': f['properties']
            })
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        return str(output_path)
    
    def generate_all(self) -> Dict[str, str]:
        """Genera todos los formatos de salida."""
        results = {}
        
        if self.features:
            results['points'] = self.create_point_shapefile()
            results['buffer'] = self.create_buffer_shapefile()
            results['geojson'] = self.create_geojson()
        
        # Metadata
        metadata = {
            'total_detections': len(self.features),
            'crs': self.crs,
            'detection_radius': self.detection_radius,
            'classes_found': list(set(f['properties']['class_name'] for f in self.features)),
            'files': {k: str(v) for k, v in results.items()}
        }
        
        with open(self.output_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return results
    
    def get_summary(self) -> Dict:
        """Resumen de las detecciones."""
        if not self.features:
            return {'total': 0}
        
        classes = {}
        for f in self.features:
            cls = f['properties']['class_name']
            classes[cls] = classes.get(cls, 0) + 1
        
        return {
            'total': len(self.features),
            'by_class': classes,
            'with_crops': sum(1 for f in self.features if f['properties']['crop_path'])
        }


def create_shapefile_from_detections(
    detections: List[Dict],
    output_dir: str = "./shapefile_output",
    crs: str = "EPSG:4326",
    detection_radius: float = 10.0
) -> Dict[str, str]:
    """
    Función de conveniencia para crear shapefile.
    
    Uso:
    ----
    >>> results = create_shapefile_from_detections(
    ...     detections=detections_list,
    ...     output_dir="./output",
    ...     detection_radius=10.0
    ... )
    """
    generator = ShapefileGenerator(
        output_dir=output_dir,
        crs=crs,
        detection_radius=detection_radius
    )
    
    generator.add_detections(detections)
    
    return generator.generate_all()


if __name__ == "__main__":
    # Ejemplo
    print("Shapefile Generator listo.")
    print("Uso: create_shapefile_from_detections(detections, output_dir)")
