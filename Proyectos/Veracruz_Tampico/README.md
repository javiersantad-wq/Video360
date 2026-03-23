# Proyecto Veracruz - Tampico

## Descripción
Corredor de microsoldadura y canalización para infraestructura de telecomunicación y/o energía eléctrica.

- **Total de bloques:** 45 segmentos
- **Longitud total aproximada:** ~400+ km
- **Extensión geográfica:** -97.95° a -96.22° W, 19.14° a 22.28° N
- **Fecha de datos:** 20 de marzo de 2026

## Tipos de Trabajo
- Microzanja (varios kilómetros)
- Postes CFE (existentes y nuevos)
- Canalización

## Estructura del Proyecto

```
Veracruz_Tampico/
├── datos/                              # ← PARA ARCMAP: cargar estos archivos
│   ├── Veracruz-Tampico-50km_blocks_v4.shp   # Shapefile del corredor (PRINCIPAL)
│   ├── Veracruz-Tampico-50km_blocks_v4.shx
│   ├── Veracruz-Tampico-50km_blocks_v4.dbf
│   ├── Veracruz-Tampico-50km_blocks_v4.prj
│   ├── Veracruz-Tampico-50km_blocks_v4.cpg
│   └── (agregar aquí datos INEGI cuando se descarguen)
├── analisis/
│   └── (resultados de análisis adicionales)
├── analisis_ejidos/                     # Copia de análisis de ejidos
│   ├── ejidos_Veracruz_Tampico.csv
│   └── ejidos_Veracruz_Tampico.geojson
├── ANALISIS_DEL_PROYECTO.docx          # ← REPORTE WORD
└── README.md                           # Este archivo
```

## Datos para ArcMap/QGIS

### Shapefile Principal
**Archivo:** `datos/Veracruz-Tampico-50km_blocks_v4.shp`

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

### Capas Adicionales (después de descargar de INEGI)
- `datos/inegi_localidades.shp` - Localidades del INEGI
- `datos/inegi_ageb.shp` - AGEB urbanas

## Estados y Municipios

### Tamaulipas (CVE 30)
Municipios principales: Tampico, Ciudad Madero, San Fernando, Méndez, Burgos, Cruillas, San Carlos,San Fernando

## Ejidos Identificados

- **Total a 2 km:** 280 ejidos
- **Estados:** Tamaulipas (100%)
- **Críticos (<500m):** EL MORALILLO, ANAHUAC, VILLA CUAUHTEMOC, EL CRUCERO

## Zonas Sensibles Identificadas

- **Zona costera de Tampico/Cd. Madero** - Alta densidad de población
- **Corredor río Pánuco** - Posibles comunidades pesqueras
- **Zona urbana de San Fernando** - Paso por zona urbana

## Próximos Pasos

1. [ ] Descargar Marco Geoestadístico de INEGI (ver instrucciones en `../datos_inegi/`)
2. [ ] Cargar shapefile del corredor en ArcMap
3. [ ] Agregar capa de ejidos desde `../analisis_ejidos/ejidos_Veracruz_Tampico.geojson`
4. [ ] Descargar y agregar localidades INEGI
5. [ ] Identificar zonas de exclusión para vuelo
6. [ ] Contactar comunidades ejidales y pesqueras
7. [ ] Coordinar con autoridades portuarias (si aplica)
8. [ ] Obtener permisos (SEDENA, AFAC, Asambleas Ejidales)

## Referencias
- RAN: https://www.gob.mx/ran
- AFAC: https://www.gob.mx/afac
- INEGI Marco Geoestadístico: https://www.inegi.org.mx/geo/
