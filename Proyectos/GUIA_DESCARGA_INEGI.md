# Guía de Descarga de Datos INEGI y Red Geodésica

## Contenido

1. Datos INEGI a Descargar
2. Red Geodésica Nacional
3. Instrucciones de Descarga Paso a Paso
4. Archivos a Descargar por Proyecto
5. Cómo Montar en ArcMap

---

## 1. DATOS INEGI A DESCARGAR

### 1.1 Marco Geoestadístico Nacional

El Marco Geoestadístico contiene la información geográfica oficial de México.

**Sitio web:** https://www.inegi.org.mx/geo/

**Archivos a descargar (shapefile):**

| Archivo | Descripción | Para qué sirve |
|---------|------------|---------------|
| `00_ENT.shp` | Estados de México | Referencia de límites estatales |
| `00_MUN.shp` | Municipios | Límites municipales |
| `00_LOC.shp` | Localidades | Puntos de ciudades/pueblos con población |
| `00_AGEB_URB.shp` | AGEB Urbanas | Polígonos de áreas urbanas |
| `00_MANZ.shp` | Manzanas | Polígonos de manzanas urbanas |
| `00_EJIDO.shp` | Ejidos | Polígonos de predios ejidales (ya tenemos dato similar) |

**Estados que cubren los proyectos:**

| Estado | CVE INEGI | Proyectos |
|--------|-----------|-----------|
| Tamaulipas | 28 | Ambos |
| San Luis Potosí | 24 | Tampico-San Luis |
| Veracruz | 30 | Veracruz-Tampico |

### 1.2 Datos Específicos por Proyecto

#### PARA TAMPICO - SAN LUIS POTOSÍ

**Bounding box:**
- West: -100.95°
- South: 21.85°
- East: -97.87°
- North: 22.28°

**Municipios principales:**
- Tamaulipas: Aldama, Güémez, San Fernando, Valle Hermoso, Río Bravo, Tampico, Ciudad Madero
- San Luis Potosí: Ciudad Valles, Tamazunchale, Ébano, San Vicente

#### PARA VERACRUZ - TAMPICO

**Bounding box:**
- West: -97.95°
- South: 19.14°
- East: -96.22°
- North: 22.28°

**Municipios principales:**
- Tamaulipas: Tampico, Ciudad Madero, San Fernando, Méndez, Burgos, Cruillas, San Carlos
- Veracruz: Veracruz, Boca del Río, Martínez de la Torre, Tlapacoyan

---

## 2. RED GEODÉSICA NACIONAL

La Red Geodésica proporciona puntos de control con coordenadas precisas.

### 2.1 ¿Qué es?

Es una red de puntos monumentados en todo México con coordenadas en:
- **WGS84** (GPS)
- **ITRF92/ITRF08** (Marco internacional)
- **datum oficial mexicano**

### 2.2 Puntos Disponibles

**Estaciones Permanentes GNSS (EPGN)**
- Son estaciones GPS/GLONASS en tiempo real
- Altamente precisas (mm)
- Algunas son públicas y gratuitas

**Red Nacional de Geodésia Activa (RNA)**

| Estación | Ubicación | Coordenadas Aproximadas |
|----------|-----------|------------------------|
| TAMP | Tampico, Tamps | 22.20°N, -97.85°W |
| VERAC | Veracruz, Ver | 19.20°N, -96.10°W |
| SLPI | San Luis Potosí | 22.15°N, -100.90°W |

### 2.3 Cómo Descargar Puntos

**Sitio:** https://www.inegi.org.mx/geo/

**Buscar:** "Red Geodésica" o "Datos Geodésicos"

**Formato de entrega:**
- CSV con coordenadas
- Shapefile de monument os
- RINEX (para procesamiento GPS avanzado)

### 2.4 Alternativa: Servicio de Posicionamiento

El INEGI ofrece el servicio **MEXICO-GPS**:
- Corrección en tiempo real vía internet
- Precisión: 2-5 cm horizontal
- Requiere registro gratuito

**URL:** https://www.inegi.org.mx/geo/mexico_gps/

---

## 3. INSTRUCCIONES DE DESCARGA PASO A PASO

### 3.1 Marco Geoestadístico

**Paso 1:** Ir a https://www.inegi.org.mx/geo/

