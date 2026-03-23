# Proyecto Tampico - San Luis Potosí

## Descripción
Corredor de canalización para infraestructura de telecomunicación y/o energía eléctrica.

- **Total de bloques:** 45 segmentos
- **Longitud total aproximada:** ~300+ km
- **Extensión geográfica:** -100.95° a -97.87° W, 21.85° a 22.28° N
- **Fecha de datos:** 20 de marzo de 2026

## Tipos de Trabajo
- Canalización minicepa
- Canalización tipo A
- Canalización piedra bola
- Postes CFE

## Estructura del Proyecto

```
Tampico_SanLuis/
├── datos/                              # ← PARA ARCMAP: cargar estos archivos
│   ├── Tampico_SanLuis-50km_blocks.shp    # Shapefile del corredor (PRINCIPAL)
│   ├── Tampico_SanLuis-50km_blocks.shx
│   ├── Tampico_SanLuis-50km_blocks.dbf
│   ├── Tampico_SanLuis-50km_blocks.prj
│   ├── Tampico_SanLuis-50km_blocks.cpg
│   └── (agregar aquí datos INEGI cuando se descarguen)
├── analisis/
│   └── (resultados de análisis adicionales)
├── analisis_ejidos/                     # Copia de análisis de ejidos
│   ├── ejidos_Tampico_SanLuis.csv
│   └── ejidos_Tampico_SanLuis.geojson
├── ANALISIS_DEL_PROYECTO.docx          # ← REPORTE WORD
└── README.md                           # Este archivo
```

## Datos para ArcMap/QGIS

### Shapefile Principal
**Archivo:** `datos/Tampico_SanLuis-50km_blocks.shp`

**Campos:**
| Campo | Descripción |
|-------|-------------|
| Name | Nombre del trabajo |
| FolderPath | Ruta de carpeta |
| SymbolID | ID del símbolo |
| Shape_Leng | Longitud de la geometría |
| km | Longitud en kilómetros |
| bloque | Número de bloque |

**Tipo de geometría:** LineString Z (líneas 3D con coordenadas + elevación)

### Capas Adicionales ( después de descargar de INEGI)
- `datos/inegi_localidades.shp` - Localidades del INEGI
- `datos/inegi_ageb.shp` - AGEB urbanas

## Estados y Municipios

### Tamaulipas (CVE 30)
Municipios principales: Aldama, Güémez, San Fernando, Valle Hermoso, Río Bravo

### San Luis Potosí (CVE 24)
Municipios principales: Ciudad Vales, Tamazunchale, Ébano, San Vicente

## Ejidos Identificados

- **Total a 2 km:** 160 ejidos
- **Estados:** San Luis Potosí (130), Tamaulipas (30)
- **Críticos (<500m):** EL MORALILLO, ANAHUAC, VILLA CUAUHTEMOC, EL CRUCERO

## Próximos Pasos

1. [ ] Descargar Marco Geoestadístico de INEGI (ver instrucciones en `../datos_inegi/`)
2. [ ] Cargar shapefile del corredor en ArcMap
3. [ ] Agregar capa de ejidos desde `../analisis_ejidos/ejidos_Tampico_SanLuis.geojson`
4. [ ] Descargar y agregar localidades INEGI
5. [ ] Identificar zonas de exclusión para vuelo
6. [ ] Contactar comunidades ejidales
7. [ ] Obtener permisos (SEDENA, AFAC, Asambleas Ejidales)

## Referencias
- RAN: https://www.gob.mx/ran
- AFAC: https://www.gob.mx/afac
- INEGI Marco Geoestadístico: https://www.inegi.org.mx/geo/
