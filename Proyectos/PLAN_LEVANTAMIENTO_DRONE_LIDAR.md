# Plan de Levantamiento con Dron + LiDAR

## Proyectos de Corredores de Infraestructura

**Fecha de elaboración:** 23 de marzo de 2026  
**Versión:** 1.0

---

## ÍNDICE

1. Resumen de Proyectos
2. Especificaciones Técnicas Recomendadas
3. Planificación de Vuelo por Bloque
4. Puntos de Despegue/Aterrizaje
5. GCPs y Control Terrestre
6. Cronograma de Trabajo
7. Checklist de Campo
8. Procesamiento de Datos
9. Equipo Necesario
10. Permisos y Coordinacion
11. Anexos

---

## 1. RESUMEN DE PROYECTOS

### 1.1 Proyecto Tampico - San Luis Potosí

| Característica | Valor |
|----------------|-------|
| **Longitud total** | ~300+ km |
| **Número de bloques** | 45 |
| **Tipo de trabajo** | Canalización (minicepa, tipo A, piedra bola) + postes CFE |
| **Estados** | Tamaulipas (CVE 30), San Luis Potosí (CVE 24) |
| **Municipios principales** | Aldama, Güémez, San Fernando, Valle Hermoso, Río Bravo (Tamps); Ciudad Valles, Tamazunchale, Ébano (SLP) |
| **Ejidos identificados** | 160 (a 2 km del corredor) |
| **Ciudades principales** | Tampico → San Fernando → Aldama → (hacia SLP) |
| **Terreno dominante** | Planicie costera, zonas agrícolas |

### 1.2 Proyecto Veracruz - Tampico

| Característica | Valor |
|----------------|-------|
| **Longitud total** | ~400+ km |
| **Número de bloques** | 45 |
| **Tipo de trabajo** | Microzanja + postes CFE + canalización |
| **Estados** | Tamaulipas (CVE 30) |
| **Municipios principales** | Tampico, Cd. Madero, San Fernando, Méndez, Burgos, Cruillas, San Carlos |
| **Ejidos identificados** | 280 (a 2 km del corredor) |
| **Ciudades principales** | Veracruz → Tampico → Cd. Madero → San Fernando |
| **Terreno dominante** | Costa, humedales, zona urbana, zona rural |

---

## 2. ESPECIFICACIONES TÉCNICAS RECOMENDADAS

### 2.1 Configuración de Vuelo LiDAR

| Parámetro | Valor | Justificación |
|------------|-------|---------------|
| **Altura de vuelo** | 80 m sobre terreno | Balance entre resolución y cobertura |
| **Velocidad de vuelo** | 8 m/s | LiDAR requiere velocidad moderada |
| **Sobreposición frontal** | 60% | Garantiza densidad de puntos |
| **Sobreposición lateral** | 30% | Líneas paralelas con 70% de ancho efectivo |
| **Ancho de franja** | ~120 m por pasada | A 80m de altura con escaneo de 90° |
| **Puntos por m²** | 16-25 pts/m² | Suficiente para clasificación de suelo |
| **Returns** | 3-5 returns | Para penetrar vegetación densa |

### 2.2 Configuración de Vuelo con Cámara 360

| Parámetro | Valor | Justificación |
|------------|-------|---------------|
| **Altura de vuelo** | 60 m | Más cerca para mejor resolución |
| **Velocidad de vuelo** | 6 m/s | Estabilidad para capturar 360° |
| **Sobreposición frontal** | 75% | Para ortomosaico sin gaps |
| **Sobreposición lateral** | 40% | Garantiza cobertura completa |
| **Intervalo de captura** | 2 segundos | Sincronizado con GPS |

### 2.3 Sistema de Georreferenciación

