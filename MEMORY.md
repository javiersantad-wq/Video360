# MEMORY.md - Eduardo's Assistant

## Guidelines de Recuperación de Memoria

**Usar memory_search cuando el usuario mencione:**

- **Referencias explícitas:** "continúa nuestra conversación sobre...", "¿de qué discutimos?", "como mencioné antes..."
- **Referencias temporales:** "¿qué hablamos ayer?", "mostrar chats de la semana pasada"
- **Señales implícitas:**
  - Verbos en pasado sugiriendo intercambios previos: "sugiriste", "decidimos"
  - Posesivos sin contexto: "mi proyecto", "nuestro enfoque"
  - Artículos definidos asumiendo conocimiento compartido: "el bug", "la estrategia"
  - Pronombres sin antecedente: "ayúdame a arreglarlo", "¿qué pasa con eso?"
  - Preguntas asuntivas: "¿mencioné...?", "¿recuerdas...?"

**Keywords de alta confianza para búsqueda:**
- Nouns específicos (tecnologías, proyectos, productos)
- Conceptos técnicos (machine learning, OAuth, debugging)
- Nombres propios (ubicaciones, personas, empresas)
- Términos domain-specific

**Keywords a evitar:**
- Verbos genéricos: "hablar", "mencionar", "discutir"
- Marcadores de tiempo: "ayer", "la semana pasada"
- Nombres vagos: "cosa", "asunto", "problema" (sin specifics)

**Decision framework:**
1. ¿Referencia temporal? → memory_search o memory_get con fecha
2. ¿Tema específico mencionado? → memory_search
3. ¿Referencia vaga? → Pedir clarificación
4. ¿Sin referencia a pasado? → No buscar

---

## Proyecto Activo: Análisis de Vuelo de Dron (2026-03-23)

**Dos corredores identificados:**
1. **Tampico-San Luis Potosí** - 45 bloques, canalización (~300km)
2. **Veracruz-Tampico** - 45 bloques, microzanja/postes (~400km)

