# Análisis de Ejidos para Proyectos de Vuelo de Dron
## Corredores: Tampico-San Luis Potosí y Veracruz-Tampico

**Fecha:** 23 de marzo de 2026  
**Elaborado por:** Asistente Eduardo

---

## 1. RESUMEN EJECUTIVO

Se realizó un análisis geoespacial para identificar predios ejidales (comunales) cercanos a los corredores de vuelo proyectados. Esto es crítico para identificar posibles conflictos sociales antes de levantar un vuelo de dron.

### Resultados Principales:

| Proyecto | Ejidos a 2km | Estados | Municipios Principales |
|----------|---------------|---------|------------------------|
| Tampico-San Luis Potosí | **160** | SLP (24), Tamps (30) | Aldama, Güémez, San Fernando, etc. |
| Veracruz-Tampico | **280** | Tamps (30) | Tampico, Cd. Madero, San Fernando, etc. |

---

## 2. DESCRIPCIÓN DE LOS PROYECTOS

### 2.1 Proyecto Tampico-San Luis Potosí
- **Total de bloques:** 45
- **Tipo de trabajos:** Canalización (minicepa, tipo A, piedra bola), postes CFE
- **Extensión geográfica:** -100.95° a -97.87° W, 21.85° a 22.28° N
- **Longitud total aproximada:** ~300+ km
- **Estados atravesados:** Tamaulipas (norte) → San Luis Potosí

### 2.2 Proyecto Veracruz-Tampico
- **Total de bloques:** 45
- **Tipo de trabajos:** Microzanja, postes CFE, canalización
- **Extensión geográfica:** -97.95° a -96.22° W, 19.14° a 22.28° N
- **Longitud total aproximada:** ~400+ km
- **Estados atravesados:** Veracruz → Tamaulipas (sur a norte)

---

## 3. EJIDOS IDENTIFICADOS POR PROYECTO

### 3.1 Proyecto Tampico-San Luis Potosí

**Estados afectados:**
- **San Luis Potosí (CVE 24):** 130 ejidos
- **Tamaulipas (CVE 30):** 30 ejidos

**Municipios con mayor presencia de ejidos:**

| Municipio | Estado | Ejidos Cercanos |
|-----------|--------|-----------------|
| Aldama | Tamaulipas | 15+ |
| Güémez | Tamaulipas | 10+ |
| San Fernando | Tamaulipas | 20+ |
| Tamps capital | Tamaulipas | Varios |

**Ejidos con distancia < 500m al corredor:**
- EL MORALILLO (Tamos)
- ANAHUAC
- EL MORALILLO (segundo)
- VILLA CUAUHTEMOC (muy cercano)
- EL CRUCERO

### 3.2 Proyecto Veracruz-Tampico

**Estados afectados:**
- **Tamaulipas (CVE 30):** 280 ejidos (100%)

**Municipios principales atravesados:**
- Tampico
- Ciudad Madero
- San Fernando
- Méndez
- Burgos
- Cruillas
- San Carlos

**Ejidos críticos (distancia < 200m):**
- EL MORALILLO (¡muy cercano!)
- ANAHUAC
- VILLA CUAUHTEMOC (múltiples)
- EL CRUCERO

---

## 4. CÓDIGOS DE ESTADOS Y MUNICIPIOS

```
Tamaulipas = CVE 30
  - 001  Abasolo
  - 002  Aldama
  - ... 
  - 030  Ciudad Madero
  - ...
  - 039  Güémez
  - ...
  - 043  San Fernando
  - ...
  - 045  San Carlos
  - ...
  - 054  Tampico
  - ...

San Luis Potosí = CVE 24
  - 001  Ahualulco
  - ...
  - 039  Ciudad Valles
  - ...
  - 051  San Luis Potosí (capital)
  - ...

Veracruz = CVE 30 (NO - el estado es 30, diferente a Tamaulipas)
  - NOTA: En los datos, los ejidos del corredor VT solo muestran CVE 30 = Tamaulipas
```

---

## 5. CONSIDERACIONES SOCIALES PARA VUELO DE DRON

### 5.1 Marco Legal Relevante

**Tierras Ejidales (Ley Agraria):**
- Los ejidos son propiedad social de comunidades agrícolas
- Requieren permiso del **Asamblea Ejidal** para cualquier actividad comercial
- El artículo 10 de la Ley Agraria protege el uso de tierras ejidales

**Aviación Civil (Ley de Aeropuertos):**
- La **SCT** (Secretaría de Infraestructura, Comunicaciones y Transportes) regula vuelos de drones
- Permisos de sobrevuelo requieren análisis de riesgo
- Zonas urbanas = restricciones severas
- **Zonas rurales con comunidades = requiere permiso de comunitario**

