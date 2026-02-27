"""
Servidor HTTP simple para servir el Street View
================================================
Inicia un servidor local y abre el navegador.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

def start_server(directory=None):
    """Inicia un servidor HTTP en el directorio actual."""
    
    if directory is None:
        directory = os.getcwd()
    
    os.chdir(directory)
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Permitir acceso a directorios padre
    class MyHandler(Handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
    
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Servidor iniciado en http://localhost:{PORT}")
        print(f"Directorio: {directory}")
        print("\nPresiona Ctrl+C para detener el servidor")
        
        # Abrir navegador
        webbrowser.open(f"http://localhost:{PORT}/street_view/index.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido")


if __name__ == "__main__":
    # Usar el directorio del proyecto
    os.chdir(r"C:\Users\ed\.openclaw\workspace")
    start_server()
