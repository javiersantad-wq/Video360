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

**Próximos pasos:** Consultar RENAPO/RAN, contactar comunidades ejidales, permisos SEDENA/AFAC

---

## Proyecto: Mapeo 3D con Fusión de Sensores

**Setup objetivo:**
- Cámara 360 → color para nube de puntos LiDAR
- RTK → coordenadas precisas para LiDAR y video
- Video + RTK = video georreferenciado

**Hardware pendiente de confirmar:** modelos específicos de cámara 360, LiDAR y RTK

---

## YOLOv8-Mobile App (2026-03-12)
- ✅ Detección en tiempo real funcionando
- ✅ Etiquetas mostradas en pantalla (chair, person, cup)
- ✅ GPS mostrando coordenadas automáticamente
- ✅ Guardado automático a CSV cada 5 segundos
- ✅ Botón WhatsApp
- ✅ App estable (sin crashes)
- Package: com.xvesa.yolov8mobile
- Device: 9028eb7f (Redmi 13 Pro 5G)
- Proyecto: C:\nube\openclaw\YOLOv8-Mobile
- APK: app-debug.apk

**Continuar desarrollo: Mañana 10am**

---

## Entorno
- OS: Windows
- Workspace: C:\Users\ed\.openclaw\workspace

## Chats
- Webchat como canal principal
