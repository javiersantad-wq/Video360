"""
Script de validacion para Video360 Detector
"""
import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix UTF-8
sys.stdout.reconfigure(encoding='utf-8')


def test_imports():
    print("=" * 50)
    print("TEST 1: Importando modulos...")
    print("=" * 50)
    
    errors = []
    
    # Core modules
    try:
        import cv2
        print(f"OK opencv-python: {cv2.__version__}")
    except ImportError as e:
        errors.append(f"ERROR opencv-python: {e}")
        print(f"ERROR opencv-python: {e}")
    
    try:
        import numpy as np
        print(f"OK numpy: {np.__version__}")
    except ImportError as e:
        errors.append(f"ERROR numpy: {e}")
        print(f"ERROR numpy: {e}")
    
    try:
        import json
        print("OK json (stdlib)")
    except ImportError as e:
        errors.append(f"ERROR json: {e}")
    
    # Optional GIS modules
    try:
        import geopandas as gpd
        print(f"OK geopandas: {gpd.__version__}")
    except ImportError as e:
        print(f"WARN geopandas (opcional): {e}")
    
    try:
        from shapely.geometry import Point
        print("OK shapely")
    except ImportError as e:
        print(f"WARN shapely (opcional): {e}")
    
    # YOLO
    try:
        from ultralytics import YOLO
        print("OK ultralytics (YOLO)")
    except ImportError as e:
        print(f"WARN ultralytics (opcional): {e}")
    
    # PIL
    try:
        from PIL import Image
        print(f"OK Pillow: {Image.__version__}")
    except ImportError as e:
        print(f"WARN Pillow (opcional): {e}")
    
    if errors:
        print("\nERRORES EN IMPORTS:")
        for e in errors:
            print(f"  {e}")
        return False
    
    print("\nTodos los modulos requeridos instalados")
    return True


def test_video_frame_extractor():
    print("\n" + "=" * 50)
    print("TEST 2: VideoFrameExtractor")
    print("=" * 50)
    
    try:
        from video_frame_extractor import Video360FrameExtractor, GPSMetadata
        
        # Test GPS interpolation
        gps = GPSMetadata()
        gps.add_waypoint(19.4326, -99.1332, 2240, 0, 30)
        gps.add_waypoint(19.4327, -99.1331, 2242, 1000, 32)
        
        interpolated = gps.interpolate(500)
        
        if interpolated:
            print(f"OK GPS interpolation: {interpolated['lat']:.6f}, {interpolated['lon']:.6f}")
        
        # Test distance calculation
        dist = gps.calculate_distance(
            {'lat': 19.4326, 'lon': -99.1332},
            {'lat': 19.4327, 'lon': -99.1331}
        )
        print(f"OK Distance calculation: {dist:.2f} m")
        
        # Test extractor creation
        extractor = Video360FrameExtractor(
            video_path="test.mp4",
            distance_interval=20,
            output_dir="./test_output"
        )
        print("OK VideoFrameExtractor creado")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yolo_detector():
    print("\n" + "=" * 50)
    print("TEST 3: YOLODetector")
    print("=" * 50)
    
    try:
        from detector.yolo_detector import YOLODetector, CameraOrientation
        
        # Test camera orientation
        cam = CameraOrientation(1920, 1080)
        az, el = cam.pixel_to_direction(960, 540)
        print(f"OK Camera orientation (center): azimuth={az:.2f} deg, elevation={el:.2f} deg")
        
        # Test geo conversion
        geo = cam.detection_to_geo(
            type('obj', (object,), {
                'center': (960, 540),
                'bbox': (800, 400, 1120, 800),
                'class_name': 'car',
                'confidence': 0.9
            })(),
            {'lat': 19.4326, 'lon': -99.1332, 'alt': 2240},
            0.0,  # bearing
            10.0  # distance
        )
        print(f"OK Geo conversion: lat={geo['lat']:.6f}, lon={geo['lon']:.6f}")
        
        print("OK YOLODetector modulo cargado")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shapefile_generator():
    print("\n" + "=" * 50)
    print("TEST 4: ShapefileGenerator")
    print("=" * 50)
    
    try:
        try:
            from shapefile_generator import ShapefileGenerator
            has_geopandas = True
        except ImportError:
            print("WARN geopandas no disponible")
            has_geopandas = False
        
        if has_geopandas:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                gen = ShapefileGenerator(
                    output_dir=tmpdir,
                    detection_radius=10.0
                )
                
                test_detection = {
                    'class_id': 2,
                    'class_name': 'car',
                    'confidence': 0.95,
                    'bbox': (100, 100, 200, 200),
                    'center': (150, 150),
                    'frame_index': 0,
                    'frame_path': '/test/frame_0000.jpg',
                    'geo_position': {
                        'lat': 19.4326,
                        'lon': -99.1332,
                        'alt': 2240,
                        'distance_m': 10.0,
                        'bearing_deg': 45.0
                    },
                    'crop_path': None
                }
                
                gen.add_detection(test_detection)
                print(f"OK Added detection: {test_detection['class_name']}")
                
                summary = gen.get_summary()
                print(f"OK Summary: {summary}")
                
                print("OK ShapefileGenerator funcionando")
        else:
            print("WARN ShapefileGenerator requiere geopandas")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_street_view():
    print("\n" + "=" * 50)
    print("TEST 5: StreetViewGenerator")
    print("=" * 50)
    
    try:
        from streetview.street_view_generator import StreetViewHTMLGenerator
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = StreetViewHTMLGenerator(
                output_path=f"{tmpdir}/test_streetview.html",
                title="Test Street View"
            )
            
            gen.add_frame(
                image_path="/test/frame.jpg",
                gps={'lat': 19.4326, 'lon': -99.1332, 'alt': 2240},
                frame_index=0
            )
            
            print(f"OK Added frame: lat={gen.frames[0]['lat']:.6f}")
            
            output = gen.generate()
            print(f"OK Generated: {output}")
            
            return True
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_github_uploader():
    print("\n" + "=" * 50)
    print("TEST 6: GitHubUploader")
    print("=" * 50)
    
    try:
        from github.github_uploader import GitHubUploader
        
        uploader = GitHubUploader(
            repo_path=".",
            commit_message="Test commit"
        )
        
        print("OK GitHubUploader creado")
        print("  (Requiere GITHUB_TOKEN para hacer push)")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_cli():
    print("\n" + "=" * 50)
    print("TEST 7: Main CLI")
    print("=" * 50)
    
    try:
        import main
        
        print("OK main.py cargado correctamente")
        
        if hasattr(main, 'main'):
            print("OK funcion main() existe")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    print("\n" + "=" * 60)
    print("VIDEO360 DETECTOR - SUITE DE PRUEBAS")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("VideoFrameExtractor", test_video_frame_extractor()))
    results.append(("YOLODetector", test_yolo_detector()))
    results.append(("ShapefileGenerator", test_shapefile_generator()))
    results.append(("StreetViewGenerator", test_street_view()))
    results.append(("GitHubUploader", test_github_uploader()))
    results.append(("Main CLI", test_main_cli()))
    
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\nTodas las pruebas pasaron!")
        return 0
    else:
        print(f"\n{failed} pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
