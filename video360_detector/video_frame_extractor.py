"""
Video360FrameExtractor - Extracción de frames de video 360 con metadata GPS
===========================================================================
Extrae frames cada N metros de un video 360°, guardando coordenadas y altitud.
"""

import cv2
import os
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import numpy as np

# Intentar importar dependencias opcionales
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

try:
    from PyQt5.QtCore import QObject, pyqtSignal
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


class GPSMetadata:
    """Gestor de metadata GPS del video."""
    
    def __init__(self):
        self.waypoints: List[Dict] = []
        self.current_index = 0
    
    def add_waypoint(self, lat: float, lon: float, alt: float, 
                     timestamp_ms: int, speed: float = 0.0):
        """Agrega un waypoint GPS."""
        self.waypoints.append({
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'timestamp_ms': timestamp_ms,
            'speed': speed
        })
    
    def interpolate(self, timestamp_ms: int) -> Optional[Dict]:
        """Interpola coordenadas para un timestamp dado."""
        if not self.waypoints:
            return None
        
        # Encontrar waypoints adyacentes
        before = None
        after = None
        
        for wp in self.waypoints:
            if wp['timestamp_ms'] <= timestamp_ms:
                before = wp
            if wp['timestamp_ms'] >= timestamp_ms and after is None:
                after = wp
                break
        
        if before is None:
            return self.waypoints[0].copy()
        if after is None:
            return before.copy()
        if before['timestamp_ms'] == after['timestamp_ms']:
            return before.copy()
        
        # Interpolación lineal
        ratio = (timestamp_ms - before['timestamp_ms']) / \
                (after['timestamp_ms'] - before['timestamp_ms'])
        
        return {
            'lat': before['lat'] + ratio * (after['lat'] - before['lat']),
            'lon': before['lon'] + ratio * (after['lon'] - before['lon']),
            'alt': before['alt'] + ratio * (after['alt'] - before['alt']),
            'speed': before['speed'] + ratio * (after['speed'] - before['speed'])
        }
    
    def calculate_distance(self, wp1: Dict, wp2: Dict) -> float:
        """Calcula distancia entre dos puntos usando Haversine (en metros)."""
        R = 6371000  # Radio terrestre en metros
        
        lat1, lon1 = math.radians(wp1['lat']), math.radians(wp1['lon'])
        lat2, lon2 = math.radians(wp2['lat']), math.radians(wp2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c


class Video360FrameExtractor:
    """
    Extrae frames de video 360° cada cierta distancia.
    
    Parámetros:
    -----------
    video_path : str
        Ruta al archivo de video 360°
    distance_interval : int
        Distancia en metros entre frames (default: 20)
    output_dir : str
        Directorio de salida para frames y metadata
    gps_data : dict, optional
        Datos GPS en formato {'lat': [...], 'lon': [...], 'alt': [...], 'timestamps': [...]}
    """
    
    def __init__(self, 
                 video_path: str,
                 distance_interval: int = 20,
                 output_dir: str = "./output_frames",
                 gps_data: Optional[Dict] = None):
        
        self.video_path = video_path
        self.distance_interval = distance_interval
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.gps_metadata = GPSMetadata()
        
        # Cargar GPS data si se provee
        if gps_data:
            for i in range(len(gps_data.get('lat', []))):
                self.gps_metadata.add_waypoint(
                    lat=gps_data['lat'][i],
                    lon=gps_data['lon'][i],
                    alt=gps_data.get('alt', [0]*len(gps_data['lat']))[i],
                    timestamp_ms=gps_data.get('timestamps', [0]*len(gps_data['lat']))[i],
                    speed=gps_data.get('speed', [0]*len(gps_data['lat']))[i]
                )
        
        # Variables de estado
        self.frames_extracted = []
        self.total_distance = 0.0
        self.last_gps_point = None
        
        # Señales para PyQt (si está disponible)
        if PYQT5_AVAILABLE:
            self.progress_signal = pyqtSignal(int, str)
            self.finished_signal = pyqtSignal(int)
        else:
            self.progress_signal = None
            self.finished_signal = None
    
    def emit_progress(self, progress: int, message: str = ""):
        """Emite señal de progreso."""
        if self.progress_signal:
            self.progress_signal.emit(progress, message)
    
    def emit_finished(self, total_frames: int):
        """Emite señal de finalización."""
        if self.finished_signal:
            self.finished_signal.emit(total_frames)
    
    def extract_metadata_ffprobe(self) -> Optional[Dict]:
        """Extrae metadata GPS usando ffmpeg/ffprobe."""
        if not FFMPEG_AVAILABLE:
            return None
        
        try:
            probe = ffmpeg.probe(self.video_path)
            
            # Buscar metadata GPS en streams
            for stream in probe.get('streams', []):
                if stream.get('codec_name') == 'h264':
                    tags = stream.get('tags', {})
                    # Buscar coordenadas en varios formatos
                    for key, value in tags.items():
                        if 'location' in key.lower() or 'gps' in key.lower():
                            print(f"Found GPS metadata: {key} = {value}")
            return None
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return None
    
    def extract_frames(self, 
                       use_gps_distance: bool = True,
                       fallback_fps: Optional[int] = None) -> List[Dict]:
        """
        Extrae frames del video.
        
        Parámetros:
        -----------
        use_gps_distance : bool
            Si True, usa distancia GPS para间隔. Si False, usa tiempo uniforme.
        fallback_fps : int, optional
            Frames por segundo para fallback si no hay GPS.
            
        Returns:
        --------
        List[Dict]: Lista de frames extraídos con metadata
        """
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {self.video_path}")
        
        # Propiedades del video
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_ms = (frame_count / fps) * 1000
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video: {width}x{height} @ {fps:.2f} fps")
        print(f"Duración: {duration_ms/1000:.2f} segundos")
        print(f"Total frames: {frame_count}")
        
        self.emit_progress(0, "Extrayendo frames...")
        
        # Si hay datos GPS, usar distancia
        if use_gps_distance and self.gps_metadata.waypoints:
            frames = self._extract_by_distance(cap, fps, duration_ms)
        else:
            frames = self._extract_by_time(cap, fps, frame_count, fallback_fps or 1)
        
        cap.release()
        
        # Guardar metadata
        self._save_metadata()
        
        self.emit_finished(len(frames))
        return frames
    
    def _extract_by_distance(self, cap, fps: float, duration_ms: float) -> List[Dict]:
        """Extrae frames basándose en distancia GPS."""
        frames = []
        frame_idx = 0
        frame_ms = 0
        
        while frame_ms < duration_ms:
            # Obtener coordenadas GPS para este frame
            gps = self.gps_metadata.interpolate(frame_ms)
            
            # Verificar distancia desde último punto
            should_extract = False
            
            if self.last_gps_point and gps:
                distance = self.gps_metadata.calculate_distance(
                    self.last_gps_point, gps
                )
                if distance >= self.distance_interval:
                    should_extract = True
                    self.total_distance += distance
                    self.last_gps_point = gps
            elif gps:
                should_extract = True
                self.last_gps_point = gps
            
            if should_extract:
                # Extraer frame
                cap.set(cv2.CAP_PROP_POS_MSEC, frame_ms)
                ret, frame = cap.read()
                
                if ret:
                    frame_data = self._save_frame(
                        frame, frame_idx, gps, frame_ms
                    )
                    frames.append(frame_data)
                    frame_idx += 1
                    self.frames_extracted.append(frame_data)
                    
                    progress = int((frame_ms / duration_ms) * 100)
                    self.emit_progress(
                        progress, 
                        f"Frame {frame_idx}: {gps['lat']:.6f}, {gps['lon']:.6f}"
                    )
            
            # Avanzar al siguiente punto de posible extracción
            if gps:
                # Estimar tiempo para la siguiente distancia
                if gps['speed'] > 0:
                    time_step = (self.distance_interval / gps['speed']) * 1000
                    frame_ms += max(time_step, 1000 / fps)
                else:
                    frame_ms += 1000  # 1 segundo si no hay velocidad
            else:
                frame_ms += 1000  # Default 1 segundo
        
        return frames
    
    def _extract_by_time(self, cap, fps: float, frame_count: int, 
                        interval_sec: float) -> List[Dict]:
        """Extrae frames basándose en tiempo uniforme."""
        frames = []
        frame_idx = 0
        interval_frames = int(fps * interval_sec)
        
        for i in range(0, frame_count, interval_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if ret:
                frame_ms = (i / fps) * 1000
                gps = self.gps_metadata.interpolate(frame_ms)
                
                frame_data = self._save_frame(
                    frame, frame_idx, gps, frame_ms
                )
                frames.append(frame_data)
                frame_idx += 1
                self.frames_extracted.append(frame_data)
                
                progress = int((i / frame_count) * 100)
                self.emit_progress(progress, f"Frame {frame_idx}")
        
        return frames
    
    def _save_frame(self, frame: np.ndarray, index: int, 
                   gps: Optional[Dict], timestamp_ms: float) -> Dict:
        """Guarda un frame y su metadata."""
        # Nombre del archivo
        filename = f"frame_{index:04d}.jpg"
        filepath = self.output_dir / filename
        
        # Guardar imagen
        cv2.imwrite(str(filepath), frame, 
                   [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Metadata
        frame_data = {
            'index': index,
            'filename': filename,
            'filepath': str(filepath),
            'timestamp_ms': timestamp_ms,
            'timestamp_str': str(timedelta(milliseconds=int(timestamp_ms))),
            'gps': gps or {'lat': 0, 'lon': 0, 'alt': 0, 'speed': 0}
        }
        
        # Guardar JSON individual
        json_path = self.output_dir / f"frame_{index:04d}.json"
        with open(json_path, 'w') as f:
            json.dump(frame_data, f, indent=2)
        
        return frame_data
    
    def _save_metadata(self):
        """Guarda metadata general del proceso."""
        metadata = {
            'video_path': self.video_path,
            'distance_interval': self.distance_interval,
            'total_frames': len(self.frames_extracted),
            'total_distance': self.total_distance,
            'frames': self.frames_extracted,
            'extraction_time': datetime.now().isoformat()
        }
        
        with open(self.output_dir / 'extraction_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_equirectangular_info(self) -> Dict:
        """Retorna información sobre proyección equirectangular del video 360."""
        return {
            'projection': 'equirectangular',
            'projection_type': '360x180',
            'description': 'Video 360° en proyección equirectangular',
            'frame_size': (3840, 2160),  # Default 4K
            'note': 'Para street view, los frames se dividen en tiles'
        }


def extract_frames_from_video(
    video_path: str,
    output_dir: str = "./output_frames",
    distance_meters: int = 20,
    gps_data: Optional[Dict] = None
) -> List[Dict]:
    """
    Función de conveniencia para extraer frames.
    
    Uso:
    ----
    >>> frames = extract_frames_from_video(
    ...     video_path="video360.mp4",
    ...     output_dir="./frames",
    ...     distance_meters=20,
    ...     gps_data={'lat': [...], 'lon': [...], 'alt': [...], 'timestamps': [...]}
    ... )
    """
    extractor = Video360FrameExtractor(
        video_path=video_path,
        distance_interval=distance_meters,
        output_dir=output_dir,
        gps_data=gps_data
    )
    
    return extractor.extract_frames()


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python video_frame_extractor.py <video_path> [distancia_metros]")
        sys.exit(1)
    
    video = sys.argv[1]
    distancia = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    print(f"Extrayendo frames cada {distancia} metros...")
    frames = extract_frames_from_video(video, "./output_frames", distancia)
    print(f"¡Listo! {len(frames)} frames extraídos.")