```
OBLIGATORIO PARA AMBOS PROYECTOS:

1. RTK en tiempo real (base en tierra)
   - Base en punto已知 con coordenadas precisas
   - Radio de comunicación: 10-15 km
   - Accuracy esperado: 2-3 cm horizontal, 3-5 cm vertical

2. PPK como backup
   - Procesamiento post-vuelo con datos RAW GPS/GLONASS
   - Accuracy: 3-5 cm horizontal

3. GCPs (Ground Control Points)
   - Mínimo: 5 por proyecto (o 1 por cada 10 km)
   - Distribución: Inicio, medio, fin del corredor + puntos altos
   - Medición: GPS de doble frecuencia, 60+ épocas
   - Targets: X de lona blanca 1m x 1m
```

---

## 3. PLANIFICACIÓN DE VUELO POR BLOQUE

### 3.1 Metodología de Planificación

Cada bloque del shapefile representa un tramo de trabajo. La planificación de vuelo debe:

1. **Seguir el corredor** - Líneas de vuelo paralelas al corredor
2. **Buffer de cobertura** - 20m a cada lado del corredor
3. **Dividir por bloques** - Cada bloque puede ser 1-3 misiones de vuelo

### 3.2 Cálculo de Tiempo de Vuelo

```
FÓRMULAS:

Área del corredor = Longitud (km) × Ancho (m) / 1,000,000 = km²
Tiempo de vuelo (min) = (Área / Velocidad de coverage) + 10 min (setup)

Coverage rate a 80m altura, 8 m/s:
   = Ancho efectivo (120m) × Velocidad (8m/s)
   = 960 m²/s = 34.56 ha/min = 0.3456 km²/min

Ejemplo para bloque de 15 km:
   Área = 15 km × 0.15 km = 2.25 km²
   Tiempo = 2.25 / 0.3456 + 10 = ~16.5 + 10 = ~27 min de vuelo
   Baterías: ~3 packs de baterías (25 min por batería)
```

### 3.3 Estructura de Vuelo Sugerida

```
PARA CADA BLOQUE:

Misión 1: Vuelo principal (LiDAR + Cámara 360)
   - 2-3 pasadas paralelas al corredor
   - Altura: 80m
   - Batería: 20-25 min

Misión 2: GCPs y checkpoints
   - Vuelo perpendicular o foto de zonas de GCP
   - Puede hacerse con dron pequeño o manual

Misión 3: Áreas problematicas (si aplica)
   - Vecindades, zonas difíciles
   - Vuelo manual o con waypoints adicionales
```

### 3.4 Distribución de Líneas de Vuelo

```
Para corredor lineal (camino, río, canal):

PATRÓN: Líneas paralelas al corredor con offset transversal

  ←—— Corridor (eje central) ——→
  |    Líneas de vuelo:         |
  |    |---|---|---|---|---|---|  ← 30% overlap
  |    |---|---|---|---|---|---|  
  |    |---|---|---|---|---|---|  
  ↑    |---|---|---|---|---|---|  
Buffer 20m   Buffer 20m
  
Cada línea = 1 pasada de dron
```

---

## 4. PUNTOS DE DESPEGUE/ATERRIZAJE

### 4.1 Criterios de Selección

```
PUNTO DE DESPEGUE IDEAL:

✓ Espacio abierto mínimo 10m x 10m
✓ Acceso por camino/carretera
✓ Altura similar al entorno (evitar slopes pronunciados)
✓ Línea de vista a cielo abierto (para RTK)
✓ Distancia máxima del corredor: 500m (idealmente menos)
✓ Seguridad: lejos de líneas eléctricas, obstáculos

EVITAR:
✗ Techos de edificios
✗ Estacionamientos con vehículos
✗ Zonas con gente sin notificación
✗ Áreas inundadas o suelo suelto
```

### 4.2 Ubicaciones Sugeridas por Proyecto

#### Tampico - San Luis Potosí

