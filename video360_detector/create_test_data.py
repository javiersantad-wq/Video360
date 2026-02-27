"""
Generador de datos de prueba sintéticos
=======================================
Crea videos e imágenes de prueba para el pipeline.
"""

import os
import json
import numpy as np
from pathlib import Path


def create_test_video(output_path: str = "test_video.mp4", 
                      duration_sec: int = 10,
                      fps: int = 30):
    """
    Crea un video de prueba sintético.
    
    Nota: Requiere opencv-python instalado.
    """
    try:
        import cv2
        
        width, height = 1920, 1080
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame_num in range(duration_sec * fps):
            # Crear frame con gradiente y texto
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradiente de color
            for y in range(height):
                frame[y, :] = [int(255 * y / height), 100, 200]
            
            # Texto
            cv2.putText(frame, f"Frame {frame_num}", (100, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
            # Dibujar algunos rectángulos simulando objetos
            if frame_num % 90 == 0:  # Cada 3 segundos
                cv2.rectangle(frame, (400, 300), (600, 500), (0, 255, 0), 3)
            
            out.write(frame)
        
        out.release()
        print(f"✓ Video creado: {output_path}")
        return True
        
    except ImportError:
        print("✗ opencv-python no instalado")
        return False
    except Exception as e:
        print(f"✗ Error creando video: {e}")
        return False


def create_test_gps_data(output_path: str = "test_gps.json",
                        num_points: int = 100,
                        start_lat: float = 19.4326,
                        start_lon: float = -99.1332):
    """
    Crea datos GPS de prueba simulando un recorrido.
    """
    import math
    
    data = {
        'lat': [],
        'lon': [],
        'alt': [],
        'timestamps': [],
        'speed': []
    }
    
    # Simular recorrido serpenteante
    for i in range(num_points):
        t = i * 1000  # 1 segundo entre puntos
        lat = start_lat + (i * 0.0001) + math.sin(i * 0.1) * 0.00005
        lon = start_lon + (i * 0.0001) + math.cos(i * 0.1) * 0.00005
        alt = 2240 + i * 0.5 + math.sin(i * 0.2) * 5
        speed = 30 + 10 * math.sin(i * 0.15)
        
        data['lat'].append(round(lat, 7))
        data['lon'].append(round(lon, 7))
        data['alt'].append(round(alt, 2))
        data['timestamps'].append(int(t))
        data['speed'].append(round(speed, 1))
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ GPS data creado: {output_path}")
    print(f"  Puntos: {num_points}")
    print(f"  Lat: {data['lat'][0]:.6f} -> {data['lat'][-1]:.6f}")
    print(f"  Lon: {data['lon'][0]:.6f} -> {data['lon'][-1]:.6f}")
    
    return True


def create_test_frames(output_dir: str = "test_frames",
                      num_frames: int = 10):
    """
    Crea frames de imagen de prueba.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("✗ Pillow no instalado")
        return False
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for i in range(num_frames):
        # Crear imagen
        img = Image.new('RGB', (1920, 1080), color=(50, 100, 150))
        draw = ImageDraw.Draw(img)
        
        # Dibujar rectángulo simulando detección
        if i % 3 == 0:
            draw.rectangle([400, 300, 800, 700], outline='green', width=5)
            draw.text((450, 350), "CAR", fill='green')
        
        # Texto
        draw.text((100, 100), f"Frame {i}", fill='white')
        
        # Guardar
        filename = f"{output_dir}/frame_{i:04d}.jpg"
        img.save(filename, 'JPEG', quality=95)
        
        # Guardar metadata
        metadata = {
            'index': i,
            'filename': f"frame_{i:04d}.jpg",
            'filepath': filename,
            'timestamp_ms': i * 2000,
            'timestamp_str': f"00:00:{i*2:02d}",
            'gps': {
                'lat': 19.4326 + i * 0.0001,
                'lon': -99.1332 + i * 0.0001,
                'alt': 2240 + i * 0.5,
                'speed': 30
            }
        }
        
        with open(f"{output_dir}/frame_{i:04d}.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    # Metadata general
    frames = [json.load(open(f"{output_dir}/frame_{i:04d}.json")) for i in range(num_frames)]
    
    with open(f"{output_dir}/extraction_metadata.json", 'w') as f:
        json.dump({
            'video_path': 'test_video.mp4',
            'distance_interval': 20,
            'total_frames': num_frames,
            'total_distance': num_frames * 20,
            'frames': frames,
            'extraction_time': '2026-02-26T00:00:00'
        }, f, indent=2)
    
    print(f"✓ Frames de prueba creados: {num_frames}")
    return True


def create_test_detections(frames_dir: str = "test_frames",
                           output_path: str = "test_detections.json"):
    """
    Crea detecciones de prueba sintéticas.
    """
    detections = []
    
    for i in range(10):
        detections.append({
            'class_id': 2 if i % 2 == 0 else 0,  # car o person
            'class_name': 'car' if i % 2 == 0 else 'person',
            'confidence': 0.95 - (i * 0.05),
            'bbox': (400, 300, 800, 700),
            'center': (600, 500),
            'frame_index': i,
            'frame_path': f"{frames_dir}/frame_{i:04d}.jpg",
            'gps_position': {
                'lat': 19.4326 + i * 0.0001,
                'lon': -99.1332 + i * 0.0001,
                'alt': 2240 + i * 0.5
            },
            'geo_position': {
                'lat': 19.432608 + i * 0.0001,
                'lon': -99.133208 + i * 0.0001,
                'alt': 2240 + i * 0.5,
                'distance_m': 10.0,
                'bearing_deg': 45.0 + i * 10,
                'azimuth_pixel': 10.0,
                'elevation': 5.0
            },
            'crop_path': None,
            'timestamp_str': f"00:00:{i*2:02d}"
        })
    
    with open(output_path, 'w') as f:
        json.dump({
            'model': 'yolo11s.pt',
            'confidence': 0.25,
            'detection_radius': 10.0,
            'total_detections': len(detections),
            'detections': detections
        }, f, indent=2)
    
    print(f"✓ Detecciones de prueba creadas: {len(detections)}")
    return True


def run_full_test():
    """Crea todos los datos de prueba y ejecuta el pipeline."""
    print("=" * 60)
    print("🎥 CREANDO DATOS DE PRUEBA")
    print("=" * 60)
    
    # 1. Crear GPS data
    print("\n1. Creando datos GPS...")
    create_test_gps_data("test_gps.json")
    
    # 2. Crear video
    print("\n2. Creando video de prueba...")
    create_test_video("test_video.mp4", duration_sec=5)
    
    # 3. Crear frames
    print("\n3. Creando frames...")
    create_test_frames("test_frames", num_frames=10)
    
    # 4. Crear detecciones
    print("\n4. Creando detecciones...")
    create_test_detections("test_frames", "test_detections.json")
    
    print("\n" + "=" * 60)
    print("✓ DATOS DE PRUEBA CREADOS")
    print("=" * 60)
    print("\nArchivos creados:")
    for f in Path(".").glob("test_*"):
        if f.is_file():
            size = f.stat().st_size
            print(f"  - {f.name} ({size/1024:.1f} KB)")
    
    print("\nAhora puedes ejecutar:")
    print("  python main.py test_video.mp4 test_output --gps test_gps.json")
    print("  python test_all.py")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        run_full_test()
    else:
        print("Uso: python create_test_data.py --full")
        print("\nCrear datos individuales:")
        print("  python create_test_data.py --video")
        print("  python create_test_data.py --gps")
        print("  python create_test_data.py --frames")
