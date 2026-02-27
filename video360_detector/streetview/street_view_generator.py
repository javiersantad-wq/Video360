"""
StreetViewGenerator - Genera visualizador Street View con mapa y tabla
=====================================================================
Crea un visor HTML profesional tipo Google Street View con:
- Vista 360° panorámica
- Mapa lateral con ruta y detecciones
- Tabla de detecciones con mini imágenes
- Navegación sincronizada
"""

import os
import json
import webbrowser
from pathlib import Path
from typing import List, Dict, Optional


class StreetViewHTMLGenerator:
    """
    Genera un visor HTML profesional con todas las funcionalidades.
    """
    
    def __init__(self, 
                 output_path: str = "./street_view/index.html",
                 title: str = "Video360 Street View"):
        
        self.output_path = Path(output_path).resolve()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # No usar base_dir - calcular rutas manualmente
        self.base_dir = None
        
        self.title = title
        self.frames: List[Dict] = []
        self.detections: List[Dict] = []
    
    def add_frame(self, 
                 image_path: str,
                 gps: Dict,
                 frame_index: int = 0):
        """Agrega un frame."""
        # Usar la ruta tal cual - el servidor sirve desde workspace
        self.frames.append({
            'image': image_path.replace('\\', '/'),
            'lat': gps.get('lat', 0),
            'lon': gps.get('lon', 0),
            'alt': gps.get('alt', 0),
            'index': frame_index,
        })
    
    def add_frames_from_metadata(self, metadata_path: str):
        """Carga frames desde metadata."""
        metadata_path = Path(metadata_path).resolve()
        
        with open(metadata_path) as f:
            data = json.load(f)
        
        for frame in data.get('frames', []):
            gps = frame.get('gps', {})
            if gps:
                self.add_frame(
                    image_path=frame.get('filepath', ''),
                    gps=gps,
                    frame_index=frame.get('index', 0)
                )
    
    def add_detections(self, detections: List[Dict]):
        """Agrega detecciones con información de crops."""
        for det in detections:
            if det.get('geo_position'):
                # Usar la ruta tal cual
                crop_url = det.get('crop_path', '').replace('\\', '/')
                
                self.detections.append({
                    'lat': det['geo_position']['lat'],
                    'lon': det['geo_position']['lon'],
                    'class_name': det.get('class_name', 'unknown'),
                    'confidence': det.get('confidence', 0),
                    'frame_index': det.get('frame_index', 0),
                    'bearing': det['geo_position'].get('bearing_deg', 0),
                    'crop_url': crop_url,
                    'timestamp': det.get('timestamp_str', '')
                })
    
    def add_detections_from_file(self, detections_path: str):
        """Carga detecciones desde archivo."""
        with open(detections_path) as f:
            data = json.load(f)
            self.add_detections(data.get('detections', []))
    
    def generate(self) -> str:
        """Genera el visor HTML completo."""
        frames_json = json.dumps(self.frames)
        detections_json = json.dumps(self.detections)
        
        html = self._generate_html(frames_json, detections_json)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(self.output_path)
    
    def _generate_html(self, frames_json: str, detections_json: str) -> str:
        """Genera el HTML completo."""
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    
    <!-- Three.js -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    
    <!-- Leaflet -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #1a1a1a;
            color: #fff;
            height: 100vh;
            overflow: hidden;
        }}
        
        .main-container {{
            display: flex;
            height: 100vh;
            width: 100vw;
        }}
        
        /* Panel izquierdo - Mapa + Tabla */
        .left-panel {{
            width: 35%;
            display: flex;
            flex-direction: column;
            border-right: 3px solid #4CAF50;
        }}
        
        /* Mapa */
        .map-container {{
            height: 45%;
            position: relative;
        }}
        
        #map {{
            width: 100%;
            height: 100%;
        }}
        
        /* Tabla de detecciones */
        .detections-panel {{
            height: 55%;
            background: #2a2a2a;
            display: flex;
            flex-direction: column;
        }}
        
        .detections-header {{
            padding: 12px;
            background: #333;
            border-bottom: 2px solid #4CAF50;
        }}
        
        .detections-header h3 {{
            color: #4CAF50;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .detections-list {{
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }}
        
        .detection-card {{
            background: #3a3a3a;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            display: flex;
            gap: 10px;
            cursor: pointer;
            transition: all 0.2s;
            border: 2px solid transparent;
        }}
        
        .detection-card:hover {{
            background: #444;
            border-color: #4CAF50;
        }}
        
        .detection-card.selected {{
            border-color: #FF5722;
            background: #3a3a3a;
        }}
        
        .detection-img {{
            width: 80px;
            height: 60px;
            object-fit: cover;
            border-radius: 4px;
            background: #222;
        }}
        
        .detection-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .detection-info h4 {{
            font-size: 13px;
            color: #4CAF50;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .detection-info p {{
            font-size: 11px;
            color: #aaa;
            margin: 2px 0;
        }}
        
        .confidence-badge {{
            background: #4CAF50;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
        }}
        
        /* Panel derecho - Vista 360 */
        .right-panel {{
            width: 65%;
            position: relative;
        }}
        
        #panorama {{
            width: 100%;
            height: 100%;
        }}
        
        /* Overlay info */
        .info-overlay {{
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(0,0,0,0.85);
            padding: 15px;
            border-radius: 10px;
            z-index: 1000;
            min-width: 250px;
        }}
        
        .info-overlay h2 {{
            color: #4CAF50;
            font-size: 16px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .info-overlay .info-row {{
            display: flex;
            justify-content: space-between;
            margin: 6px 0;
            font-size: 13px;
        }}
        
        .info-overlay .label {{
            color: #888;
        }}
        
        .info-overlay .value {{
            color: #fff;
            font-weight: 500;
        }}
        
        /* Controles */
        .controls {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            z-index: 1000;
            background: rgba(0,0,0,0.85);
            padding: 12px 20px;
            border-radius: 30px;
        }}
        
        .ctrl-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        
        .ctrl-btn:hover {{ background: #45a049; }}
        .ctrl-btn:disabled {{ background: #555; cursor: not-allowed; }}
        .ctrl-btn.active {{ background: #FF5722; }}
        
        /* Frame slider */
        .slider-container {{
            position: absolute;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            z-index: 1000;
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 10px;
        }}
        
        .slider-container input {{
            width: 100%;
            accent-color: #4CAF50;
        }}
        
        .slider-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #888;
            margin-top: 4px;
        }}
        
        /* Loading */
        #loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            color: #4CAF50;
            z-index: 2000;
        }}
        
        /* Leyenda */
        .legend {{
            position: absolute;
            bottom: 15px;
            right: 15px;
            background: rgba(0,0,0,0.85);
            padding: 10px;
            border-radius: 8px;
            z-index: 1000;
            font-size: 11px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 4px 0;
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        /* Thumbnail strip */
        .thumb-strip {{
            position: absolute;
            bottom: 140px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 5px;
            z-index: 1000;
            overflow-x: auto;
            max-width: 80%;
            padding: 5px;
            background: rgba(0,0,0,0.6);
            border-radius: 8px;
        }}
        
        .thumb {{
            width: 60px;
            height: 40px;
            border-radius: 4px;
            cursor: pointer;
            border: 2px solid transparent;
            object-fit: cover;
        }}
        
        .thumb:hover, .thumb.active {{
            border-color: #4CAF50;
        }}
        
        /* GPS indicator */
        .gps-indicator {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(0,0,0,0.85);
            padding: 8px 12px;
            border-radius: 8px;
            z-index: 1000;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .gps-indicator .gps-ok {{
            color: #4CAF50;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Panel izquierdo -->
        <div class="left-panel">
            <!-- Mapa -->
            <div class="map-container">
                <div id="map"></div>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-dot" style="background:#4CAF50"></div>
                        <span>Ruta</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background:#FF5722"></div>
                        <span>Frame actual</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background:#2196F3"></div>
                        <span>Deteccion</span>
                    </div>
                </div>
            </div>
            
            <!-- Tabla de detecciones -->
            <div class="detections-panel">
                <div class="detections-header">
                    <h3><i class="fas fa-list"></i> Detecciones ({len(self.detections)} objetos)</h3>
                </div>
                <div class="detections-list" id="detectionsList">
                    <!-- Las detecciones se cargan aqui -->
                </div>
            </div>
        </div>
        
        <!-- Panel derecho - 360 -->
        <div class="right-panel">
            <div id="panorama"></div>
            <div id="loading">Cargando Street View...</div>
            
            <!-- Info overlay -->
            <div class="info-overlay">
                <h2><i class="fas fa-map-marker-alt"></i> Ubicacion</h2>
                <div class="info-row">
                    <span class="label">Lat/Lon:</span>
                    <span class="value" id="coords">-</span>
                </div>
                <div class="info-row">
                    <span class="label">Altitud:</span>
                    <span class="value" id="altitude">-</span>
                </div>
                <div class="info-row">
                    <span class="label">Frame:</span>
                    <span class="value" id="frameNum">-</span>
                </div>
            </div>
            
            <!-- GPS indicator -->
            <div class="gps-indicator">
                <i class="fas fa-satellite-gps gps-ok"></i>
                <span id="gpsStatus">GPS Activo</span>
            </div>
            
            <!-- Thumbnail strip -->
            <div class="thumb-strip" id="thumbStrip"></div>
            
            <!-- Slider -->
            <div class="slider-container">
                <input type="range" id="frameSlider" min="0" max="{len(self.frames)-1}" value="0">
                <div class="slider-labels">
                    <span>Inicio</span>
                    <span>Frame <span id="sliderVal">1</span> / {len(self.frames)}</span>
                    <span>Fin</span>
                </div>
            </div>
            
            <!-- Controles -->
            <div class="controls">
                <button class="ctrl-btn" onclick="prevFrame()">
                    <i class="fas fa-chevron-left"></i> Anterior
                </button>
                <button class="ctrl-btn" id="playBtn" onclick="togglePlay()">
                    <i class="fas fa-play"></i> Play
                </button>
                <button class="ctrl-btn" onclick="nextFrame()">
                    Siguiente <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        </div>
    </div>

    <script>
        // Datos
        const frames = {frames_json};
        const detections = {detections_json};
        
        let currentFrame = 0;
        let isPlaying = false;
        let playInterval = null;
        let map, routeLine, frameMarkers = [];
        let currentMarker = null;
        
        // Three.js
        let scene, camera, renderer, sphere, controls;
        let textureLoader;
        
        // Colores
        const classColors = {{
            'car': '#2196F3',
            'person': '#FF9800',
            'motorcycle': '#E91E63',
            'truck': '#9C27B0',
            'bus': '#00BCD4',
            'train': '#795548',
            'default': '#607D8B'
        }};
        
        const classIcons = {{
            'car': 'fa-car',
            'person': 'fa-person',
            'motorcycle': 'fa-motorcycle',
            'truck': 'fa-truck',
            'bus': 'fa-bus',
            'train': 'fa-train',
            'default': 'fa-circle'
        }};
        
        // Inicializar
        function init() {{
            initMap();
            initThreeJS();
            renderDetectionsList();
            renderThumbnails();
            loadFrame(0);
            document.getElementById('loading').style.display = 'none';
        }}
        
        // === MAPA ===
        function initMap() {{
            if (frames.length === 0) return;
            
            const center = [frames[0].lat, frames[0].lon];
            map = L.map('map').setView(center, 16);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; OSM'
            }}).addTo(map);
            
            // Ruta
            const route = frames.map(f => [f.lat, f.lon]);
            routeLine = L.polyline(route, {{
                color: '#4CAF50',
                weight: 5,
                opacity: 0.9
            }}).addTo(map);
            
            map.fitBounds(routeLine.getBounds(), {{padding: [30, 30]}});
            
            // Marcadores de frames
            frames.forEach((f, idx) => {{
                const marker = L.circleMarker([f.lat, f.lon], {{
                    radius: 5,
                    fillColor: '#4CAF50',
                    color: '#fff',
                    weight: 1,
                    fillOpacity: 0.8
                }}).addTo(map);
                
                marker.on('click', () => loadFrame(idx));
                frameMarkers.push(marker);
            }});
            
            // Detecciones
            detections.forEach(d => {{
                const color = classColors[d.class_name] || classColors['default'];
                const marker = L.circleMarker([d.lat, d.lon], {{
                    radius: 8,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    fillOpacity: 0.9
                }}).addTo(map);
                
                const iconClass = classIcons[d.class_name] || classIcons['default'];
                marker.bindPopup(`
                    <div style="min-width:120px">
                        <h4 style="margin:0 0 8px 0;color:#4CAF50">
                            <i class="fas ${{iconClass}}"></i> ${{d.class_name}}
                        </h4>
                        <p style="margin:3px 0;font-size:12px">
                            <b>Confianza:</b> ${{(d.confidence * 100).toFixed(1)}}%
                        </p>
                        <p style="margin:3px 0;font-size:12px">
                            <b>Frame:</b> ${{d.frame_index}}
                        </p>
                        <button onclick="goToFrame(${{d.frame_index}})" 
                            style="margin-top:8px;background:#4CAF50;color:white;border:none;
                                   padding:6px 12px;border-radius:4px;cursor:pointer;width:100%">
                            Ver en 360
                        </button>
                    </div>
                `);
            }});
        }}
        
        // === THREE.JS 360 ===
        function initThreeJS() {{
            const container = document.getElementById('panorama');
            
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 0.1);
            
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);
            
            textureLoader = new THREE.TextureLoader();
            
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableZoom = true;
            controls.enablePan = false;
            controls.rotateSpeed = -0.3;
            controls.update();
            
            animate();
            window.addEventListener('resize', onWindowResize);
        }}
        
        function loadFrame(index) {{
            if (index < 0 || index >= frames.length) return;
            
            currentFrame = index;
            const frame = frames[index];
            
            // Info
            document.getElementById('coords').textContent = 
                frame.lat.toFixed(6) + ', ' + frame.lon.toFixed(6);
            document.getElementById('altitude').textContent = frame.alt.toFixed(1) + ' m';
            document.getElementById('frameNum').textContent = (frame.index + 1) + ' / ' + frames.length;
            document.getElementById('sliderVal').textContent = frame.index + 1;
            document.getElementById('frameSlider').value = index;
            
            // Cargar imagen
            const texture = textureLoader.load(frame.image, 
                () => {{ console.log('Cargado:', frame.image); }},
                undefined,
                (err) => {{ console.error('Error cargando:', frame.image, err); }}
            );
            texture.colorSpace = THREE.SRGBColorSpace;
            
            const material = new THREE.MeshBasicMaterial({{ map: texture }});
            
            const oldSphere = scene.getObjectByName('sphere');
            if (oldSphere) scene.remove(oldSphere);
            
            const geometry = new THREE.SphereGeometry(500, 60, 40);
            geometry.scale(-1, 1, 1);
            
            sphere = new THREE.Mesh(geometry, material);
            sphere.name = 'sphere';
            scene.add(sphere);
            
            // Actualizar mapa
            updateMapMarker(index);
            
            // Actualizar thumbnails
            updateThumbnails(index);
            
            // Actualizar botones
            document.querySelectorAll('.ctrl-btn')[0].disabled = (index === 0);
            document.querySelectorAll('.ctrl-btn')[2].disabled = (index === frames.length - 1);
        }}
        
        function updateMapMarker(index) {{
            frameMarkers.forEach((m, i) => {{
                m.setStyle({{ 
                    fillColor: i === index ? '#FF5722' : '#4CAF50',
                    radius: i === index ? 10 : 5
                }});
            }});
            
            if (frameMarkers[index]) {{
                map.setView([frames[index].lat, frames[index].lon], map.getZoom());
            }}
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }}
        
        function onWindowResize() {{
            const container = document.getElementById('panorama');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }}
        
        // === TABLA DE DETECCIONES ===
        function renderDetectionsList() {{
            const container = document.getElementById('detectionsList');
            container.innerHTML = '';
            
            detections.forEach((d, idx) => {{
                const color = classColors[d.class_name] || classColors['default'];
                const iconClass = classIcons[d.class_name] || classIcons['default'];
                
                const card = document.createElement('div');
                card.className = 'detection-card';
                card.onclick = () => goToFrame(d.frame_index);
                
                const imgSrc = d.crop_url || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="60"><rect fill="%23333" width="80" height="60"/><text x="40" y="30" text-anchor="middle" fill="%23666" font-size="10">Sin imagen</text></svg>';
                
                card.innerHTML = `
                    <img src="${{imgSrc}}" class="detection-img" alt="${{d.class_name}}" 
                         onerror="this.src='data:image/svg+xml,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'80\\' height=\\'60\\'><rect fill=\\'%23333\\' width=\\'80\\' height=\\'60\\'/><text x=\\'40\\' y=\\'35\\' text-anchor=\\'middle\\' fill=\\'%23666\\' font-size=\\'10\\'>Sin imagen</text></svg>'">
                    <div class="detection-info">
                        <h4 style="color:${{color}}">
                            <i class="fas ${{iconClass}}"></i> ${{d.class_name}}
                            <span class="confidence-badge">${{(d.confidence * 100).toFixed(0)}}%</span>
                        </h4>
                        <p><i class="fas fa-map-marker-alt"></i> ${{d.lat.toFixed(5)}}, ${{d.lon.toFixed(5)}}</p>
                        <p><i class="fas fa-film"></i> Frame: ${{d.frame_index}}</p>
                    </div>
                `;
                
                container.appendChild(card);
            }});
        }}
        
        // === THUMBNAILS ===
        function renderThumbnails() {{
            const strip = document.getElementById('thumbStrip');
            strip.innerHTML = '';
            
            frames.forEach((f, idx) => {{
                if (idx % 3 !== 0) return; // Mostrar cada 3 frames
                
                const thumb = document.createElement('img');
                thumb.src = f.image;
                thumb.className = 'thumb';
                thumb.onclick = () => loadFrame(idx);
                thumb.title = 'Frame ' + (idx + 1);
                strip.appendChild(thumb);
            }});
        }}
        
        function updateThumbnails(index) {{
            document.querySelectorAll('.thumb').forEach((t, i) => {{
                const frameIdx = i * 3;
                t.classList.toggle('active', frameIdx === index);
            }});
        }}
        
        // === NAVEGACION ===
        function nextFrame() {{
            if (currentFrame < frames.length - 1) loadFrame(currentFrame + 1);
        }}
        
        function prevFrame() {{
            if (currentFrame > 0) loadFrame(currentFrame - 1);
        }}
        
        function goToFrame(index) {{
            loadFrame(index);
            map.closePopup();
        }}
        
        function togglePlay() {{
            isPlaying = !isPlaying;
            const btn = document.getElementById('playBtn');
            
            if (isPlaying) {{
                btn.innerHTML = '<i class="fas fa-pause"></i> Pause';
                btn.classList.add('active');
                playInterval = setInterval(() => {{
                    if (currentFrame < frames.length - 1) nextFrame();
                    else loadFrame(0);
                }}, 1500);
            }} else {{
                btn.innerHTML = '<i class="fas fa-play"></i> Play';
                btn.classList.remove('active');
                clearInterval(playInterval);
            }}
        }}
        
        // Slider
        document.getElementById('frameSlider').addEventListener('input', (e) => {{
            loadFrame(parseInt(e.target.value));
        }});
        
        // Keyboard
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextFrame();
            if (e.key === 'ArrowLeft') prevFrame();
            if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
        }});
        
        // Iniciar
        init();
    </script>
</body>
</html>"""
    
    def open_in_browser(self):
        """Abre el visor en el navegador."""
        if self.output_path.exists():
            webbrowser.open(f"file://{self.output_path}")


def create_pro_street_view(
    frames_dir: str = "./frames",
    output_dir: str = "./street_view",
    metadata_path: Optional[str] = None,
    detections_path: Optional[str] = None
) -> str:
    """
    Crea el street view profesional.
    
    Uso:
    ----
    >>> create_pro_street_view(
    ...     metadata_path="./frames/extraction_metadata.json",
    ...     detections_path="./detections.json"
    ... )
    """
    generator = StreetViewHTMLGenerator(
        output_path=f"{output_dir}/index.html",
        title="Video360 Street View Pro"
    )
    
    if metadata_path:
        generator.add_frames_from_metadata(metadata_path)
    
    if detections_path:
        generator.add_detections_from_file(detections_path)
    
    return generator.generate()


if __name__ == "__main__":
    print("Street View Pro Generator listo.")