```
ZONAS DE OPERACIÓN SUGERIDAS:

ZONA 1: Tampico (Inicio)
   - Punto: Parque Industrial flanking, Tampico
   - Cover: Bloques 1-8 (parte sur)
   - Access: Carretera Tampico-Ciudad Madero

ZONA 2: San Fernando (Centro)
   - Punto: sth, outskirts de San Fernando
   - Cover: Bloques 9-25 (parte media)
   - Access: Carretera federal 70

ZONA 3: Aldama/Valle Hermoso (Norte)
   - Punto: ths vicinity, Aldama
   - Cover: Bloques 26-45 (parte norte hacia SLP)
   - Access: Carretera Aldama-Ciudad Mante
```

#### Veracruz - Tampico

```
ZONAS DE OPERACIÓN SUGERIDAS:

ZONA 1: Veracruz (Inicio - Sur)
   - Punto: Centro commercial area, Boca del Río
   - Cover: Bloques 1-10 (parte sur)
   - Access: Carretera Veracruz-Cardel

ZONA 2: Tlapacoyan/PEROTE (Centro Montaña)
   - Punto: Area rural, Perote
   - Cover: Bloques 11-25 (parte media, elevación)
   - Access: Carretera federal 140

ZONA 3: Tampico (Fin - Norte)
   - Punto: Zapata/bs, norte de Tampico
   - Cover: Bloques 26-45 (parte norte)
   - Access: Carretera Tampico-Mante
```

---

## 5. GCPs Y CONTROL TERRESTRE

### 5.1 Distribución de GCPs

```
PARA CADA PROYECTO:

GCPs requeridos: Mínimo 5-7 por proyecto completo

DISTRIBUCIÓN:

Proyecto Tampico-San Luis (~300km):
├── GCP-TS-01: Inicio (cerca de Tampico) - 22.20°N, -97.85°W
├── GCP-TS-02: San Fernando (medio) - 22.75°N, -98.95°W
├── GCP-TS-03: Norte (antes de SLP) - 22.20°N, -99.50°W
├── GCP-TS-04: punto alto - verificar en mapa
└── GCP-TS-05: Punto de verificación (no usado en ajuste)

Proyecto Veracruz-Tampico (~400km):
├── GCP-VT-01: Inicio (Boca del Río) - 19.10°N, -96.10°W
├── GCP-VT-02: Zona Media (Martínez de la Torre) - 19.95°N, -96.85°W
├── GCP-VT-03: San Fernando (medio-norte) - 22.75°N, -98.15°W
├── GCP-VT-04: Tampico (fin norte) - 22.25°N, -97.85°W
└── GCP-VT-05: Punto de verificación

ADICIONAL: 1 GCP por cada 50km adicionales de corredor
```

### 5.2 Especificaciones de GCP

```
GCP = Ground Control Point = Punto de Control Terrestre

MEDICIÓN:
- GPS de doble frecuencia (RTK o post-procesado)
- 60+ épocas, rate 1-5 segundos
- Archivo RAW para post-proceso
- Accuracy objetivo: < 2 cm horizontal, < 3 cm vertical

TARGET EN CAMPO:
- X de lona blanca 1m x 1m
- O bien: Marcaje permanente en el suelo (pintura)
- Fotografía del GCP con dron para referencia
- Coordenadas del centro del X

DOCUMENTACIÓN:
- Photo del GCP en su ubicación
- Coordenadas en formato:
  - LAT, LON (WGS84)
  - UTM (para procesamiento)
  - Elevación ortométrica (msnm)
```

---

## 6. CRONOGRAMA DE TRABAJO

### 6.1 Estimación de Tiempo

