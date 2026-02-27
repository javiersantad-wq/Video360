# Video360 Detector

Detector de objetos en video 360° usando YOLO con georreferenciación.

## Archivos en este repositorio

```
Video360/
├── real_output/
│   ├── detections.json          # Detecciones YOLO
│   ├── shapefile/              # Archivos GIS
│   │   ├── detections_points.shp
│   │   ├── detections_buffer.shp
│   │   └── detections.geojson
│   └── street_view/
│       └── index.html          # Visor Street View
├── real_gps.json               # Datos GPS del video
├── video360_detector/          # Codigo fuente
│   ├── main.py                 # Pipeline principal
│   ├── video_frame_extractor.py
│   ├── yolo_detector.py
│   ├── shapefile_generator.py
│   └── street_view_generator.py
```

## Street View

Para ver el Street View, sirve los archivos con un servidor HTTP:

```bash
cd Video360
python -m http.server 8000
```

Luego abre: http://localhost:8000/real_output/street_view/index.html

## Shapefiles

Los archivos GIS están en `real_output/shapefile/`:

- **detections_points.shp** - Puntos de detecciones
- **detections_buffer.shp** - Círculos de 10m alrededor de cada detección
- **detections.geojson** - Formato GeoJSON

## Detecciones

- **107 frames** (cada 20 metros)
- **870 detecciones** de objetos
- Coordenadas GPS para cada detección

## Ejecutar el pipeline

```bash
# Instalar dependencias
pip install -r video360_detector/requirements.txt

# Extraer frames
python main.py tu_video.mp4 output --distance 20 --gps tu_gps.json

# O solo una parte
python main.py tu_video.mp4 output --step extract   # Extraer frames
python main.py tu_video.mp4 output --step detect    # Ejecutar YOLO
python main.py tu_video.mp4 output --step shapefile # Crear shapefile
```
