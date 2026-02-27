#!/usr/bin/env python3
"""
Video360 Detector - Pipeline Principal
=======================================
Extrae frames de video 360°, detecta objetos con YOLO, genera shapefiles
georreferenciados y crea un visor Street View.

Uso:
----
    python main.py video.mp4 [output_dir] [opciones]

Ejemplo:
--------
    python main.py video360.mp4 resultado --distance 20 --radius 10
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Video360 Detector - YOLO + GIS Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Básico
  python main.py video.mp4 output
  
  # Con opciones
  python main.py video.mp4 output -d 20 -r 10 --model yolo11s.pt
  
  # Solo extraer frames
  python main.py video.mp4 output --step extract
  
  # Solo detección
  python main.py video.mp4 output --step detect
  
  # Solo shapefile
  python main.py video.mp4 output --step shapefile
        """
    )
    
    # Argumentos posicionales
    parser.add_argument('video', help='Ruta al video 360°')
    parser.add_argument('output', nargs='?', default='output_video360',
                        help='Directorio de salida (default: output_video360)')
    
    # Opciones de extracción
    parser.add_argument('-d', '--distance', type=int, default=20,
                        help='Distancia entre frames en metros (default: 20)')
    
    # Opciones de detección
    parser.add_argument('-m', '--model', default='yolo11s.pt',
                        help='Modelo YOLO (default: yolo11s.pt)')
    parser.add_argument('-c', '--confidence', type=float, default=0.25,
                        help='Confianza mínima YOLO (default: 0.25)')
    parser.add_argument('-r', '--radius', type=float, default=10.0,
                        help='Radio de detección en metros (default: 10)')
    
    # Paso a ejecutar
    parser.add_argument('--step', choices=['extract', 'detect', 'shapefile', 
                                            'streetview', 'all'], 
                        default='all',
                        help='Paso a ejecutar (default: all)')
    
    # Opciones adicionales
    parser.add_argument('--gps', help='Archivo JSON con datos GPS')
    parser.add_argument('--no-crops', action='store_true',
                        help='No guardar recortes de detecciones')
    parser.add_argument('--no-streetview', action='store_true',
                        help='No crear visor Street View')
    parser.add_argument('--open', action='store_true',
                        help='Abrir visor Street View al terminar')
    
    args = parser.parse_args()
    
    # Validar video
    if not os.path.exists(args.video):
        print(f"❌ Error: Video no encontrado: {args.video}")
        sys.exit(1)
    
    # Crear directorio de salida
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🎥 Video360 Detector - Pipeline YOLO + GIS")
    print("=" * 60)
    print(f"📹 Video: {args.video}")
    print(f"📁 Output: {output_dir}")
    print(f"📏 Distancia: {args.distance}m")
    print(f"🎯 Modelo: {args.model}")
    print(f"📍 Radio: {args.radius}m")
    print("=" * 60)
    
    # Importar módulos
    from video_frame_extractor import Video360FrameExtractor
    from detector.yolo_detector import YOLODetector
    from shapefile_generator import ShapefileGenerator
    from streetview.street_view_generator import StreetViewHTMLGenerator
    
    results = {}
    frames = []
    detections = []
    
    # === EXTRACT ===
    if args.step in ['extract', 'all']:
        print("\n📼 Paso 1: Extrayendo frames...")
        
        # Cargar GPS si existe
        gps_data = None
        if args.gps and os.path.exists(args.gps):
            with open(args.gps) as f:
                gps_data = json.load(f)
            print(f"   → GPS cargado: {len(gps_data.get('lat', []))} puntos")
        
        extractor = Video360FrameExtractor(
            video_path=args.video,
            distance_interval=args.distance,
            output_dir=str(output_dir / 'frames'),
            gps_data=gps_data
        )
        
        frames = extractor.extract_frames()
        print(f"   ✅ {len(frames)} frames extraídos")
        
        if not frames:
            print("❌ Error: No se pudieron extraer frames")
            sys.exit(1)
    
    # === DETECT ===
    if args.step in ['detect', 'all']:
        print("\n🤖 Paso 2: Ejecutando YOLO...")
        
        # Buscar frames si no se extrajeron
        if not frames:
            metadata_path = output_dir / 'frames' / 'extraction_metadata.json'
            if metadata_path.exists():
                with open(metadata_path) as f:
                    data = json.load(f)
                    frames = data.get('frames', [])
        
        detector = YOLODetector(
            model_name=args.model,
            confidence=args.confidence,
            detection_radius=args.radius
        )
        
        metadata_path = output_dir / 'frames' / 'extraction_metadata.json'
        detections = detector.process_directory(
            str(output_dir / 'frames'),
            metadata_path=str(metadata_path) if metadata_path.exists() else None,
            save_crops=not args.no_crops
        )
        
        print(f"   ✅ {len(detections)} objetos detectados")
        
        # Guardar detecciones
        detector.save_detections_json(str(output_dir / 'detections.json'))
    
    # === SHAPEFILE ===
    if args.step in ['shapefile', 'all']:
        print("\n🗺️ Paso 3: Generando Shapefile...")
        
        # Cargar detecciones si no se tienen
        if not detections:
            detections_path = output_dir / 'detections.json'
            if detections_path.exists():
                with open(detections_path) as f:
                    data = json.load(f)
                    detections = data.get('detections', [])
        
        if detections:
            generator = ShapefileGenerator(
                output_dir=str(output_dir / 'shapefile'),
                detection_radius=args.radius
            )
            
            generator.add_detections(detections)
            results = generator.generate_all()
            
            summary = generator.get_summary()
            print(f"   ✅ {summary['total']} detecciones georreferenciadas")
            print(f"   📊 Por clase: {summary['by_class']}")
        else:
            print("   ⚠️ No hay detecciones para procesar")
    
    # === STREET VIEW ===
    if args.step in ['streetview', 'all'] and not args.no_streetview:
        print("\n🌐 Paso 4: Generando Street View...")
        
        streetview = StreetViewHTMLGenerator(
            output_path=str(output_dir / 'street_view' / 'index.html'),
            title="Video360 Street View"
        )
        
        # Cargar frames
        if not frames:
            metadata_path = output_dir / 'frames' / 'extraction_metadata.json'
            if metadata_path.exists():
                streetview.add_frames_from_metadata(str(metadata_path))
        
        if streetview.frames:
            streetview.generate()
            print(f"   ✅ Visor Street View creado ({len(streetview.frames)} frames)")
            
            if args.open:
                streetview.open_in_browser()
        else:
            print("   ⚠️ No hay frames para Street View")
    
    # === RESUMEN ===
    print("\n" + "=" * 60)
    print("📋 RESUMEN")
    print("=" * 60)
    print(f"📁 Directorio: {output_dir}")
    
    if frames:
        print(f"📼 Frames: {len(frames)}")
    if detections:
        print(f"🤖 Detecciones: {len(detections)}")
    
    print("\n📂 Archivos generados:")
    for item in output_dir.rglob('*'):
        if item.is_file() and not item.name.startswith('.'):
            size = item.stat().st_size
            size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/1024/1024:.1f}MB"
            print(f"   - {item.relative_to(output_dir)} ({size_str})")
    
    print("\n✅ ¡Proceso completado!")
    
    return output_dir


if __name__ == "__main__":
    main()