```
PARA AMBOS PROYECTOS:

Consideraciones:
- 2 operadores de dron
- 1 topógrafo para GCPs
- 1 coordinador logístico
- 1 vehículo de apoyo

Capacidad diaria estimada:
- 2-4 bloques por día (según longitud)
- 8-15 km de corredor cubierto por día
- 3-5 GCPs medidos por día

TIEMPO TOTAL ESTIMADO POR PROYECTO:

Fase 1: Reconocimiento y setup
   - 1 día de oficina (planificación, revisión de datos)
   - 0.5 días de reconocimiento de campo

Fase 2: GCPs y control terrestre
   - 2 días para 5-7 GCPs por proyecto

Fase 3: Vuelos de dron
   - 8-12 días de vuelo (45 bloques / ~4-5 bloques por día)

Fase 4: Procesamiento y QA
   - 3-5 días de procesamiento
   - 1-2 días de validación

TOTAL ESTIMADO POR PROYECTO: 15-20 días laborables

PARA AMBOS PROYECTOS: 30-40 días (con equipo dedicado)
```

### 6.2 Secuencia Sugerida

```
DÍA 1-2: Oficinas
├── Revisión de shapefiles y plan de vuelo
├── Descarga de mapas offline
├── Briefing con equipo
└── Verificación de equipos

DÍA 3: Campo - GCPs
├── Topógrafo mide GCPs
└── Equipo de dron hace reconocimiento

DÍA 4-7: Vuelos (primera semana)
├── 4-5 días de vuelo
├── 2-3 bloques por día
└── Backup de datos daily

DÍA 8: Descanso/Weather buffer

DÍA 9-12: Vuelos (segunda semana)
├── Completar bloques restantes
└── GCPs de verificación

DÍA 13-15: Procesamiento
├── Procesamiento de nube de puntos
├── Clasificación
└── Entrega preliminar

DÍA 16-17: Validación y correcciones
├── QC de datos
└── Vuelos adicionales si necesarios

DÍA 18-20: Entrega final
```

---

## 7. CHECKLIST DE CAMPO

### 7.1 Antes de Salir de Oficina

```
□ Baterías cargadas al 100% (todas)
□ SD cards formateadas y verificadas
□ RTK base cargada y verificada
□ RTK rover cargado y verificado
□ Dron principal verificado (test de motores)
□ Dron backup cargado y verificado
□ Tablet/celular con flight plan cargado
□ Maps offline descargados para la zona
□ Weather forecast verificado (no lluvia, viento <10m/s)
□ Permisos de vuelo impresos
□ Contactos de emergencia guardados
□ Botiquín de primeros aux
□ Agua y snacks (zona rural)
□ Radio comunicación (si aplica)
```

### 7.2 Antes de Cada Vuelo

```
□ Weather check in sitio (viento, nubes)
□ Inspección visual del área de despegue
□ Verificar línea de vista RTK (cielo abierto)
□ Check de batería del dron
□ Check de batería del control
□ SD card insertada y verificada
□ GPS del dron con fix (esperar 30+ segundos)
□ RTK link establecido y verificado
□ Flight plan cargado y verificado en mapa
□ Lista de waypoints revisada
□ Emergency landing spots identificados
□ Notify teammate del flight plan
□ Persona de guardia asignada (para emergencias)
```

### 7.3 Después de Cada Vuelo

```
□ Apagar dron y контроллер
□ Retirar SD card y guardar en lugar seguro
□ Descargar datos a laptop (mínimo 2 copies)
□ Verificar coverage en campo (quick preview)
□ Marcar SD card como "used" y fecha
□ Check de batería restante
□ Reporte de vuelo (hora, duracion, anomalías)
□ Documentar condiciones (fotos del sitio)
□ Backup de datos (copiar a segundo disk)
```

---

## 8. PROCESAMIENTO DE DATOS

### 8.1 Pipeline de Procesamiento

```
DÍA 1-2: Descarga y organización

ESTRUCTURA DE CARPETAS:
Proyecto/
├── campo/
│   ├── 2026-03-XX/
│   │   ├── bloque_01/
│   │   │   ├── raw_lidar/
│   │   │   ├── raw_photos/
│   │   │   ├── logs/
│   │   │   └── video/
│   │   └── bloque_02/
│   └── ...
├── gnss/
│   ├── base_rover/
│   └── ppk/
├── gcps/
│   ├── measurements/
│   └── photos/
└── processing/
    ├── 01_raw/
    ├── 02_trajectory/
    ├── 03_pointcloud/
    ├── 04_classified/
    ├── 05_dem/
    └── 06_deliverable/
```

