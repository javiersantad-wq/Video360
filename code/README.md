# 🎥 Video360 Detector

Plugin de QGIS para procesar videos 360°, detectar objetos con YOLO y generar shapefiles georreferenciados.

## 🚀 Características

- **Extracción de frames**: Extrae frames cada N metros (configurable, default 20m)
- **Detección YOLO**: Detecta objetos en tiempo real con YOLOv11
- **Georreferenciación**: Calcula coordenadas GPS de cada detección
- **Shapefile**: Genera archivos SHP con puntos y buffers (10m radio)
- **Recortes**: Guarda imágenes recortadas de cada detección
- **Street View**: Visor HTML interactivo tipo Street View
- **Mapillary**: Prepara datos para subir a Mapillary

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Instalar plugin en QGIS

**Opción A: Instalación local**
```bash
# Copiar a directorio de plugins de QGIS
cp -r video360_detector ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

**Opción B: Zip para distribución**
```bash
# Crear archivo ZIP del directorio
zip -r video360_detector.zip video360_detector/
# En QGIS: Plugins > Install from ZIP
```

## 🎯 Uso

### Desde QGIS (Plugin)

1. Abrir QGIS
2. Ir a **Complementos > Video360 Detector**
3. Seleccionar video 360°
4. Configurar parámetros
5. Click en **Ejecutar Todo**

### Desde Línea de Comandos

```bash
# Uso básico
python main.py video.mp4 resultado

# Con opciones personalizadas
python main.py video.mp4 resultado \
  --distance 20 \
  --radius 10 \
  --model yolo11s.pt \
  --confidence 0.3

# Solo un paso
python main.py video.mp4 output --step extract   # Extraer frames
python main.py video.mp4 output --step detect     # Solo YOLO
python main.py video.mp4 output --step shapefile  # Solo shapefile
```

## 📋 Parámetros

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `video` | Ruta al video 360° | - |
| `output` | Directorio de salida | `output_video360` |
| `-d, --distance` | Distancia entre frames (m) | 20 |
| `-r, --radius` | Radio de detección (m) | 10 |
| `-m, --model` | Modelo YOLO | `yolo11s.pt` |
| `-c, --confidence` | Umbral de confianza | 0.25 |

### Modelos YOLO disponibles

- `yolo11n.pt` - Nano (más rápido)
- `yolo11s.pt` - Small (balanceado)
- `yolo11m.pt` - Medium
- `yolo11l.pt` - Large
- `yolo11x.pt` - XLarge (más preciso)

## 📁 Estructura de Salida

```
output_video360/
├── frames/                    # Frames extraídos
│   ├── frame_0000.jpg
│   ├── frame_0000.json
│   ├── frame_0001.jpg
│   └── extraction_metadata.json
├── detections/
│   └── detections.json       # Todas las detecciones
├── shapefile/                # Archivos GIS
│   ├── detections_points.shp
│   ├── detections_points.shx
│   ├── detections_points.dbf
│   ├── detections_buffer.shp
│   └── detections.geojson
├── street_view/              # Visor interactivo
│   ├── index.html
│   └── frames/
└── detections.json           # Detecciones finales
```

## 🔧 Formato de GPS (opcional)

Si tienes un archivo GPS externo:

```json
{
  "lat": [19.4326, 19.4327, 19.4328],
  "lon": [-99.1332, -99.1331, -99.1330],
  "alt": [2240, 2242, 2245],
  "timestamps": [0, 1000, 2000],
  "speed": [30, 32, 28]
}
```

## 🌐 Street View

El visor HTML generado permite:
- Navegar entre frames con botones o flechas
- Arrastrar para rotar la vista
- Ver coordenadas GPS de cada frame

Para abrirlo:
```bash
# Abrir en navegador
python -m http.server 8000
# Luego ir a http://localhost:8000/output/street_view/
```

## 📤 GitHub

Subir resultados a GitHub:

```bash
python -c "
from github.github_uploader import upload_to_github
upload_to_github([
    'output/shapefile/detections.shp',
    'output/shapefile/detections.geojson',
    'output/detections.json'
], commit_message='Nuevas detecciones')
```

## 🐛 Solución de Problemas

**YOLO no funciona**
```bash
pip install ultralytics
```

**Error con shapefile**
```bash
pip install geopandas shapely
```

**Video no se abre**
- Verificar códec: `ffprobe video.mp4`
- Instalar códecs: `pip install av`

## 📝 Licencia

MIT License

## 👤 Autor

Video360 Detector Team