### 5.2 Problemas Sociales Potenciales

| Problema | Descripción | Severidad |
|----------|-------------|-----------|
| **Conflicto por tierra** | Ejidos cerca de derechos de vía pueden tener litigios históricos | ⚠️⚠️⚠️ |
| **Nulos o insuficientes permisos** | Comunidades pueden negarse si no hay consulta previa | ⚠️⚠️⚠️ |
| **Impacto a cultivos** | Drones pueden alarmar ganado o afectar aves | ⚠️⚠️ |
| **Privacidad** | Comunidades pueden sentirse vigiladas | ⚠️ |
| **Conflictos服野外** | Areas de difícil acceso con comunidades hostiles | ⚠️⚠️ |
| **Daños a infraestructura** | Riesgo de caída sobre líneas eléctricas o cultivos | ⚠️ |

### 5.3 Pasos Recomendados Antes del Vuelo

1. **Consulta con autoridades agrarias:**
   - RAN (Registro Agrario Nacional) - verificar status de cada ejido
   - Liga de Comunidades Agrarias de Tamaulipas

2. **Contacto directo con ejidatarios:**
   - Asamblea ejidal = decisión colectiva
   - Presidentes de paraje/comunidad
   - Delegados municipales

3. **Documentación requerida:**
   - Carta de autorización de la asamblea ejidal
   - Permiso de la Secretaría de la Defensa Nacional (según zona)
   - Registro ante la AFAC (Agencia Federal de Aviación Civil)

4. **Compensación justa:**
   - Algunos ejidos cobran por uso de tierras
   - Negociar compensaciones por daños eventuales

---

## 6. RECOMENDACIONES DE ACCIÓN

### Alta Prioridad (acciones inmediatas)

1. **Mapear exactamente los ejidos más cercanos** a cada bloque de vuelo
2. **Identificar líderes comunales** en cada ejido crítico
3. **Preparar cartas de presentación** explicando el proyecto
4. **Programar reuniones** con asambleas ejidales antes del vuelo

### Mediana Prioridad

5. **Verificar status legal** de cada ejido en el RAN
6. **Investigar conflictos históricos** de tierra en la zona
7. **Contactar a la UMCA** (Unidad de Materiales y Combustibles) si aplica
8. **Obtener permisos de la SEDENA** para zonas estratégicas

### Documentos a Generar

- [ ] Mapa GIS con ejidos identificados
- [ ] Directorio de contactos por comunidad
- [ ] Plantilla de carta de autorización ejidal
- [ ] Checklist de requisitos legales

---

## 7. FUENTES DE INFORMACIÓN

### Datos Geoespaciales
- **RENAPO:** Padrón de ejidos y comunidades agrarias
- **RAN:** Registro Agrario Nacional -ww..gob.mx/ran
- **SIAP:** Sistema Nacional de Información e Integración de Mercados

### Marco Legal
- **Ley Agraria:** www.gob.mx/se/acciones-y-programas/ley-agraria
- **AFAC:** www.gob.mx/afac
- **SCT:** www.gob.mx/sct

### Contexto Socioeconómico
- **Coneval:** Pobreza municipal en Tamaulipas y SLP
- **BIENVIVIR:** Indicadores de bienestar por comunidad

---

## 8. ARCHIVOS GENERADOS

| Archivo | Descripción | Ubicación |
|---------|-------------|-----------|
| `ejidos_Tampico_SanLuis.geojson` | Ejidos cercanos al corredor TS | `analisis_ejidos/` |
| `ejidos_Veracruz_Tampico.geojson` | Ejidos cercanos al corredor VT | `analisis_ejidos/` |
| `ejidos_Tampico_SanLuis.csv` | Tabla de ejidos TS para Excel | `analisis_ejidos/` |
| `ejidos_Veracruz_Tampico.csv` | Tabla de ejidos VT para Excel | `analisis_ejidos/` |
| `datos/Tampico_SanLuis-50km_blocks.*` | Shapefile original del corredor | `Tampico_SanLuis/datos/` |
| `datos/Veracruz-Tampico-50km_blocks_v4.*` | Shapefile original del corredor | `Veracruz_Tampico/datos/` |

---

## 9. PRÓXIMOS PASOS

1. [ ] **Revisar los CSV generados** para identificar ejidos críticos
2. [ ] **Investigar en RENAPO** el status legal de ejidos con distancia < 500m
3. [ ] **Contactar autoridades municipales** de San Fernando, Tampico, Cd. Madero
4. [ ] **Buscar en INEGI** indicadores de pobreza y cohesión social por municipio
5. [ ] **Programar gira de acercamiento** con comunidades antes del vuelo

---

*Reporte generado automáticamente mediante análisis geoespacial de archivos shapefile*