### 8.2 Workflow Detallado

```
STEP 1: Descarga de datos RAW
├── Dron → laptop (copia 1)
├── Laptop → external drive (copia 2)
├── Verificar checksums si posible
└── Nombrado estándar: PROYECTO_BLOQUE_YYYYMMDD_HHMM

STEP 2: Procesamiento de trayectoria
├── Descargar datos de la base RTK
├── Combinar con datos RAW GPS del dron
├── Procesar con software (RTKLIB, Inertial Explorer)
├── Generar archivo .traj con timestamps
└── Verificar: gaps < 0.1 segundos

STEP 3: Georreferenciación RAW
├── Importar datos LiDAR RAW
├── Aplicar trayectorias
├── Verificar accuracy de posición
├── Exportar en formato .las o .laz
└── QC: revisar que points make sense

STEP 4: Clasificación de puntos
├── Clasificar automáticamente (ground, vegetation, buildings)
├── Software: LAStools, CloudCompare, PDAL
├── Manual review: corregir errores obvios
├── Ground points para DTM
└── All points para DSM

STEP 5: Generación de modelos
├── DTM (Digital Terrain Model) - solo ground
├── DSM (Digital Surface Model) - todo
├── Nube de puntos coloreada (si RGB disponible)
└── Ortomosaico (si hay fotos)

STEP 6: Validación
├── Comparar con GCPs (debería ser < 5 cm)
├── Comparar con checkpoints independientes
├── Visual inspection en 3D
└── Reporte de accuracy

STEP 7: Entrega
├── .las/.laz (nube de puntos cruda)
├── .tif (DTM y DSM)
├── .pdf (reporte de accuracy)
├── .shp/.gpkg (sivector data requested)
└── Archivo de métadata (parameters, date, crew)
```

### 8.3 Software Recomendado

| Función | Herramienta | Costo |
|---------|------------|-------|
| Flight planning | UGCS, QGroundControl | Gratis - $500 |
| Process GNSS/RTK | RTKLIB, Waypoint GIFA | Gratis - $2000 |
| Process LiDAR | LAStools, PDAL, CloudCompare | Gratis |
| Procesamiento DJI | DJI Terra, DJI P1 | Depende equipo |
| GIS/Visualización | QGIS, ArcGIS Pro | Gratis - $ |
| Deliverables | Global Mapper | $ |

---

## 9. EQUIPO NECESARIO

### 9.1 Equipo Principal

```
Drones:
├── Dron 1: DJI M300/M350 RTK + LiDAR (L1 o similar)
├── Dron 2: DJI M300/M350 RTK + Cámara 360
└── Dron 3: Backup (Mavic o similar)

Sensores:
├── LiDAR: Velodyne VLP-32C / Livox Avia / DJI L1
├── Cámara 360: Insta360 X4 / Ricoh Theta
└── Cámara RGB (opcional): Para ortomosaicos
```

### 9.2 Equipo de Georreferenciación

```
□ RTK Base: CHC Nav i93 / Spectra SP80 o similar
□ RTK Rover: CHC Nav i93 / Spectra SP80 o similar
□ GPS de mano: Garmin GPSmap (para navegación)
□ Baterías extra para RTK (mínimo 4 sets)
```

### 9.3 Equipo de Apoyo

```
□ Laptop de procesamiento: i7+, 32GB RAM, 1TB SSD, GPU dedicado
□ Disco duro externo: 2TB mínimo (para backup)
□ Tablet para flight planning: iPad o similar
□ Radios de comunicación: Motorola o similar
□ Cámara convencional: Para dokumentation
□ Botiquín primero aux
□ Kit de herramientas: destornilladores, alicates, etc
```

---

## 10. PERMISOS Y COORDINACIÓN

