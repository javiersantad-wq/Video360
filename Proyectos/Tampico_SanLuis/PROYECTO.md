# Proyecto: Tampico - San Luis Potosí

## Descripción
Corredor de canalización para infraestructura de telecomunicacion/vía de alta tensión
- **Bloques:** 45 segmentos
- **Longitud total:** ~300+ km
- **Extensión:** Desde Tampico, Tamaulipas hasta San Luis Potosí

## Tipos de Trabajo Identificados
- Canalización minicepa
- Canalización tipo A
- Canalización piedra bola
- Postes CFE

## Estructura de Carpetas

```
Tampico_SanLuis/
├── datos/                    # Archivos originales y procesados
│   ├── *.shp, *.shx, etc.   # Shapefile del corredor
│   └── (agregar aquí datos adicionales)
├── analisis/                 # Análisis específicos del proyecto
│   └── (agregar aquí análisis adicionales)
└── README.md                 # Este archivo
```

## Datos Geográficos
- **CRS:** EPSG:4326 (WGS84)
- **Tipo de geometría:** LineString Z (líneas 3D)
- **Fecha de datos:** 2026-03-20

## Ejidos Cercanos (2km buffer)
- **Total:** 160 ejidos
- **Estados:** San Luis Potosí (130), Tamaulipas (30)
- **Municipios principales:** Aldama, Güémez, San Fernando

## Archivos Generados
- `../analisis_ejidos/ejidos_Tampico_SanLuis.csv` - Lista de ejidos
- `../analisis_ejidos/ejidos_Tampico_SanLuis.geojson` - Geometrías

## Acciones Pendientes
1. Revisar CSV de ejidos para identificar críticos (< 500m)
2. Consultar RENAPO para status legal de ejidos prioritarios
3. Contactar autoridades agrarias de SLP y Tamaulipas
