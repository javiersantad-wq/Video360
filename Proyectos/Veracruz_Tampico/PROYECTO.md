# Proyecto: Veracruz - Tampico

## Descripción
Corredor de canalización y microsoldadura para infraestructura
- **Bloques:** 45 segmentos
- **Longitud total:** ~400+ km
- **Extensión:** Desde Veracruz hasta Tampico, Tamaulipas

## Tipos de Trabajo Identificados
- Microzanja (varios kilómetros)
- Postes CFE (existentes y nuevos)
- Canalización

## Estructura de Carpetas

```
Veracruz_Tampico/
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
- **Total:** 280 ejidos
- **Estados:** Tamaulipas (100%)
- **Municipios principales:** Tampico, Cd. Madero, San Fernando, Méndez, Burgos, Cruillas

## Archivos Generados
- `../analisis_ejidos/ejidos_Veracruz_Tampico.csv` - Lista de ejidos
- `../analisis_ejidos/ejidos_Veracruz_Tampico.geojson` - Geometrías

## Acciones Pendientes
1. Revisar CSV de ejidos para identificar críticos (< 500m)
2. Consultar RAN para status legal de ejidos en zona costera
3. Contactar comunidades pesqueras (afectación costera)
4. Coordinar con autoridades portuarias si aplica