**Paso 2:** Buscar el menú "Descargas" o "Productos"

**Paso 3:** Seleccionar "Marco Geoestadístico"

**Paso 4:** Elegir la versión más reciente (2024 o 2025)

**Paso 5:** Seleccionar el nivel "Estatal" o "Nacional"

**Paso 6:** Filtrar por estados:
- Tamaulipas (código 28)
- San Luis Potosí (código 24)
- Veracruz (código 30)

**Paso 7:** Descargar en formato ZIP (shapefile)

**Paso 8:** Extraer en la carpeta `datos_inegi/` del proyecto

### 3.2 Red Geodésica

**Paso 1:** Ir a https://www.inegi.org.mx/geo/

**Paso 2:** Buscar "Geodésia" o "Datos Geodésicos"

**Paso 3:** Descargar:
- Estaciones Permanentes (EPGN) - archivo CSV
- Monumentos de la Red Pasiva - shapefile

**Paso 4:** Filtrar por área de interés usando el bounding box

### 3.3 Datos Elevación (DEM)

**Importante para corrección de altura:**

| Producto | Resolución | URL |
|----------|------------|-----|
| Modelo Digital de Elevación (MDE) | 30m | Descargar desde INEGI |
| ASTER DEM | 30m | Alternativa gratuita |
| SRTM | 30m | Alternativa gratuita |

**Usar para:**
- Corrección de altura de datos LiDAR
- Generación de modelos de terreno
- Análisis topográfico

---

## 4. ARCHIVOS A DESCARGAR POR PROYECTO

### 4.1 Estructura de Carpetas Sugerida

```
Proyectos/
├── datos_inegi/
│   ├── marco_geografico/
│   │   ├── 00_ENT.shp (Estados)
│   │   ├── 00_MUN.shp (Municipios)
│   │   ├── 00_LOC.shp (Localidades)
│   │   ├── 00_AGEB_URB.shp (AGEB urbanas)
│   │   └── 00_MANZ.shp (Manzanas)
│   ├── red_geodesica/
│   │   ├── estaciones_permanentes.csv
│   │   └── monumentos.shp
│   └── dem/
│       └── mde_tamps_slp_ver.tif
│
├── Tampico_SanLuis/
│   └── datos/
│       └── (archivos existentes)
│
└── Veracruz_Tampico/
    └── datos/
        └── (archivos existentes)
```

### 4.2 Archivos a Descargar

| # | Archivo | Tamaño Aprox | Prioridad |
|---|---------|--------------|-----------|
| 1 | Estados (00_ENT.shp) | 1 MB | Alta |
| 2 | Municipios (00_MUN.shp) | 5 MB | Alta |
| 3 | Localidades (00_LOC.shp) | 50 MB | Alta |
| 4 | AGEB Urbanas (00_AGEB_URB.shp) | 200 MB | Media |
| 5 | Manzanas (00_MANZ.shp) | 500 MB | Baja |
| 6 | Estaciones GPS (EPGN) | 1 MB | Alta |
| 7 | Monumentos Red Geodésica | 10 MB | Media |
| 8 | MDE 30m | 100 MB | Alta |

**Total estimado:** ~1 GB

---

## 5. CÓMO MONTAR EN ARCMAP

### 5.1 Agregar Shapefiles

**Paso 1:** Abrir ArcMap

**Paso 2:** Ir a "Catalog" (ventana lateral o menú)

**Paso 3:** Navegar a la carpeta del proyecto:
```
C:\Users\ed\.openclaw\workspace\Proyectos\
```

**Paso 4:** Arrastrar folders al mapa

### 5.2 Capas a Agregar (en orden)

**Para cada proyecto, agregar en este orden:**

