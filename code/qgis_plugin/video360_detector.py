"""
Video360Detector - Plugin QGIS para video 360 con YOLO
========================================================
Plugin de QGIS que integra extracción de frames, detección YOLO
y generación de shapefiles georreferenciados.
"""

import os
import json
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# QGIS imports
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QAction
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QProgressBar, QTextEdit, QMessageBox, QGroupBox
)
from qgis.core import (
    Qgis, 
    Qt,
    QgsProject, 
    QgsVectorLayer,
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
   Qgis,
    addVectorLayer,
    addRasterLayer
)
from qgis import processing

# Importar módulos locales
from .video_frame_extractor import Video360FrameExtractor
from .detector.yolo_detector import YOLODetector
from .shapefile_generator import ShapefileGenerator
from .streetview.street_view_generator import StreetViewHTMLGenerator


class Video360DetectorDialog(QDialog):
    """Diálogo principal del plugin."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video360 Detector - YOLO")
        self.resize(600, 700)
        
        # Estado
        self.frames_dir = ""
        self.detections = []
        self.output_dir = ""
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🎥 Video360 Detector con YOLO")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)
        
        # Grupo: Video Input
        input_group = QGroupBox("📹 Video de Entrada")
        input_layout = QVBoxLayout()
        
        # Video file
        video_layout = QHBoxLayout()
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Seleccionar video 360°...")
        video_btn = QPushButton("📂")
        video_btn.clicked.connect(self.select_video)
        video_layout.addWidget(self.video_input)
        video_layout.addWidget(video_btn)
        input_layout.addLayout(video_layout)
        
        # GPS Data (optional)
        gps_layout = QHBoxLayout()
        self.gps_input = QLineEdit()
        self.gps_input.setPlaceholderText("Archivo GPS (JSON) - Opcional...")
        gps_btn = QPushButton("📂")
        gps_btn.clicked.connect(self.select_gps)
        gps_layout.addWidget(self.gps_input)
        gps_layout.addWidget(gps_btn)
        input_layout.addLayout(gps_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Grupo: Configuración
        config_group = QGroupBox("⚙️ Configuración")
        config_layout = QVBoxLayout()
        
        # Distance interval
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Distancia entre frames (m):"))
        self.distance_spin = QSpinBox()
        self.distance_spin.setRange(1, 500)
        self.distance_spin.setValue(20)
        dist_layout.addWidget(self.distance_spin)
        dist_layout.addStretch()
        config_layout.addLayout(dist_layout)
        
        # Detection radius
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Radio de detección (m):"))
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 100)
        self.radius_spin.setValue(10)
        radius_layout.addWidget(self.radius_spin)
        radius_layout.addStretch()
        config_layout.addLayout(radius_layout)
        
        # YOLO Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Modelo YOLO:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "yolo11n.pt - Nano (rápido)",
            "yolo11s.pt - Small",
            "yolo11m.pt - Medium",
            "yolo11l.pt - Large",
            "yolo11x.pt - XLarge"
        ])
        self.model_combo.setCurrentIndex(1)  # Small
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        config_layout.addLayout(model_layout)
        
        # Confidence
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confianza mínima:"))
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.01, 1.0)
        self.conf_spin.setValue(0.25)
        self.conf_spin.setSingleStep(0.05)
        conf_layout.addWidget(self.conf_spin)
        conf_layout.addStretch()
        config_layout.addLayout(conf_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Opciones adicionales
        options_group = QGroupBox("📋 Opciones")
        options_layout = QVBoxLayout()
        
        self.save_crops_check = QCheckBox("Guardar recortes de detecciones")
        self.save_crops_check.setChecked(True)
        options_layout.addWidget(self.save_crops_check)
        
        self.create_streetview_check = QCheckBox("Crear visor Street View")
        self.create_streetview_check.setChecked(True)
        options_layout.addWidget(self.create_streetview_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Output
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Directorio de salida:"))
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("output_video360")
        output_layout.addWidget(self.output_input)
        layout.addLayout(output_layout)
        
        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Log
        self.log = QTextEdit()
        self.log.setMaximumHeight(100)
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("🚀 Ejecutar Todo")
        self.run_btn.setStyleSheet("background: #4CAF50; color: white; padding: 10px;")
        self.run_btn.clicked.connect(self.run_pipeline)
        
        self.close_btn = QPushButton("✖️ Cerrar")
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def log_msg(self, msg: str):
        """Agrega mensaje al log."""
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def select_video(self):
        """Selecciona archivo de video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Video", "", 
            "Videos (*.mp4 *.avi *.mov *.mkv)"
        )
        if file_path:
            self.video_input.setText(file_path)
    
    def select_gps(self):
        """Selecciona archivo GPS."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar GPS", "",
            "JSON (*.json)"
        )
        if file_path:
            self.gps_input.setText(file_path)
    
    def load_gps_data(self) -> Optional[Dict]:
        """Carga datos GPS del archivo."""
        gps_file = self.gps_input.text()
        if not gps_file or not os.path.exists(gps_file):
            return None
        
        try:
            with open(gps_file) as f:
                return json.load(f)
        except Exception as e:
            self.log_msg(f"Error cargando GPS: {e}")
            return None
    
    def run_pipeline(self):
        """Ejecuta el pipeline completo."""
        video_path = self.video_input.text()
        
        if not video_path:
            QMessageBox.warning(self, "Error", "Selecciona un video")
            return
        
        if not os.path.exists(video_path):
            QMessageBox.warning(self, "Error", "Video no encontrado")
            return
        
        # Configuración
        distance = self.distance_spin.value()
        radius = self.radius_spin.value()
        model_name = self.model_combo.currentText().split(" - ")[0]
        confidence = self.conf_spin.value()
        
        output_dir = self.output_input.text() or "output_video360"
        
        self.run_btn.setEnabled(False)
        self.progress.setValue(0)
        
        try:
            # === Paso 1: Extraer frames ===
            self.log_msg("=" * 40)
            self.log_msg("1️⃣ Extrayendo frames...")
            self.progress.setValue(10)
            
            gps_data = self.load_gps_data()
            
            extractor = Video360FrameExtractor(
                video_path=video_path,
                distance_interval=distance,
                output_dir=f"{output_dir}/frames",
                gps_data=gps_data
            )
            
            frames = extractor.extract_frames()
            self.log_msg(f"   → {len(frames)} frames extraídos")
            self.progress.setValue(30)
            
            # === Paso 2: Detección YOLO ===
            self.log_msg("2️⃣ Ejecutando YOLO...")
            self.progress.setValue(40)
            
            detector = YOLODetector(
                model_name=model_name,
                confidence=confidence,
                detection_radius=radius
            )
            
            frames_dir = f"{output_dir}/frames"
            metadata_path = f"{frames_dir}/extraction_metadata.json"
            
            self.detections = detector.process_directory(
                frames_dir,
                metadata_path=metadata_path,
                save_crops=self.save_crops_check.isChecked()
            )
            
            self.log_msg(f"   → {len(self.detections)} objetos detectados")
            self.progress.setValue(60)
            
            # === Paso 3: Generar Shapefile ===
            self.log_msg("3️⃣ Generando Shapefile...")
            self.progress.setValue(70)
            
            shapefile_gen = ShapefileGenerator(
                output_dir=f"{output_dir}/shapefile",
                detection_radius=radius
            )
            
            shapefile_gen.add_detections(self.detections)
            shapefile_results = shapefile_gen.generate_all()
            
            summary = shapefile_gen.get_summary()
            self.log_msg(f"   → {summary['total']} detecciones georreferenciadas")
            self.log_msg(f"   → Clases: {summary['by_class']}")
            self.progress.setValue(85)
            
            # === Paso 4: Street View ===
            if self.create_streetview_check.isChecked():
                self.log_msg("4️⃣ Generando Street View...")
                
                streetview = StreetViewHTMLGenerator(
                    output_path=f"{output_dir}/street_view/index.html"
                )
                streetview.add_frames_from_metadata(metadata_path)
                streetview.generate()
                
                self.log_msg("   → Visor Street View creado")
            
            # === Cargar en QGIS ===
            self.log_msg("5️⃣ Cargando capas en QGIS...")
            
            # Cargar shapefile de puntos
            if shapefile_results.get('points'):
                layer = addVectorLayer(shapefile_results['points'], "Detecciones", "ogr")
                if layer:
                    self.log_msg("   → Capa de detecciones cargada")
            
            # Cargar shapefile de buffers
            if shapefile_results.get('buffer'):
                layer = addVectorLayer(shapefile_results['buffer'], "Detecciones_Buffer", "ogr")
                if layer:
                    self.log_msg("   → Capa de buffers cargada")
            
            self.progress.setValue(100)
            self.log_msg("✅ ¡Proceso completado!")
            
            QMessageBox.information(
                self, "Éxito", 
                f"Proceso completado!\n"
                f"- Frames: {len(frames)}\n"
                f"- Detecciones: {len(self.detections)}\n"
                f"- Output: {output_dir}"
            )
            
        except Exception as e:
            self.log_msg(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", str(e))
        
        finally:
            self.run_btn.setEnabled(True)


def run_plugin():
    """Función para ejecutar el plugin."""
    dialog = Video360DetectorDialog()
    dialog.exec_()


# Para Testing sin QGIS
def run_cli(video_path: str, output_dir: str = "output"):
    """Ejecuta sin QGIS (modo CLI)."""
    import sys
    
    print(f"Procesando: {video_path}")
    print(f"Output: {output_dir}")
    
    # 1. Extraer frames
    print("\n1. Extrayendo frames...")
    extractor = Video360FrameExtractor(
        video_path=video_path,
        distance_interval=20,
        output_dir=f"{output_dir}/frames"
    )
    frames = extractor.extract_frames()
    print(f"   → {len(frames)} frames")
    
    # 2. YOLO
    print("\n2. Ejecutando YOLO...")
    detector = YOLODetector(
        model_name="yolo11s.pt",
        confidence=0.25,
        detection_radius=10.0
    )
    detections = detector.process_directory(
        f"{output_dir}/frames",
        metadata_path=f"{output_dir}/frames/extraction_metadata.json"
    )
    print(f"   → {len(detections)} detecciones")
    
    # 3. Shapefile
    print("\n3. Generando Shapefile...")
    shapefile_gen = ShapefileGenerator(
        output_dir=f"{output_dir}/shapefile",
        detection_radius=10.0
    )
    shapefile_gen.add_detections(detections)
    results = shapefile_gen.generate_all()
    print(f"   → {results}")
    
    # 4. Street View
    print("\n4. Generando Street View...")
    streetview = StreetViewHTMLGenerator(
        output_path=f"{output_dir}/street_view/index.html"
    )
    streetview.add_frames_from_metadata(f"{output_dir}/frames/extraction_metadata.json")
    streetview.generate()
    
    print("\n✅ ¡Listo!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "output")
    else:
        print("Usage: python video360_detector.py <video_path> [output_dir]")
