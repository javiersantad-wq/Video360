"""
YOLODetector - Detección de objetos en frames de video 360
===========================================================
Utiliza YOLO para detectar objetos en frames extraídos y calcula
sus ubicaciones geográficas basándose en la posición del frame
y la dirección de la cámara.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math

# Intentar importar YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Advertencia: ultralytics no está instalado. Instalar con: pip install ultralytics")


@dataclass
class Detection:
    """Representa una detección de objeto."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    frame_index: int
    frame_path: str
    gps_position: Optional[Dict] = None
    geo_position: Optional[Dict] = None  # Lat, lon, alt
    crop_path: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'confidence': self.confidence,
            'bbox': self.bbox,
            'center': self.center,
            'frame_index': self.frame_index,
            'frame_path': self.frame_path,
            'gps_position': self.gps_position,
            'geo_position': self.geo_position,
            'crop_path': self.crop_path
        }


class CameraOrientation:
    """
    Estima la orientación de la cámara en un frame de video 360.
    En una proyección equirectangular, diferentes regiones del frame
    corresponden a diferentes direcciones.
    """
    
    # Mapeo de clases YOLO comunes a direcciones approximate
    # Esto es simplificado - en producción se usaría más datos
    ROAD_CLASSES = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 
                   5: 'bus', 7: 'truck'}
    
    def __init__(self, frame_width: int, frame_height: int):
        self.width = frame_width
        self.height = frame_height
        self.fov_horizontal = 360  # Video 360 completo
        self.fov_vertical = 180
    
    def pixel_to_direction(self, x: int, y: int) -> Tuple[float, float]:
        """
        Convierte coordenadas de pixel a dirección (azimuth, elevación).
        
        Returns:
            Tuple[azimuth, elevation] en grados
        """
        # Normalizar a [-1, 1]
        nx = (2 * x / self.width) - 1
        ny = (2 * y / self.height) - 1
        
        # Calcular ángulos
        azimuth = nx * (self.fov_horizontal / 2)
        elevation = ny * (self.fov_vertical / 2)
        
        return (azimuth, elevation)
    
    def estimate_camera_bearing(self, detections: List[Detection],
                                road_detection: bool = True) -> float:
        """
        Estima la orientación de la cámara basándose en detecciones.
        
        Asume que la mayoría de objetos están frente a la cámara.
        """
        if not detections or not road_detection:
            return 0.0  # Default: mirando al norte
        
        # Filtrar detecciones de "carretera" (vehículos, personas)
        road_objects = [d for d in detections 
                      if d.class_name in self.ROAD_CLASSES.values()]
        
        if not road_objects:
            return 0.0
        
        # Calcular azimuth promedio de los centros
        bearings = []
        for det in road_objects:
            az, _ = self.pixel_to_direction(det.center[0], det.center[1])
            bearings.append(az)
        
        # Retornar promedio (en radians)
        return np.radians(np.mean(bearings))
    
    def detection_to_geo(self, detection: Detection, 
                        frame_gps: Dict,
                        camera_bearing: float,
                        detection_distance: float = 10.0) -> Dict:
        """
        Convierte una detección a coordenadas geográficas.
        
        Parámetros:
        -----------
        detection : Detection
            La detección con posición en pixel
        frame_gps : Dict
            Posición GPS del frame (lat, lon, alt)
        camera_bearing : float
            Bearing de la cámara en radians
        detection_distance : float
            Distancia estimada del objeto en metros
            
        Returns:
        --------
        Dict con lat, lon, alt del objeto detectado
        """
        # Obtener dirección del objeto
        az, el = self.pixel_to_direction(
            detection.center[0], 
            detection.center[1]
        )
        
        # Bearing total del objeto
        obj_bearing = camera_bearing + np.radians(az)
        
        # Distancia del objeto (estimada o configurable)
        distance = detection_distance
        
        # Calcular nueva posición
        R = 6371000  # Radio terrestre en metros
        lat1 = np.radians(frame_gps['lat'])
        lon1 = np.radians(frame_gps['lon'])
        
        # Nueva posición
        lat2 = np.arcsin(
            np.sin(lat1) * np.cos(distance/R) +
            np.cos(lat1) * np.sin(distance/R) * np.cos(obj_bearing)
        )
        
        lon2 = lon1 + np.arctan2(
            np.sin(obj_bearing) * np.sin(distance/R) * np.cos(lat1),
            np.cos(distance/R) - np.sin(lat1) * np.sin(lat2)
        )
        
        return {
            'lat': np.degrees(lat2),
            'lon': np.degrees(lon2),
            'alt': frame_gps.get('alt', 0),
            'distance_m': distance,
            'bearing_deg': np.degrees(obj_bearing),
            'azimuth_pixel': az,
            'elevation': el
        }


