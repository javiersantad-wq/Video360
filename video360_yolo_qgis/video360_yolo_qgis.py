#!/usr/bin/env python3
"""
Video360 YOLO Detector para QGIS
================================
Herramienta completa para procesar videos 360°, detectar objetos con YOLO
y generar shapefiles georreferenciados.

Parámetros configurables:
-----------------------
- Distancia entre frames (metros)
- Radio de detección (metros)
- Modelo YOLO
- Confianza mínima
- Output directory

Uso:
----
    python video360_yolo_qgis.py --video video.mp4 --gps track.gpx [opciones]

Ejemplo:
--------
    python video360_yolo_qgis.py --video 360.mp4 --gps track.gpx --distance 10 --model yolo11n
"""

import os
import sys
import json
import argparse
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import math

# GIS
try:
    import geopandas as gpd
    from shapely.geometry import Point, buffer
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("ADVERTENCIA: geopandas no está instalado")

# YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("ADVERTENCIA: ultralytics no está instalado")

# GPX
try:
    import gpxpy
    GPXPY_AVAILABLE = True
except ImportError:
    GPXPY_AVAILABLE = False
    print("ADVERTENCIA: gpxpy no está instalado")


class GPSMetadata:
    """Gestiona metadata GPS del video."""
    
    def __init__(self):
        self.waypoints = []
    
    def load_from_gpx(self, gpx_path):
        """Carga datos desde archivo GPX."""
        if not GPXPY_AVAILABLE:
            raise ImportError("gpxpy requerido: pip install gpxpy")
        
        with open(gpx_path, 'r') as f:
            gpx = gpxpy.parse(f)
        
        points = gpx.tracks[0].segments[0].points
        base_time = points[0].time.timestamp()
        
        for point in points:
            self.waypoints.append({
                'lat': round(point.latitude, 7),
                'lon': round(point.longitude, 7),
                'alt': round(point.elevation or 0, 1),
                'timestamp': int((point.time.timestamp() - base_time) * 1000),
                'speed': point.speed or 30
            })
        
        print(f"GPS cargado: {len(self.waypoints)} puntos")
        return self
    
    def interpolate(self, timestamp_ms):
        """Interpola coordenadas para un timestamp."""
        if not self.waypoints:
            return None
        
        for i, wp in enumerate(self.waypoints):
            if wp['timestamp'] >= timestamp_ms:
                if i == 0:
                    return wp.copy()
                prev = self.waypoints[i-1]
                curr = wp
                ratio = (timestamp_ms - prev['timestamp']) / (curr['timestamp'] - prev['timestamp'])
                return {
                    'lat': prev['lat'] + ratio * (curr['lat'] - prev['lat']),
                    'lon': prev['lon'] + ratio * (curr['lon'] - prev['lon']),
                    'alt': prev['alt'] + ratio * (curr['alt'] - prev['alt']),
                    'speed': prev['speed']
                }
        return self.waypoints[-1].copy()
    
    def calculate_distance(self, wp1, wp2):
        """Calcula distancia entre dos puntos (metros)."""
        R = 6371000
        lat1, lon1 = math.radians(wp1['lat']), math.radians(wp1['lon'])
        lat2, lon2 = math.radians(wp2['lat']), math.radians(wp2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return 2 * R * math.asin(math.sqrt(a))


class Video360Extractor:
    """Extrae frames de video 360° cada N metros."""
    
    def __init__(self, video_path, gps_data=None, distance_interval=20, output_dir='frames'):
        self.video_path = video_path
        self.distance_interval = distance_interval
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.gps = GPSMetadata()
        if gps_data:
            self.gps.waypoints = gps_data
        
        self.frames = []
        self.total_distance = 0
        self.last_point = None
    
    def extract(self):
        """Extrae frames cada distancia especificada."""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir: {self.video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_ms = (total_frames / fps) * 1000
        
        print(f"Video: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)} @ {fps:.2f} fps")
        print(f"Duración: {duration_ms/1000:.1f}s | Extrayendo cada {self.distance_interval}m...")
        
        frame_idx = 0
        ms = 0
        step_ms = 1000  # 1 segundo inicial
        
        while ms < duration_ms:
            gps = self.gps.interpolate(ms)
            
            should_extract = False
            if self.last_point and gps:
                dist = self.gps.calculate_distance(self.last_point, gps)
                if dist >= self.distance_interval:
                    should_extract = True
                    self.total_distance += dist
                    self.last_point = gps
            elif gps:
                should_extract = True
                self.last_point = gps
            
            if should_extract:
                cap.set(cv2.CAP_PROP_POS_MSEC, ms)
                ret, frame = cap.read()
                
                if ret:
                    filename = f"frame_{frame_idx:04d}.jpg"
                    filepath = self.output_dir / filename
                    cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    
                    self.frames.append({
                        'index': frame_idx,
                        'filename': filename,
                        'filepath': str(filepath),
                        'timestamp_ms': int(ms),
                        'gps': gps
                    })
                    
                    # Estimar siguiente step basado en velocidad
                    if gps and gps.get('speed', 0) > 0:
                        step_ms = (self.distance_interval / gps['speed']) * 1000
                    
                    frame_idx += 1
                    print(f"  Frame {frame_idx}: {gps['lat']:.5f}, {gps['lon']:.5f} ({dist:.1f}m)")
            
            ms += step_ms
        
        cap.release()
        
        # Guardar metadata
        metadata = {
            'video_path': self.video_path,
            'distance_interval': self.distance_interval,
            'total_frames': len(self.frames),
            'total_distance': self.total_distance,
            'frames': self.frames
        }
        
        with open(self.output_dir / 'extraction_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ {len(self.frames)} frames extraídos ({self.total_distance:.0f}m)")
        return self.frames


class YOLODetector:
    """Detecta objetos con YOLO."""
    
    COCO_CLASSES = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle',
        5: 'bus', 6: 'train', 7: 'truck', 9: 'traffic light',
        11: 'stop sign', 15: 'bird', 16: 'cat', 17: 'dog'
    }
    
    def __init__(self, model='yolo11n.pt', confidence=0.25, detection_radius=10.0):
        if not YOLO_AVAILABLE:
            raise ImportError("ultralytics requerido: pip install ultralytics")
        
        self.model = YOLO(model)
        self.confidence = confidence
        self.detection_radius = detection_radius
        self.detections = []
        
        print(f"YOLO cargado: {model} (confianza: {confidence})")
    
    def process_frames(self, frames_dir, metadata_path=None):
        """Procesa todos los frames."""
        frames_dir = Path(frames_dir)
        
        # Cargar metadata
        frames_info = []
        if metadata_path and Path(metadata_path).exists():
            with open(metadata_path) as f:
                data = json.load(f)
                frames_info = {f['index']: f for f in data.get('frames', [])}
        
        # Procesar cada frame
        for frame_file in sorted(frames_dir.glob('frame_*.jpg')):
            img = cv2.imread(str(frame_file))
            if img is None:
                continue
            
            idx = int(frame_file.stem.split('_')[1])
            frame_gps = frames_info.get(idx, {}).get('gps', {})
            
            results = self.model(img, conf=self.confidence, verbose=False)
            
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    detection = {
                        'class_id': cls,
                        'class_name': self.COCO_CLASSES.get(cls, f'class_{cls}'),
                        'confidence': conf,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'center': [int((x1+x2)/2), int((y1+y2)/2)],
                        'frame_index': idx,
                        'frame_path': str(frame_file),
                        'timestamp_str': frames_info.get(idx, {}).get('timestamp_ms', 0)
                    }
                    
                    # Calcular posición geográfica
                    if frame_gps:
                        detection['geo_position'] = self.calculate_geo_position(
                            detection['center'], frame_gps
                        )
                    
                    self.detections.append(detection)
            
            print(f"  {frame_file.name}: {len([d for d in self.detections if d['frame_index'] == idx])} detecciones")
        
        print(f"\n✓ Total: {len(self.detections)} detecciones")
        
        # Guardar crops
        self.save_crops(frames_dir)
        
        return self.detections
    
    def calculate_geo_position(self, center, frame_gps):
        """Calcula posición geográfica de una detección."""
        # Estimación simplificada: asume detección a detection_radius metros
        # En realidad necesitarías más datos (heading de la cámara)
        
        # Usar azimuth del centro como aproximación
        img_w = 1920  # Asumir resolución estándar
        az_deg = ((center[0] / img_w) - 0.5) * 360
        
        R = 6371000
        lat1, lon1 = math.radians(frame_gps['lat']), math.radians(frame_gps['lon'])
        az_rad = math.radians(az_deg)
        
        lat2 = math.asin(
            math.sin(lat1) * math.cos(self.detection_radius / R) +
            math.cos(lat1) * math.sin(self.detection_radius / R) * math.cos(az_rad)
        )
        
        lon2 = lon1 + math.atan2(
            math.sin(az_rad) * math.sin(self.detection_radius / R) * math.cos(lat1),
            math.cos(self.detection_radius / R) - math.sin(lat1) * math.sin(lat2)
        )
        
        return {
            'lat': math.degrees(lat2),
            'lon': math.degrees(lon2),
            'alt': frame_gps.get('alt', 0),
            'distance_m': self.detection_radius,
            'bearing_deg': az_deg,
            'azimuth_pixel': az_deg
        }
    
    def save_crops(self, frames_dir, crops_dir=None):
        """Guarda recortes de detecciones."""
        if crops_dir is None:
            crops_dir = frames_dir / 'crops'
        crops_dir = Path(crops_dir)
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        for det in self.detections:
            if not det.get('bbox'):
                continue
            
            x1, y1, x2, y2 = det['bbox']
            img = cv2.imread(det['frame_path'])
            if img is None:
                continue
            
            h, w = img.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 > x1 and y2 > y1:
                crop = img[y1:y2, x1:x2]
                filename = f"crop_{det['frame_index']:04d}_{det['class_name']}_{det['confidence']:.2f}.jpg"
                filepath = crops_dir / filename
                cv2.imwrite(str(filepath), crop)
                det['crop_path'] = str(filepath)
        
        print(f"✓ Recortes guardados en: {crops_dir}")
    
    def save_detections(self, output_path):
        """Guarda detecciones en JSON."""
        with open(output_path, 'w') as f:
            json.dump({
                'model': self.model.model_name,
                'confidence': self.confidence,
                'detection_radius': self.detection_radius,
                'total_detections': len(self.detections),
                'detections': self.detections
            }, f, indent=2)
        
        print(f"✓ Detecciones guardadas: {output_path}")


class ShapefileGenerator:
    """Genera shapefiles desde detecciones."""
    
    def __init__(self, output_dir='shapefile', detection_radius=10.0):
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("geopandas requerido: pip install geopandas")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.detection_radius = detection_radius
        self.features = []
    
    def add_detections(self, detections):
        """Agrega detecciones."""
        for det in detections:
            if not det.get('geo_position'):
                continue
            
            geo = det['geo_position']
            props = {
                'id': len(self.features),
                'class_id': det.get('class_id'),
                'class_name': det.get('class_name'),
                'confidence': round(det.get('confidence', 0), 3),
                'frame_idx': det.get('frame_index'),
                'lat': round(geo.get('lat', 0), 7),
                'lon': round(geo.get('lon', 0), 7),
                'alt_m': round(geo.get('alt', 0), 2),
                'dist_m': round(geo.get('distance_m', 0), 2),
                'bearing': round(geo.get('bearing_deg', 0), 2)
            }
            
            # Copiar crop si existe
            crop_path = det.get('crop_path', '')
            if crop_path and Path(crop_path).exists():
                props['has_crop'] = 1
            
            self.features.append({
                'geometry': Point(geo['lon'], geo['lat']),
                **props
            })
    
    def generate(self):
        """Genera shapefiles."""
        if not self.features:
            print("No hay detecciones con posición geográfica")
            return {}
        
        gdf = gpd.GeoDataFrame(self.features, crs='EPSG:4326')
        
        results = {}
        
        # Puntos
        points_path = self.output_dir / 'detections_points.shp'
        gdf.to_file(points_path)
        results['points'] = str(points_path)
        print(f"✓ Shapefile puntos: {points_path}")
        
        # Buffers (círculos de 10m)
        buffers = []
        for f in self.features:
            buffers.append({
                **f,
                'geometry': f['geometry'].buffer(self.detection_radius)
            })
        
        gdf_buffer = gpd.GeoDataFrame(buffers, crs='EPSG:4326')
        buffer_path = self.output_dir / 'detections_buffer.shp'
        gdf_buffer.to_file(buffer_path)
        results['buffer'] = str(buffer_path)
        print(f"✓ Shapefile buffer: {buffer_path}")
        
        # GeoJSON
        geojson_path = self.output_dir / 'detections.geojson'
        gdf.to_file(geojson_path, driver='GeoJSON')
        results['geojson'] = str(geojson_path)
        print(f"✓ GeoJSON: {geojson_path}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Video360 YOLO Detector para QGIS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  # Básico
  python video360_yolo_qgis.py --video video.mp4 --gps track.gpx
  
  # Con opciones personalizadas
  python video360_yolo_qgis.py --video 360.mp4 --gps track.gpx --distance 10 --model yolo11s --confidence 0.3
  
  # Solo detección (si ya tienes frames)
  python video360_yolo_qgis.py --video 360.mp4 --step detect --frames-dir ./frames
        '''
    )
    
    # Video
    parser.add_argument('--video', required=True, help='Ruta al video 360°')
    parser.add_argument('--gps', help='Ruta al archivo GPX (opcional)')
    
    # Parámetros
    parser.add_argument('--distance', type=int, default=20, 
                       help='Distancia entre frames en metros (default: 20)')
    parser.add_argument('--radius', type=float, default=10.0,
                       help='Radio de detección en metros (default: 10)')
    parser.add_argument('--model', default='yolo11n.pt',
                       help='Modelo YOLO (default: yolo11n.pt)')
    parser.add_argument('--confidence', type=float, default=0.25,
                       help='Umbral de confianza (default: 0.25)')
    parser.add_argument('--output', default='output',
                       help='Directorio de salida (default: output)')
    
    # Paso a ejecutar
    parser.add_argument('--step', choices=['extract', 'detect', 'shapefile', 'all'],
                       default='all', help='Paso a ejecutar (default: all)')
    parser.add_argument('--frames-dir', help='Directorio de frames (para --step detect)')
    
    args = parser.parse_args()
    
    # Validar
    if not os.path.exists(args.video):
        print(f"ERROR: Video no encontrado: {args.video}")
        sys.exit(1)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    frames_dir = output_dir / 'frames'
    detections_path = output_dir / 'detections.json'
    shapefile_dir = output_dir / 'shapefile'
    
    print("=" * 60)
    print("Video360 YOLO Detector para QGIS")
    print("=" * 60)
    print(f"Video: {args.video}")
    print(f"Distancia: {args.distance}m")
    print(f"Modelo: {args.model}")
    print(f"Confianza: {args.confidence}")
    print(f"Radio: {args.radius}m")
    print("=" * 60)
    
    frames = []
    detections = []
    
    # === EXTRACT ===
    if args.step in ['extract', 'all']:
        print("\n[1/3] Extrayendo frames...")
        
        # Cargar GPS
        gps_data = None
        if args.gps and os.path.exists(args.gps):
            gps = GPSMetadata().load_from_gpx(args.gps)
            gps_data = {'waypoints': gps.waypoints}
        
        extractor = Video360Extractor(
            video_path=args.video,
            gps_data=gps_data,
            distance_interval=args.distance,
            output_dir=str(frames_dir)
        )
        
        frames = extractor.extract()
        print(f"Frames extraídos: {len(frames)}")
    
    # === DETECT ===
    if args.step in ['detect', 'all']:
        print("\n[2/3] Ejecutando YOLO...")
        
        # Buscar frames si no se extrajeron
        if not frames:
            metadata_path = frames_dir / 'extraction_metadata.json'
            if metadata_path.exists():
                with open(metadata_path) as f:
                    data = json.load(f)
                    frames = data.get('frames', [])
        
        detector = YOLODetector(
            model=args.model,
            confidence=args.confidence,
            detection_radius=args.radius
        )
        
        detections = detector.process_frames(
            str(frames_dir),
            metadata_path=str(frames_dir / 'extraction_metadata.json')
        )
        
        detector.save_detections(str(detections_path))
    
    # === SHAPEFILE ===
    if args.step in ['shapefile', 'all']:
        print("\n[3/3] Generando Shapefile...")
        
        if not detections:
            if detections_path.exists():
                with open(detections_path) as f:
                    data = json.load(f)
                    detections = data.get('detections', [])
        
        if detections:
            gen = ShapefileGenerator(
                output_dir=str(shapefile_dir),
                detection_radius=args.radius
            )
            gen.add_detections(detections)
            results = gen.generate()
            
            print("\n" + "=" * 60)
            print("RESUMEN")
            print("=" * 60)
            print(f"Frames: {len(frames)}")
            print(f"Detecciones: {len(detections)}")
            print(f"Output: {output_dir}")
            print(f"  - Frames: {frames_dir}")
            print(f"  - Detecciones: {detections_path}")
            print(f"  - Shapefile: {shapefile_dir}")
        else:
            print("No hay detecciones para procesar")
    
    print("\n✓ Proceso completado!")
    
    return output_dir


if __name__ == "__main__":
    main()
