# Plan de Levantamiento: LiDAR Vehicular + Dron como Backup

## Metodología Principal

### 1. LiDAR Vehicular (PRINCIPAL)
- Scanner LiDAR montado en vehículo
- GPS/GNSS + IMU para georreferenciación
- Cobertura desde caminos/carreteras
- Ventajas: rápido, preciso, sin permisos de airspace

### 2. Dron (SECUNDARIO/Backup)
- Para zonas donde el carro no puede acceder
- Áreas con vegetación densa donde se necesita vista aérea
- Complemento al LiDAR vehicular

---

## Configuración LiDAR Vehicular

### Equipo Principal
| Componente | Especificación |
|-----------|---------------|
| LiDAR | Velodyne VLP-32, Livox Horizon, o similar |
| GPS/IMU | Applanix POS LV, OxTS, o similar |
| Cámara | 360° o RGB para textura |
| Vehículo | SUV o pickup 4x4 |
| Laptop | Adquisición en tiempo real |

### Parámetros de Adquisición
| Parámetro | Valor |
|-----------|-------|
| Velocidad vehicular | 30-60 km/h |
| Densidad de puntos | 100-500 pts/m² |
| Ancho de franja | 20-50 m por pasada |
| Accuracy horizontal | 2-5 cm |
| Accuracy vertical | 3-8 cm |

---

## Plan de Trabajo por Bloque

### Metodología: 1 bloque = 1 día completo

**Estructura por día:**
1. **Mañana:** Adquisición LiDAR vehicular (carreteras/caminos)
2. **Tarde:** Verificación de coverage + sobrevuelo dron si necesario
3. **Noche:** Backup de datos + procesamiento inicial

### Tiempo Estimado por Bloque (LiDAR Vehicular)

| Tipo de trabajo | Tiempo estimado |
|-----------------|----------------|
| Adquisición LiDAR carro | 4-6 horas |
| Cobertura de caminos | Variable según km |
| Verificación campo | 1-2 horas |
| Procesamiento inicial | 2-4 horas |
| **Total por día** | **8-10 horas** |

---

## Cronograma Corregido

### Proyecto 1: TAMPICO - SAN LUIS

| Día | Fecha | Actividad | Método |
|-----|-------|-----------|--------|
| 1 | 30/03 | Bloque 1: Adquisición LiDAR | Carro |
| 2 | 31/03 | Bloque 1: Procesamiento + Dron backup si necesario | Carro + Dron |
| 3 | 01/04 | Bloque 2: Adquisición LiDAR | Carro |
| 4 | 02/04 | Bloque 2: Procesamiento + Dron | Carro + Dron |
| 5 | 03/04 | Bloque 3: Adquisición LiDAR | Carro |
| 6 | 04/04 | Bloque 3: Procesamiento + Dron | Carro + Dron |
| 7 | 05/04 | Descanso | - |
| 8 | 06/04 | Bloque 4: Adquisición LiDAR | Carro |
| 9 | 07/04 | Bloque 4: Procesamiento + Dron | Carro + Dron |
| 10 | 08/04 | Bloque 5: Adquisición LiDAR | Carro |
| 11 | 09/04 | Bloque 5: Procesamiento + Dron | Carro + Dron |
| 12 | 10/04 | Descanso | - |
| 13 | 11/04 | Bloque 6: Adquisición LiDAR | Carro |
| 14 | 12/04 | Bloque 6: Procesamiento + Dron | Carro + Dron |
| 15 | 13/04 | Bloque 7: Adquisición LiDAR | Carro |
| 16 | 14/04 | Bloque 7: Procesamiento + Dron | Carro + Dron |
| 17 | 15/04 | Descanso | - |
| 18 | 16/04 | Bloque 8: Adquisición LiDAR | Carro |
| 19 | 17/04 | Bloque 8: Procesamiento + Dron | Carro + Dron |
| 20 | 18/04 | Bloque 9: Adquisición LiDAR | Carro |
| 21 | 19/04 | Bloque 9: Procesamiento + Dron | Carro + Dron |

### Proyecto 2: VERACRUZ - TAMPICO