**Estructura de proyectos:**
- `C:\Users\ed\.openclaw\workspace\Proyectos\Tampico_SanLuis\`
- `C:\Users\ed\.openclaw\workspace\Proyectos\Veracruz_Tampico\`

**Análisis geoespacial realizado:**
- 160 ejidos identificados a 2km del corredor TS
- 280 ejidos identificados a 2km del corredor VT
- Estados: Tamaulipas (CVE 30), San Luis Potosí (CVE 24)

**Archivos generados:**
- `analisis_ejidos/ejidos_Tampico_SanLuis.csv` + `.geojson`
- `analisis_ejidos/ejidos_Veracruz_Tampico.csv` + `.geojson`
- `REPORTE_ANALISIS_SOCIAL.md` - Reporte completo con consideraciones sociales
- `localidades_osm.shp` - 875 localidades para TS, 617 para VT (OSM)
- `PLAN_LEVANTAMIENTO_DRONE_LIDAR.md` - Plan completo de levantamiento
- `*_flight_lines.shp` - Líneas de vuelo aproximadas para GIS
- `*_flight_summary.csv` - Resumen por bloque (km, tiempo, baterías)
- `ANALISIS_DEL_PROYECTO.docx` - Reporte Word por proyecto

**Datos técnicos por proyecto:**
| Proyecto | Longitud | Bloques | Tiempo estimado |
|----------|----------|---------|-----------------|
| Tampico-San Luis | ~435 km | 45 | ~15-20 días |
| Veracruz-Tampico | ~520 km | 45 | ~15-20 días |

**Próximos pasos:** Consultar RENAPO/RAN, contactar comunidades ejidales, permisos SEDENA/AFAC

---

## Proyecto: RTKCamera Pro (2026-05-09) 🆕

**Ubicación:** `C:\Users\ed\.openclaw\workspace\Proyectos\RTKCamera\`

**Objetivo:** App de mapeo geoespacial Android con RTK para precisión centimétrica. Inspirada en RTKcamera (at.redcatch.rtkcamera v2.1) pero con soporte dual para fotos y video.

**Features:**
- Tab RTK: Mapa OSMDroid + selector receptor GNSS (Bluetooth) + config NTRIP + indicadores de fix
- Tab Camera: Captura fotos/video geoetiquetadas (Insta360 X5 via TCP 6666 o cámara celular via CameraX)
- Tab App: Gestión de proyecto, exportación JSON/KML, estadísticas
- Distance trigger: Captura automática cada X metros (configurable 2-20m)
- RTK accuracy: ±2cm con fix RTK

**Arquitectura:**
- 3 Foreground Services: RTKService (BT GNSS), NTRIPService (TCP caster), Insta360Service (TCP 6666)
- Min SDK 26, Target SDK 34, Kotlin, MVVM
- Dependencias: OSMDroid 6.1.18, CameraX 1.3.1, Gson 2.10.1

**Estado:** Esqueleto completo creado (24 archivos, 4KK+ líneas Kotlin/XML). Faltan:
- Implementar distance trigger logic
- Probar conexión real con UM980
- Implementar sync GPS-Insta360 (timestamp matching)
- Agregar export GPX
- Soporte Livox Mid-360

**Para construir:**
```bash
cd android_app
gradle wrapper --gradle-version 8.4
./gradlew assembleDebug
```

---

## Proyecto: PointCloudPoleDetector (2026-03-23)

**Objetivo:** Detectar postes en nubes de puntos LiDAR para líneas de transmisión.

**Ubicación:** `C:\Users\ed\.openclaw\workspace\Proyectos\PointCloudPoleDetector\`

### .EXE DISTRIBUIBLE (2026-03-25) ✅
**Carpeta:** `C:\nube\nubes_a_shp\extract_pole_centroids\`
**Tamaño:** 365.6 MB (no necesita Python ni nada instalado)

**INTERACTIVO:** Al abrir el .exe sin argumentos abre menu para elegir clases, CRS, formatos, radio de clustering, etc.
**CLI:** Tambien funciona desde linea de comandos con parametros.

```
extract_pole_centroids/
├── extract_pole_centroids.exe  (17.6 MB)
├── _internal/                  (Python + dependencias)
└── ODA/                       (ODA File Converter para DWG, 69 MB)
```

**Uso:**
```cmd
extract_pole_centroids.exe archivo.las salida --class-code 14 --crs EPSG:32614 --dxf --dwg
```

**Dependencias incluidas:** laspy, geopandas, shapely, fiona, ezdxf, scikit-learn, numpy, pyproj, ODA File Converter

### Script: extract_pole_centroids.py (COMPLETO 2026-03-25)
Detección por filtrado geométrico (sin DL), usa DBSCAN + radius filter.

**Pendiente:** Probar GUI web (app.py), fine-tuning con datos etiquetados

---

## Proyecto: Mapeo 3D con Fusión de Sensores

**Setup objetivo:**
- Cámara 360 → color para nube de puntos LiDAR
- RTK → coordenadas precisas para LiDAR y video
- Video + RTK = video georreferenciado

**Hardware pendiente de confirmar:** modelos específicos de cámara 360, LiDAR y RTK

---

## Proyecto: CFMOTO 300NK BLE Scanner (2026-05-09) 🔧

**Ubicación:** `C:\Users\ed\.openclaw\workspace\Proyectos\CFMOTO_BLE\`

### Dispositivos BLE detectados (sin moto cerca):
- CFMOTO-LE-8C472C → DD:0D:30:8C:47:2C, -55 dBm, servicio 34fb
- CFMOTO-5F2C → 03:FF:01:04:5F:2C, -63 dBm, servicio 34fb

### Servicio BLE principal: Nordic UART (NUS) UUID 0000fea1-...

### App Android modificada: `com.cfmoto.blescanner`
- Scanner BLE con filtros para CFMOTO
- GATT Explorer con lectura/escritura de characteristics
- **Sniffer Mode**: foreground service que captura todo el trafico BLE
- APK debug en: `C:\Users\ed\Documents\apkcfmoto\apkcfmoto\CFMOTO_BLE\app\build\outputs\apk\debug\app-debug.apk`

### Protocolo (del APK de CFMOTO RIDE):
- Auth: Challenge-Response con encriptacion (cipher desconocido)
- Datos moto: speed, GPS, voltaje, temperatura, etc. via protobuf
- Comandos remotos: MQTT via 4G (lock/unlock/horn/etc.)
- WiFi Direct: canal de datos local

### Siguiente paso: capturar handshake con la moto cerca

---

## Entorno
- OS: Windows
- Workspace: C:\Users\ed\.openclaw\workspace

## Chats
- Webchat como canal principal

## Proyecto: Mapeo 3D con Fusión de Sensores (2026-05-02) ⚠️ ACTIVO

**Ubicación:** `C:\nube\openclaw\2026-03-06_proyecto_rtk_lidar_insta360\`
**Archivos:** 711 | **Respaldo:** `memory\2026-05-02-proyecto-rtk-lidar-insta360-respaldo.md`

### Hardware
| Componente | Estado | Notas |
|------------|--------|-------|
| Insta360 X5 | ✅ Disponible | Protocolo: TCP 6666 binary |
| Xiaomi Pad 7 Pro | ✅ Disponible | Control principal |
| GPS RTK (UM980/ZED-F9P) | ⏳ Comprar | $251-492 MX$ |
| Livox Mid-360 | ⏳ Opcional | Para nubes de puntos |
| USB UART FT232RL | ⏳ Comprar | ~$17-31 MX$ |
| Cable OTG USB-C | ⏳ Comprar | ~$6-13 MX$ |

### Método (basado en REDcatch 360RTK)

### Método (basado en REDcatch 360RTK)
1. Video continuo Insta360 X5 + logging GPS (CSV timestamps)
2. Fotos discretas como GCPs
3. Post-proceso: frames ↔ GPS → Metashape/Pix4D

### Lecciones
- ❌ No coordenadas en EXIF (6 dígitos insuficientes para RTK)
- ❌ No API HTTP para X5 (protocolo real: TCP 6666 binary)
- ✅ Logging GPS + timestamps como clave de sincronización
- 🆕 **Insta360 OSC API** (2026-05-10): HTTP/JSON público en puerto 80 — es el camino correcto para controlar X5 sin el protocolo binario del 6666
  - Docs: https://github.com/Insta360Develop/Insta360_OSC
  - Puerto: 80, headers: `Content-Type: application/json`, `X-XSRF-Protected: 1`
  - Endpoints: `/osc/info`, `/osc/state`, `/osc/commands/execute`, `/osc/commands/status`
  - Comandos: `camera.takePicture`, `camera.setOptions`, `camera.listFiles`, `camera.startCapture`/`stopCapture`
  - ⚠️ Puerto 80 de la X5 no respondió en pruebas — puede que el API OSC no esté activo o necesite activación vía app Insta360 primero
- Puerto 17777 en el celular = mock server/testing, no es de la cámara

### Compras Aliexpress
| Item | Precio MX$ | Link |
|------|-----------|------|
| Módulo UM980 RTK | $251-492 | 1005009578780196 |
| FT232RL USB UART | $17-31 | 1005006445462581 |
| Cable OTG USB-C | $6-13 | 1005009370263139