class YOLODetector:
    """
    Detector de objetos usando YOLO.
    
    Parámetros:
    -----------
    model_name : str
        Nombre del modelo YOLO (default: 'yolo11n.pt')
    confidence : float
        Umbral de confianza (default: 0.25)
    detection_radius : float
        Radio máximo de detección en metros (default: 10)
    """
    
    # Nombres de clases COCO estándar
    COCO_CLASSES = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle',
        4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat',
        9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign',
        12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat',
        16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant',
        21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack',
        25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase',
        29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball',
        33: 'kite', 34: 'baseball bat', 35: 'baseball glove',
        36: 'skateboard', 37: 'surfboard', 38: 'tennis racket',
        39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork',
        43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple',
        48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot',
        52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
        56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
        60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop',
        64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone',
        68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink',
        72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase',
        76: 'scissors', 77: 'teddy bear', 78: 'hair drier',
        79: 'toothbrush'
    }
    
    def __init__(self, 
                 model_name: str = "yolo11n.pt",
                 confidence: float = 0.25,
                 detection_radius: float = 10.0):
        
        if not YOLO_AVAILABLE:
            raise ImportError("YOLO no está disponible. Instalar: pip install ultralytics")
        
        self.model_name = model_name
        self.confidence = confidence
        self.detection_radius = detection_radius
        
        # Cargar modelo
        print(f"Cargando modelo YOLO: {model_name}...")
        self.model = YOLO(model_name)
        print("Modelo cargado.")
        
        self.camera_orientation = None
        self.detections_all: List[Detection] = []
    
    def process_frame(self, 
                     frame_path: str,
                     frame_gps: Optional[Dict] = None,
                     frame_index: int = 0,
                     save_crops: bool = True,
                     crops_dir: Optional[Path] = None) -> List[Detection]:
        """
        Procesa un frame y detecta objetos.
        
        Parámetros:
        -----------
        frame_path : str
            Ruta al frame/imagen
        frame_gps : Dict, optional
            Coordenadas GPS del frame
        frame_index : int
            Índice del frame
        save_crops : bool
            Si True, guarda recortes de detecciones
        crops_dir : Path, optional
            Directorio para guardar crops
            
        Returns:
        --------
        List[Detection]: Lista de detecciones
        """
        # Cargar imagen
        image = cv2.imread(frame_path)
        if image is None:
            print(f"Error cargando imagen: {frame_path}")
            return []
        
        if self.camera_orientation is None:
            h, w = image.shape[:2]
            self.camera_orientation = CameraOrientation(w, h)
        
        # Ejecutar detección
        results = self.model(image, conf=self.confidence, verbose=False)
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extraer datos
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Centro del bbox
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                detection = Detection(
                    class_id=cls,
                    class_name=self.COCO_CLASSES.get(cls, f'class_{cls}'),
                    confidence=conf,
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    center=(cx, cy),
                    frame_index=frame_index,
                    frame_path=frame_path,
                    gps_position=frame_gps
                )
                
                # Calcular posición geográfica
                if frame_gps:
                    camera_bearing = self.camera_orientation.estimate_camera_bearing(
                        [detection]
                    )
                    geo = self.camera_orientation.detection_to_geo(
                        detection, frame_gps, camera_bearing, 
                        self.detection_radius
                    )
                    detection.geo_position = geo
                
                # Guardar crop
                if save_crops:
                    crop = self._save_crop(image, detection, crops_dir)
                    detection.crop_path = crop
                
                detections.append(detection)
                self.detections_all.append(detection)
        
        return detections
    
    def _save_crop(self, 
                   image: np.ndarray, 
                   detection: Detection,
                   crops_dir: Optional[Path] = None) -> Optional[str]:
        """Guarda el recorte de una detección."""
        if crops_dir is None:
            crops_dir = Path(detection.frame_path).parent / 'crops'
        
        crops_dir = Path(crops_dir)
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        x1, y1, x2, y2 = detection.bbox
        
        # Asegurar que estén dentro de la imagen
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        # Extraer crop
        crop = image[y1:y2, x1:x2]
        
        # Nombre del archivo
        filename = f"crop_{detection.frame_index:04d}_{detection.class_name}_{detection.confidence:.2f}.jpg"
        filepath = crops_dir / filename
        
        # Guardar
        cv2.imwrite(str(filepath), crop)
        
        return str(filepath)
    
    def process_directory(self, 
                         frames_dir: str,
                         metadata_path: Optional[str] = None,
                         save_crops: bool = True) -> List[Detection]:
        """
        Procesa todos los frames en un directorio.
        
        Parámetros:
        -----------
        frames_dir : str
            Directorio con frames
        metadata_path : str, optional
            Ruta al archivo metadata de extracción
        save_crops : bool
            Si True, guarda recortes
             
        Returns:
        --------
        List[Detection]: Todas las detecciones
        """
        frames_dir = Path(frames_dir)
        
        # Cargar metadata
        frames_info = []
        if metadata_path:
            with open(metadata_path) as f:
                data = json.load(f)
                frames_info = data.get('frames', [])
        
        # Encontrar todos los frames
        frame_files = sorted(frames_dir.glob("frame_*.jpg"))
        
        all_detections = []
        
        for i, frame_file in enumerate(frame_files):
            print(f"Procesando: {frame_file.name}")
            
            # Obtener GPS del frame
            frame_gps = None
            if frames_info and i < len(frames_info):
                frame_gps = frames_info[i].get('gps')
            
            detections = self.process_frame(
                str(frame_file),
                frame_gps=frame_gps,
                frame_index=i,
                save_crops=save_crops
            )
            
            all_detections.extend(detections)
            print(f"  -> {len(detections)} detecciones")
        
        return all_detections
    
    def save_detections_json(self, output_path: str):
        """Guarda todas las detecciones en JSON."""
        data = {
            'model': self.model_name,
            'confidence': self.confidence,
            'detection_radius': self.detection_radius,
            'total_detections': len(self.detections_all),
            'detections': [d.to_dict() for d in self.detections_all]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Guardado: {output_path}")


def detect_objects(
    frames_dir: str,
    output_dir: str = "./detections",
    model: str = "yolo11n.pt",
    confidence: float = 0.25,
    detection_radius: float = 10.0,
    save_crops: bool = True
) -> List[Dict]:
    """
    Función de conveniencia para detección.
    
    Uso:
    ----
    >>> detections = detect_objects(
    ...     frames_dir="./frames",
    ...     output_dir="./detections",
    ...     model="yolo11s.pt",  # Modelo más grande
    ...     confidence=0.3,
    ...     detection_radius=10.0
    ... )
    """
    os.makedirs(output_dir, exist_ok=True)
    
    detector = YOLODetector(
        model_name=model,
        confidence=confidence,
        detection_radius=detection_radius
    )
    
    all_detections = detector.process_directory(
        frames_dir,
        save_crops=save_crops
    )
    
    # Guardar
    detector.save_detections_json(f"{output_dir}/detections.json")
    
    return [d.to_dict() for d in all_detections]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python yolo_detector.py <frames_dir> [output_dir]")
        sys.exit(1)
    
    frames = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "./detections"
    
    detect_objects(frames, output)