| Día | Fecha | Actividad | Método |
|-----|-------|-----------|--------|
| 22 | 20/04 | Transición | - |
| 23 | 21/04 | Bloque 1: Adquisición LiDAR | Carro |
| 24 | 22/04 | Bloque 1: Procesamiento + Dron | Carro + Dron |
| 25 | 23/04 | Bloque 2: Adquisición LiDAR | Carro |
| 26 | 24/04 | Bloque 2: Procesamiento + Dron | Carro + Dron |
| 27 | 25/04 | Descanso | - |
| 28 | 26/04 | Bloque 3: Adquisición LiDAR | Carro |
| 29 | 27/04 | Bloque 3: Procesamiento + Dron | Carro + Dron |
| 30 | 28/04 | Bloque 4: Adquisición LiDAR | Carro |
| 31 | 29/04 | Bloque 4: Procesamiento + Dron | Carro + Dron |
| 32 | 30/04 | Descanso | - |
| 33 | 01/05 | Bloque 5: Adquisición LiDAR | Carro |
| 34 | 02/05 | Bloque 5: Procesamiento + Dron | Carro + Dron |
| 35 | 03/05 | Bloque 6: Adquisición LiDAR | Carro |
| 36 | 04/05 | Bloque 6: Procesamiento + Dron | Carro + Dron |
| 37 | 05/05 | Descanso | - |
| 38 | 06/05 | Bloque 7: Adquisición LiDAR | Carro |
| 39 | 07/05 | Bloque 7: Procesamiento + Dron | Carro + Dron |
| 40 | 08/05 | Bloque 8: Adquisición LiDAR | Carro |
| 41 | 09/05 | Bloque 8: Procesamiento + Dron | Carro + Dron |
| 42 | 10/05 | Descanso | - |
| 43 | 11/05 | Bloque 9: Adquisición LiDAR | Carro |
| 44 | 12/05 | Bloque 9: Procesamiento + Dron | Carro + Dron |
| 45 | 13/05 | Bloque 10: Adquisición LiDAR | Carro |
| 46 | 14/05 | Bloque 10: Procesamiento + Dron | Carro + Dron |
| 47 | 15/05 | Descanso | - |
| 48 | 16/05 | Bloque 11: Adquisición LiDAR | Carro |
| 49 | 17/05 | Bloque 11: Procesamiento + Dron | Carro + Dron |
| 50-54 | 18-22/05 | Procesamiento Final | Oficina |
| 55 | 23/05 | Entrega | - |

---

## Resumen

| Concepto | Valor |
|----------|-------|
| Total bloques | 20 |
| Días de adquisición LiDAR | 20 |
| Días de procesamiento | 20 |
| Días de descanso | 7 |
| Días procesamiento final | 5 |
| **Total días** | **52** |
| Fecha inicio | 30 de Marzo 2026 |
| Fecha término | 23 de Mayo 2026 |

---

## Equipo Necesario

### LiDAR Vehicular
- [ ] Scanner LiDAR (Velodyne/Livox)
- [ ] Sistema GPS/IMU
- [ ] Laptop de adquisición
- [ ] Vehículo 4x4
- [ ] Baterías y cargadores
- [ ] Disco duro para backup

### Dron (Backup)
- [ ] Dron DJI M300/M350 RTK
- [ ] LiDAR para dron (DJI L1 o similar)
- [ ] Baterías adicionales
- [ ] Control remoto

### Apoyo
- [ ] RTK de mano para GCPs
- [ ] GPS de navegación
- [ ] Radios de comunicación
- [ ] Herramientas básicas

---

## Ventajas del LiDAR Vehicular

1. **Más rápido** - 30-60 km/h vs 5-10 m/s del dron
2. **Sin restricciones de airspace** - No necesita permisos de vuelo
3. **Mejor precisión** - Sistemas GPS/IMU de alta precisión
4. **Más seguro** - No hay riesgo de caída
5. **Funciona en más condiciones** - Viento, lluvia ligera

## Cuando usar el Dron

1. Zonas donde el carro no puede llegar
2. Áreas con vegetación muy densa
3. Necesidad de vista aérea complementaria
4. Verificación deCoverage

---

*Documento generado - 2026-03-23*
