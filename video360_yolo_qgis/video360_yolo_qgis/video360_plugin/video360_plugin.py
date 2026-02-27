"""
Video360 YOLO Detector - Plugin para QGIS
==========================================
Plugin que integra el pipeline completo de detección en QGIS.
"""

from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QProgressBar, QTextEdit, QMessageBox, QGroupBox,
    QFormLayout, QTabWidget, QWidget
)
from qgis.core import (
    Qgis,Qgis, addVectorLayer, addRasterLayer, 
   QgProject, 
    QStringListValidator
)
from qgis import processing
import os
import subprocess
import json


class Video360Plugin:
    """Plugin class principal."""
    
    def __init__(self, iface):
        self.iface = iface
        self.dlg = None
        self.action = None
    
    def initGui(self):
        """Inicializa la GUI."""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        
        self.action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            'Video360 YOLO Detector',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('Video360', self.action)
    
    def unload(self):
        """Descar el plugin."""
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu('Video360', self.action)
    
    def run(self):
        """Ejecuta el diálogo del plugin."""
        if self.dlg is None:
            self.dlg = Video360Dialog()
        
        self.dlg.show()


class Video360Dialog(QDialog):
    """Diálogo principal del plugin."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video360 YOLO Detector para QGIS")
        self.resize(700, 650)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🎥 Video360 YOLO Detector")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Entrada
        tab_input = QWidget()
        input_layout = QVBoxLayout()
        
        # Video
        video_group = QGroupBox("📹 Video 360°")
        video_layout = QHBoxLayout()
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Seleccionar video 360°...")
        video_btn = QPushButton("📂")
        video_btn.clicked.connect(self.select_video)
        video_layout.addWidget(self.video_input)
        video_layout.addWidget(video_btn)
        video_group.setLayout(video_layout)
        input_layout.addWidget(video_group)
        
        # GPS
        gps_group = QGroupBox("📍 Datos GPS (GPX)")
        gps_layout = QHBoxLayout()
        self.gps_input = QLineEdit()
        self.gps_input.setPlaceholderText("Archivo GPX (opcional)...")
        gps_btn = QPushButton("📂")
        gps_btn.clicked.connect(self.select_gps)
        gps_layout.addWidget(self.gps_input)
        gps_layout.addWidget(gps_btn)
        gps_group.setLayout(gps_layout)
        input_layout.addWidget(gps_group)
        
        tab_input.setLayout(input_layout)
        tabs.addTab(tab_input, "Entrada")
        
        # Tab 2: Configuración
        tab_config = QWidget()
        config_layout = QFormLayout()
        
        # Distancia
        self.distance_spin = QSpinBox()
        self.distance_spin.setRange(1, 500)
        self.distance_spin.setValue(20)
        self.distance_spin.setSuffix(" metros")
        config_layout.addRow("Distancia entre frames:", self.distance_spin)
        
        # Radio
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(1, 100)
        self.radius_spin.setValue(10.0)
        self.radius_spin.setSuffix(" metros")
        config_layout.addRow("Radio de detección:", self.radius_spin)
        
        # Modelo
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "yolo11n.pt - Nano (rápido)",
            "yolo11s.pt - Small",
            "yolo11m.pt - Medium",
            "yolo11l.pt - Large",
            "yolo11x.pt - XLarge"
        ])
        self.model_combo.setCurrentIndex(0)
        config_layout.addRow("Modelo YOLO:", self.model_combo)
        
        # Confianza
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.01, 1.0)
        self.conf_spin.setValue(0.25)
        self.conf_spin.setSingleStep(0.05)
        config_layout.addRow("Confianza mínima:", self.conf_spin)
        
        tab_config.setLayout(config_layout)
        tabs.addTab(tab_config, "Configuración")
        
        # Tab 3: Output
        tab_output = QWidget()
        output_layout = QFormLayout()
        
        # Directorio output
        output_dir_layout = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Directorio de salida...")
        self.output_input.setText("output_video360")
        output_btn = QPushButton("📂")
        output_btn.clicked.connect(self.select_output)
        output_dir_layout.addWidget(self.output_input)
        output_dir_layout.addWidget(output_btn)
        output_layout.addRow("Output:", output_dir_layout)
        
        # Paso
        self.step_combo = QComboBox()
        self.step_combo.addItems([
            "all - Todo el pipeline",
            "extract - Solo extraer frames",
            "detect - Solo YOLO",
            "shapefile - Solo shapefile"
        ])
        output_layout.addRow("Paso a ejecutar:", self.step_combo)
        
        tab_output.setLayout(output_layout)
        tabs.addTab(tab_output, "Output")
        
        layout.addWidget(tabs)
        
        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Log
        self.log = QTextEdit()
        self.log.setMaximumHeight(120)
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("🚀 Ejecutar")
        self.run_btn.setStyleSheet("background: #4CAF50; color: white; padding: 12px; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_pipeline)
        
        self.close_btn = QPushButton("✖ Cerrar")
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def log_msg(self, msg):
        """Agrega mensaje al log."""
        self.log.append(msg)
    
    def select_video(self):
        """Selecciona video."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Video", "", 
            "Videos (*.mp4 *.avi *.mov *.mkv)"
        )
        if path:
            self.video_input.setText(path)
    
    def select_gps(self):
        """Selecciona archivo GPX."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar GPX", "", 
            "GPX (*.gpx)"
        )
        if path:
            self.gps_input.setText(path)
    
    def select_output(self):
        """Selecciona directorio de output."""
        path = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if path:
            self.output_input.setText(path)
    
    def run_pipeline(self):
        """Ejecuta el pipeline."""
        video = self.video_input.text()
        
        if not video:
            QMessageBox.warning(self, "Error", "Selecciona un video")
            return
        
        if not os.path.exists(video):
            QMessageBox.warning(self, "Error", "Video no encontrado")
            return
        
        # Obtener parámetros
        distance = self.distance_spin.value()
        radius = self.radius_spin.value()
        model = self.model_combo.currentText().split(" - ")[0]
        confidence = self.conf_spin.value()
        output = self.output_input.text() or "output_video360"
        step = self.step_combo.currentText().split(" - ")[0]
        
        self.log_msg("=" * 50)
        self.log_msg("Ejecutando Video360 YOLO Detector...")
        self.log_msg(f"Video: {video}")
        self.log_msg(f"Distancia: {distance}m")
        self.log_msg(f"Modelo: {model}")
        
        self.run_btn.setEnabled(False)
        
        try:
            # Ejecutar script Python
            script = os.path.join(os.path.dirname(__file__), 'video360_yolo_qgis.py')
            
            cmd = [
                sys.executable, script,
                '--video', video,
                '--distance', str(distance),
                '--radius', str(radius),
                '--model', model,
                '--confidence', str(confidence),
                '--output', output,
                '--step', step
            ]
            
            if self.gps_input.text():
                cmd.extend(['--gps', self.gps_input.text()])
            
            self.log_msg("Ejecutando...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            if result.returncode == 0:
                self.log_msg(result.stdout)
                
                # Cargar shapefile en QGIS
                shapefile_path = os.path.join(output, 'shapefile', 'detections_points.shp')
                if os.path.exists(shapefile_path):
                    layer = addVectorLayer(shapefile_path, "Detecciones Video360", "ogr")
                    if layer:
                        self.log_msg("✓ Capa cargada en QGIS")
                
                QMessageBox.information(
                    self, "Éxito", 
                    f"Proceso completado!\nOutput: {output}"
                )
            else:
                self.log_msg(f"ERROR: {result.stderr}")
                QMessageBox.critical(self, "Error", result.stderr)
        
        except Exception as e:
            self.log_msg(f"ERROR: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))
        
        finally:
            self.run_btn.setEnabled(True)