### 10.1 Permisos Requeridos

```
MÉX - Requisitos para vuelo de dron:

1. AFAC (Agencia Federal de Aviación Civil)
   - Registro de equipo (si > 250g)
   - Permiso de vuelo en airspace específico
   - Altitud máxima: 120m AGL (sin permiso especial)

2. SEDENA (Secretaría de la Defensa Nacional)
   - Para zonas fronterizas, estratégicas
   - Verificar si el corredor está en zona restringida
   - Tiempo de respuesta: 2-4 semanas

3. Permisos Ejidales/Comunitarios
   - Contactar Asamblea Ejidal
   - Obtener carta de autorización
   - Coordinar horarios de vuelo
   - Algunos cobran tarifa por uso de tierras

4. Propiedad Privada
   - Permiso de propietarios
   - Para puntos de despegue en privado
```

### 10.2 Contactos por Proyecto

```
PARA AMBOS PROYECTOS:

□ RAN (Registro Agrario Nacional): www.gob.mx/ran
□ AFAC: www.gob.mx/afac
□ SEDENA: www.gob.mx/sedena

PARA TAMAULIPAS:
□ Gobierno del Estado de Tamaulipas
□ Municipio de Tampico
□ Municipio de San Fernando
□ Municipio de Cd. Madero

PARA SAN LUIS POTOSÍ:
□ Gobierno del Estado de SLP
□ Municipio de Ciudad Valles
□ Municipio de Tamazunchale
```

### 10.3 Coordinación Comunitaria

```
PARA CADA EJIDO IDENTIFICADO:

Contacto previo (1-2 semanas antes):
├── Carta formal explicando el proyecto
├── Qué se va a hacer (vuelo de dron para levantamiento topográfico)
├── Duración estimada
├── Beneficios para la comunidad
└── Persona de contacto

Día del vuelo:
├── Presentar credentials
├── Explicar qué vamos a hacer
├── Respetar instrucciones del ejido
└── Dejar contacto para dudas

Post-vuelo:
├── Agradecer la cooperación
└── Ofrecer copia de resultados (si aplica)
```

---

## 11. ANEXOS

### Anexo A: Formato de Reporte de Vuelo

```
REPORTE DE VUELO

Fecha: _____________
Proyecto: _____________
Bloque(s): _____________
Operador: _____________

DATOS DE VUELO:
Hora inicio: _____________
Hora fin: _____________
Duración: _____________
Baterías usadas: _____________
Condiciones weather: _____________

ÁREA CUBIERTA:
Cobertura (%) vs planificada: _____________
Anomalías: _____________
Areas no cubiertas: _____________

EQUIPO:
Dron ID: _____________
 firmware: _____________
LiDAR ID: _____________

DATOS:
Archivos: _____________
Tamaño total: _____________
Checksums: _____________

INCIDENTES:
□ Ninguno
□ Incidente: _____________

FIRMAS:
Operador: _____________
Supervisor: _____________
```

### Anexo B: Formato de Etiqueta de Datos

```
PROYECTO: [NOMBRE]
BLOQUE: [NUMERO]
FECHA: [YYYY-MM-DD]
HORA: [HH:MM]
OPERADOR: [NOMBRE]
DRON: [MODELO]
SENSOR: [TIPO]

ARCHIVOS:
- lidar_raw/
- photos/
- logs/

NOTAS:
```

---

## RESUMEN EJECUTIVO

| Aspecto | Tampico-San Luis | Veracruz-Tampico |
|---------|------------------|------------------|
| Longitud | ~300 km | ~400 km |
| Bloques | 45 | 45 |
| Tiempo estimado | 15-20 días | 15-20 días |
| Equipo requerido | 2 drones + 1 backup | 2 drones + 1 backup |
| GCPs | 5-7 | 5-7 |
| Dificultad principal | Zona rural, acceso | Zona costera, vegetación |

---

*Documento generado automáticamente - 2026-03-23*
