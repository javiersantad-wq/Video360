# -*- coding: utf-8 -*-

"""
Video360 YOLO Detector for QGIS Processing Toolbox
================================================
Plugin para Processing Toolbox de QGIS.
"""

import os
import sys
import json
import subprocess

from qgis.core import (
    Qgis,
    Qt,
    qgis,
    Qgis,
    QCoreApplication,
    QSettings,
    QIcon,
    QAction,
    QMessageBox,
    Qgis,
    qgis,
    # Processing
    QgsProcessingProvider,
    QgsProcessingAlgorithm,
    QgsProcessingFeedback,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsMessageLog,
    # Parameters
    QgsProcessingParameterFile,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterFolderDestination,
    # Registry
    QgsApplication,
)

# Import processing
try:
    from processing.core.Processing import Processing
    PROCESSING_AVAILABLE = True
except ImportError:
    PROCESSING_AVAILABLE = False


class Video360Provider(QgsProcessingProvider):
    """Provider para Video360 en Processing Toolbox."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.algs = []

    def loadAlgorithms(self):
        """Carga los algoritmos."""
        self.algs = [
            Video360ExtractFrames(),
            Video360Detect(),
            Video360GenerateShapefile(),
        ]
        
        for alg in self.algs:
            self.addAlgorithm(alg)

    def name(self):
        return "video360"

    def displayName(self):
        return "Video360 YOLO"

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def id(self):
        return "video360"

    def longName(self):
        return self.displayName()


class Video360ExtractFrames(QgsProcessingAlgorithm):
    """Extrae frames del video."""

    def group(self):
        return "Video360"

    def groupId(self):
        return "video360"

    def initAlgorithm(self, config=None):
        # Video input
        self.addParameter(
            QgsProcessingParameterFile(
                "VIDEO",
                "Video 360°",
                extensionFilter="Videos (*.mp4 *.avi *.mov *.mkv)"
            )
        )

        # GPS (optional)
        self.addParameter(
            QgsProcessingParameterFile(
                "GPS",
                "Archivo GPX (opcional)",
                extensionFilter="GPX (*.gpx)",
                optional=True
            )
        )

        # Distance
        self.addParameter(
            QgsProcessingParameterNumber(
                "DISTANCE",
                "Distancia entre frames (metros)",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=20,
                minValue=1,
                maxValue=500
            )
        )

        # Output directory
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                "OUTPUT",
                "Directorio de salida"
            )
        )

    def name(self):
        return "extractframes"

    def displayName(self):
        return "1. Extraer Frames"

    def shortHelpString(self):
        return "Extrae frames de un video 360 grados cada N metros"

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def processAlgorithm(self, parameters, context, feedback):
        video = self.parameterAsFile(parameters, "VIDEO", context)
        gps = self.parameterAsFile(parameters, "GPS", context)
        distance = self.parameterAsInt(parameters, "DISTANCE", context)
        output = self.parameterAsString(parameters, "OUTPUT", context)

        if not video:
            feedback.reportError("No se especificó el video")
            return {}

        feedback.pushInfo(f"Extrayendo frames cada {distance} metros...")

        # Find script
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        script = os.path.join(plugin_dir, "video360_yolo_qgis.py")

        if not os.path.exists(script):
            feedback.reportError(f"Script no encontrado: {script}")
            return {}

        # Execute
        cmd = [
            sys.executable, script,
            "--video", video,
            "--distance", str(distance),
            "--output", output,
            "--step", "extract"
        ]

        if gps and os.path.exists(gps):
            cmd.extend(["--gps", gps])

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            feedback.pushInfo("Frames extraidos correctamente")
            return {"OUTPUT": output}
        else:
            feedback.reportError(result.stderr)
            return {}


class Video360Detect(QgsProcessingAlgorithm):
    """Ejecuta YOLO en frames."""

    def group(self):
        return "Video360"

    def groupId(self):
        return "video360"

    def initAlgorithm(self, config=None):
        # Frames directory
        self.addParameter(
            QgsProcessingParameterFile(
                "FRAMES",
                "Directorio de frames",
                extensionFilter="Directories"
            )
        )

        # Model
        self.addParameter(
            QgsProcessingParameterString(
                "MODEL",
                "Modelo YOLO",
                defaultValue="yolo11n.pt",
                optional=True
            )
        )

        # Confidence
        self.addParameter(
            QgsProcessingParameterNumber(
                "CONFIDENCE",
                "Confianza minima",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.25,
                minValue=0.01,
                maxValue=1.0
            )
        )

        # Radius
        self.addParameter(
            QgsProcessingParameterNumber(
                "RADIUS",
                "Radio de deteccion (metros)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                minValue=1.0,
                maxValue=100.0
            )
        )

    def name(self):
        return "detectobjects"

    def displayName(self):
        return "2. Detectar Objetos YOLO"

    def shortHelpString(self):
        return "Ejecuta YOLO en los frames extraidos"

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def processAlgorithm(self, parameters, context, feedback):
        frames_dir = self.parameterAsString(parameters, "FRAMES", context)
        model = self.parameterAsString(parameters, "MODEL", context)
        confidence = self.parameterAsDouble(parameters, "CONFIDENCE", context)
        radius = self.parameterAsDouble(parameters, "RADIUS", context)

        feedback.pushInfo(f"Ejecutando YOLO ({model})...")

        # Find script
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        script = os.path.join(plugin_dir, "video360_yolo_qgis.py")

        if not os.path.exists(script):
            feedback.reportError(f"Script no encontrado: {script}")
            return {}

        # Execute
        cmd = [
            sys.executable, script,
            "--video", "dummy.mp4",
            "--frames-dir", frames_dir,
            "--model", model,
            "--confidence", str(confidence),
            "--radius", str(radius),
            "--step", "detect"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            feedback.pushInfo("Detecciones completadas")
            return {"OUTPUT": frames_dir}
        else:
            feedback.reportError(result.stderr)
            return {}


class Video360GenerateShapefile(QgsProcessingAlgorithm):
    """Genera shapefile."""

    def group(self):
        return "Video360"

    def groupId(self):
        return "video360"

    def initAlgorithm(self, config=None):
        # Detections
        self.addParameter(
            QgsProcessingParameterFile(
                "DETECTIONS",
                "Archivo detections.json",
                extensionFilter="JSON (*.json)"
            )
        )

        # Radius
        self.addParameter(
            QgsProcessingParameterNumber(
                "RADIUS",
                "Radio del buffer (metros)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=10.0,
                minValue=1.0,
                maxValue=100.0
            )
        )

        # Output
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                "OUTPUT",
                "Directorio de salida"
            )
        )

    def name(self):
        return "generateshapefile"

    def displayName(self):
        return "3. Generar Shapefile"

    def shortHelpString(self):
        return "Genera shapefile desde detecciones"

    def icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def processAlgorithm(self, parameters, context, feedback):
        detections = self.parameterAsFile(parameters, "DETECTIONS", context)
        radius = self.parameterAsDouble(parameters, "RADIUS", context)
        output = self.parameterAsString(parameters, "OUTPUT", context)

        feedback.pushInfo(f"Generando shapefile (radio: {radius}m)...")

        # Find script
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        script = os.path.join(plugin_dir, "video360_yolo_qgis.py")

        if not os.path.exists(script):
            feedback.reportError(f"Script no encontrado: {script}")
            return {}

        # Execute
        cmd = [
            sys.executable, script,
            "--video", "dummy.mp4",
            "--radius", str(radius),
            "--output", output,
            "--step", "shapefile"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            feedback.pushInfo("Shapefile generado")
            
            # Load in QGIS
            shp_path = os.path.join(output, "shapefile", "detections_points.shp")
            if os.path.exists(shp_path):
                layer = QgisCore.QgsVectorLayer(shp_path, "Video360 Detecciones", "ogr")
                if layer.isValid():
                    QgisProject.instance().addMapLayer(layer)
                    feedback.pushInfo("Capa cargada en QGIS")
            
            return {"OUTPUT": output}
        else:
            feedback.reportError(result.stderr)
            return {}


class Video360ProcessingPlugin:
    """Plugin principal."""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initProcessing(self):
        """Inicializa el provider."""
        self.provider = Video360Provider()
        QgisApplication.processingRegistry().addProvider(self.provider)
        self.iface.messageBar().pushMessage(
            "Video360",
            "Plugin cargado en Processing Toolbox",
            Qgis.Success,
            3
        )

    def initGui(self):
        """Inicializa la GUI."""
        self.initProcessing()

    def unload(self):
        """Desarga el plugin."""
        if self.provider:
            QgisApplication.processingRegistry().removeProvider(self.provider)


def classFactory(iface):
    """Factory function."""
    return Video360ProcessingPlugin(iface)
