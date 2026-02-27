"""
Video360 YOLO Detector - Plugin para QGIS
==========================================
"""

def classFactory(iface):
    """Factory function para QGIS."""
    from .video360_plugin import Video360Plugin
    return Video360Plugin(iface)