```
1. Estados (referencia)
   → datos_inegi/marco_geografico/00_ENT.shp

2. Municipios (referencia)
   → datos_inegi/marco_geografico/00_MUN.shp

3. Corredor del proyecto (principal)
   → Tampico_SanLuis/datos/Tampico_SanLuis-50km_blocks.shp
   → Veracruz_Tampico/datos/Veracruz-Tampico-50km_blocks_v4.shp

4. Líneas de vuelo sugeridas
   → Tampico_SanLuis/datos/Tampico_SanLuis_flight_lines.shp
   → Veracruz_Tampico/datos/Veracruz_Tampico_flight_lines.shp

5. Ejidos cercanos
   → Tampico_SanLuis/analisis/ejidos_Tampico_SanLuis.geojson
   → Veracruz_Tampico/analisis/ejidos_Veracruz_Tampico.geojson

6. Localidades OSM
   → Tampico_SanLuis/datos/localidades_osm.shp
   → Veracruz_Tampico/datos/localidades_osm.shp

7. Localidades INEGI (después de descargar)
   → datos_inegi/marco_geografico/00_LOC.shp

8. AGEB Urbanas (después de descargar)
   → datos_inegi/marco_geografico/00_AGEB_URB.shp
```

### 5.3 Configuración de Simbología

**Corredor:** Línea gruesa, color azul

**Flight lines:** Línea punteada, color verde

**Ejidos:** Polígono sin relleno, borde rojo, transparencia 50%

**Localidades:** Símbolo de punto, tamaño según tipo (ciudad=grande, pueblo=mediano, hamlet=chico)

### 5.4 Definir SRC

**Todos los archivos están en WGS84 (EPSG:4326)**

Para verificar/cambiar:
1. Click derecho en capa → Properties → Source
2. Verificar que Coordinate System sea "GCS_WGS_1984"

---

## 6. RESUMEN DE UBICACIÓN DE ARCHIVOS

### Workspace Principal
```
C:\Users\ed\.openclaw\workspace\Proyectos\
```

### Archivos por Proyecto

#### Proyecto Tampico - San Luis Potosí
```
C:\Users\ed\.openclaw\workspace\Proyectos\Tampico_SanLuis\
├── ANALISIS_DEL_PROYECTO.docx          ← Reporte Word
├── README.md                             ← Documentación
├── PROYECTO.md                           ← Descripción
├── datos/
│   ├── Tampico_SanLuis-50km_blocks.shp  ← CORREDOR (principal)
│   ├── localidades_osm.shp               ← Localidades OSM
│   ├── Tampico_SanLuis_flight_lines.shp ← Líneas de vuelo
│   └── Tampico_SanLuis_flight_summary.csv
└── analisis/
    ├── ejidos_Tampico_SanLuis.csv
    ├── ejidos_Tampico_SanLuis.geojson
    └── localidades_cercanas.csv
```

#### Proyecto Veracruz - Tampico
```
C:\Users\ed\.openclaw\workspace\Proyectos\Veracruz_Tampico\
├── ANALISIS_DEL_PROYECTO.docx                  ← Reporte Word
├── README.md                                   ← Documentación
├── PROYECTO.md                                 ← Descripción
├── datos/
│   ├── Veracruz-Tampico-50km_blocks_v4.shp     ← CORREDOR (principal)
│   ├── localidades_osm.shp                     ← Localidades OSM
│   ├── Veracruz_Tampico_flight_lines.geojson   ← Líneas de vuelo
│   └── Veracruz_Tampico_flight_summary.csv
└── analisis/
    ├── ejidos_Veracruz_Tampico.csv
    ├── ejidos_Veracruz_Tampico.geojson
    └── localidades_cercanas.csv
```

#### Archivos Generales
```
C:\Users\ed\.openclaw\workspace\Proyectos\
├── PLAN_LEVANTAMIENTO_DRONE_LIDAR.md   ← Plan completo
├── REPORTE_ANALISIS_SOCIAL.md          ← Análisis social
├── GUIA_DESCARGA_INEGI.md              ← Este documento
├── datos_inegi/                        ← Carpeta para datos INEGI (vacía)
│   └── INSTRUCCIONES_DESCARGA_INEGI.txt
└── *.py                                ← Scripts de generación
```

---

## 7. PRÓXIMOS PASOS

1. [ ] Descargar Marco Geoestadístico de INEGI
2. [ ] Descargar Red Geodésica
3. [ ] Descargar DEM (Modelo Digital de Elevación)
4. [ ] Extraer archivos en `datos_inegi/`
5. [ ] Agregar capas en ArcMap
6. [ ] Configurar simbología
7. [ ] Definir áreas de trabajo específicas

---

*Documento generado automáticamente - 2026-03-23*
