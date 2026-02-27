"""
Video360 QGIS Plugin - metadata.txt
====================================
Metadata del plugin para QGIS.
"""

# Metadata del plugin
metadata = {
    'name': 'Video360 Detector',
    'description': 'Plugin para extraer frames de video 360°, detectar objetos con YOLO y crear shapefiles georreferenciados',
    'author': 'Video360 Team',
    'email': 'support@example.com',
    'category': 'Raster',
    'icon': 'icon.png',
    'version': '1.0.0',
    'qgisMinimumVersion': '3.20',
    'experimental': False,
    'deprecated': False,
    'tags': 'video,360,yolo,detection,gis,georeference',
    'homepage': 'https://github.com/example/video360_detector',
    'repository': 'https://github.com/example/video360_detector',
    'tracker': 'https://github.com/example/video360_detector/issues',
    'download_url': 'https://github.com/example/video360_detector/releases',
}

# Dependencies
dependencies = {
    'python': [
        'cv2',
        'numpy', 
        'ultralytics',
        'geopandas',
        'shapely',
        'PyQt5'
    ]
}

def classFactory(iface):
    """Factory function para QGIS."""
    from .video360_detector import Video360DetectorPlugin
    return Video360DetectorPlugin(iface)


class Video360DetectorPlugin:
    """Plugin class principal."""
    
    def __init__(self, iface):
        self.iface = iface
    
    def initGui(self):
        """Inicializa la GUI."""
        from qgis.PyQt.QtWidgets import QAction
        from qgis.PyQt.QtGui import QIcon
        
        icon_path = __file__.parent / 'icon.png'
        
        self.action = QAction(
            QIcon(str(icon_path)) if icon_path.exists() else QIcon(),
            'Video360 Detector',
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
        """Ejecuta el plugin."""
        from .video360_detector import Video360DetectorDialog
        dialog = Video360DetectorDialog()
        dialog.exec_()
