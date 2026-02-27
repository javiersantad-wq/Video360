# Video360 YOLO Detector para QGIS

Herramienta completa para procesar videos 360°, detectar objetos con YOLO y generar shapefiles georreferenciados.

## Características

- 🎥 **Extracción de frames** cada N metros (configurable)
- 🤖 **Detección YOLO** en tiempo real
- 📍 **Georreferenciación** de detecciones
- 🗺️ **Shapefiles** con puntos y buffers
- 🖼️ **Recortes** de cada detección
- 🌍 **Street View** visor HTML

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Instalar plugin en QGIS

**Opción A: Copiar a directorio de plugins**
```bash
cp -r video360_plugin ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

**Opción B: Zip para distribución**
```bash
zip -r video360_plugin.zip video360_plugin/
# En QGIS: Complementos > Instalar desde ZIP
```

## Uso

### Desde línea de comandos

```bash
# Básico
python video360_yolo_qgis.py --video tu_video.mp4 --gps tu_track.gpx

# Con opciones personalizadas
python video360_yolo_qgis.py \
  --video 360.mp4 \
  --gps track.gpx \
  --distance 10 \
  --model yolo11s \
  --confidence 0.3 \
  --output mi_output
```

### Parámetros

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--video` | Ruta al video 360° | **requerido** |
| `--gps` | Archivo GPX con track | opcional |
| `--distance` | Distancia entre frames (m) | 20 |
| `--radius` | Radio de detección (m) | 10 |
| `--model` | Modelo YOLO | yolo11n.pt |
| `--confidence` | Umbral de confianza | 0.25 |
| `--output` | Directorio de salida | output |
| `--step` | Paso (extract/detect/shapefile/all) | all |

### Modelos YOLO disponibles

- `yolo11n.pt` - Nano (más rápido)
- `yolo11s.pt` - Small (balanceado)
- `yolo11m.pt` - Medium
- `yolo11l.pt` - Large
- `yolo11x.pt` - XLarge (más preciso)

### Modo interactivo (QGIS)

1. Abre QGIS
2. Ve a **Complementos > Video360 YOLO Detector**
3. Selecciona el video y (opcional) el archivo GPX
4. Configura parámetros
5. Click en **Ejecutar**

## Estructura de salida

```
output/
├── frames/
│   ├── frame_0000.jpg
│   ├── frame_0001.jpg
│   ├── extraction_metadata.json
│   └── crops/
│       ├── crop_0000_car_0.85.jpg
│       └── ...
├── detections.json
└── shapefile/
    ├── detections_points.shp
    ├── detections_buffer.shp
    └── detections.geojson
```

## Street View

Para ver el visor Street View:

```bash
cd output
python -m http.server 8000
```

Luego abre: http://localhost:8000

## Hardware

- **CPU**: Funciona sin GPU (úsese modelo nano para velocidad)
- **GPU CUDA**: Opcional, acelera YOLO (~10x más rápido)

Para usar CUDA:
```bash
# Instalar versión con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## Problemas comunes

### YOLO no funciona
```bash
pip install ultralytics
```

### Error con shapefile
```bash
pip install geopandas shapely
```

### Video no se abre
- Verificar códec: `ffprobe video.mp4`
- Instalar códecs: `pip install av`

## Licencia

MIT License
