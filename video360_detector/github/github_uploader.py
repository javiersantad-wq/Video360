"""
GitHubUploader - Sube archivos a repositorio GitHub
====================================================
Maneja la autenticación y subida de archivos al repositorio.
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import subprocess

# Intentar importar библиотеку de GitHub
try:
    from github import Github
    from github.GithubException import GithubException
    PYGithub_AVAILABLE = True
except ImportError:
    PYGithub_AVAILABLE = False
    print("Advertencia: PyGithub no instalado. Instalar con: pip install PyGithub")


class GitHubUploader:
    """
    Sube archivos al repositorio GitHub.
    
    Parámetros:
    -----------
    repo_path : str
        Ruta al repositorio local (default: '.')
    token : str, optional
        Token de GitHub (también puede setearse con GITHUB_TOKEN env)
    commit_message : str
        Mensaje de commit base
    """
    
    def __init__(self, 
                 repo_path: str = ".",
                 token: Optional[str] = None,
                 commit_message: str = "Update: Video360 detections"):
        
        self.repo_path = Path(repo_path)
        self.token = token or os.environ.get('GITHUB_TOKEN', '')
        self.commit_message_base = commit_message
        
        self.uploaded_files: List[str] = []
        self.repo = None
        
        # Intentar inicializar repo
        self._init_repo()
    
    def _init_repo(self):
        """Inicializa el repositorio."""
        # Verificar si es un repo git
        git_dir = self.repo_path / '.git'
        
        if not git_dir.exists():
            print(f"Inicializando repositorio en {self.repo_path}")
            subprocess.run(['git', 'init'], cwd=self.repo_path, capture_output=True)
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, capture_output=True)
    
    def add_file(self, 
                file_path: str, 
                repo_path: str,
                commit_message: Optional[str] = None) -> bool:
        """
        Agrega un archivo al staging.
        
        Parámetros:
        -----------
        file_path : str
            Ruta del archivo a agregar
        repo_path : str
            Ruta dentro del repositorio
        commit_message : str, optional
            Mensaje de commit
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Archivo no encontrado: {file_path}")
            return False
        
        try:
            # git add
            result = subprocess.run(
                ['git', 'add', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.uploaded_files.append(str(file_path))
                print(f"Agregado: {file_path}")
                return True
            else:
                print(f"Error agregando {file_path}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def commit(self, message: Optional[str] = None) -> bool:
        """Hace commit de los cambios."""
        if not self.uploaded_files:
            print("No hay archivos para commit")
            return False
        
        msg = message or f"{self.commit_message_base} - {datetime.now().isoformat()}"
        
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', msg],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Commit hecho: {msg}")
                self.uploaded_files = []  # Limpiar
                return True
            else:
                print(f"Error en commit: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def push(self, 
             branch: str = "main",
             remote: str = "origin") -> bool:
        """Sube cambios al remoto."""
        if not self.token:
            print("ERROR: Se requiere GITHUB_TOKEN para hacer push")
            return False
        
        try:
            # Configurar remote con token
            remote_url = f"https://{self.token}@github.com/{self._get_repo_name()}.git"
            
            result = subprocess.run(
                ['git', 'remote', 'set-url', remote, remote_url],
                cwd=self.repo_path,
                capture_output=True
            )
            
            # Push
            result = subprocess.run(
                ['git', 'push', remote, branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"Push a {remote}/{branch} exitoso")
                return True
            else:
                print(f"Error en push: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def _get_repo_name(self) -> str:
        """Obtiene el nombre del repositorio."""
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            url = result.stdout.strip()
            # Extraer owner/repo
            if 'github.com' in url:
                return url.split('github.com/')[-1].replace('.git', '')
        except:
            pass
        return "owner/repo"
    
    def upload_all(self, 
                  files: List[str],
                  commit_message: Optional[str] = None,
                  push: bool = True) -> bool:
        """
        Sube múltiples archivos.
        
        Parámetros:
        -----------
        files : List[str]
            Lista de archivos a subir
        commit_message : str, optional
            Mensaje de commit
        push : bool
            Si True, hace push después del commit
        """
        # Agregar archivos
        for f in files:
            self.add_file(f, f)
        
        if not self.uploaded_files:
            print("No hay archivos para subir")
            return False
        
        # Commit
        if not self.commit(commit_message):
            return False
        
        # Push
        if push:
            return self.push()
        
        return True
    
    def create_github_release(self,
                             tag: str,
                             title: str,
                             description: str) -> Optional[Dict]:
        """Crea un release en GitHub (requiere token)."""
        if not self.token or not PYGithub_AVAILABLE:
            print("Token no disponible para crear release")
            return None
        
        try:
            g = Github(self.token)
            repo = g.get_repo(self._get_repo_name())
            
            release = repo.create_git_release(
                tag=tag,
                title=title,
                message=description,
                draft=False,
                prerelease=False
            )
            
            return {
                'tag': tag,
                'url': release.html_url,
                'id': release.id
            }
            
        except Exception as e:
            print(f"Error creando release: {e}")
            return None


class GitHubManager:
    """Gestor avanzado de GitHub con API."""
    
    def __init__(self, token: str):
        if not PYGithub_AVAILABLE:
            raise ImportError("PyGithub requerido")
        
        self.g = Github(token)
        self.repo = None
    
    def set_repo(self, repo_name: str):
        """Selecciona repositorio."""
        self.repo = self.g.get_repo(repo_name)
    
    def upload_file(self, 
                   file_path: str,
                   repo_path: str,
                   message: str,
                   branch: str = "main") -> bool:
        """Sube un archivo directamente via API."""
        if not self.repo:
            print("Repositorio no seleccionado")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            self.repo.create_file(
                path=repo_path,
                message=message,
                content=content,
                branch=branch
            )
            
            print(f"Archivo subido: {repo_path}")
            return True
            
        except GithubException as e:
            print(f"Error: {e}")
            return False
    
    def list_releases(self) -> List[Dict]:
        """Lista releases del repositorio."""
        if not self.repo:
            return []
        
        releases = []
        for r in self.repo.get_releases():
            releases.append({
                'tag': r.tag_name,
                'title': r.title,
                'url': r.html_url
            })
        
        return releases


def upload_to_github(
    files: List[str],
    repo_path: str = ".",
    commit_message: str = "Add: Video360 detection data",
    push: bool = True
) -> bool:
    """
    Función de conveniencia para subir archivos.
    
    Uso:
    ----
    >>> upload_to_github(
    ...     files=["./shapefile/detections.shp", "./detections.geojson"],
    ...     commit_message="Nuevas detecciones"
    ... )
    """
    uploader = GitHubUploader(
        repo_path=repo_path,
        commit_message=commit_message
    )
    
    return uploader.upload_all(files, push=push)


if __name__ == "__main__":
    print("GitHub Uploader listo.")
    print("Uso: upload_to_github(files, repo_path)")
