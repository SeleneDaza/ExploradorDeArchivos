"""
Hilo de búsqueda recursiva por nombre de archivo.
Emite cada resultado conforme lo encuentra para actualizar la UI en tiempo real.
"""
import os # módulo para interactuar con el SO
from PyQt5.QtCore import QThread, pyqtSignal

# carpetas que se omiten durante la búsqueda para no perder tiempo
# son carpetas del sistema o de herramientas que no interesan al usuario
_SKIP = {
    "__pycache__", "node_modules", ".git", ".svn", ".hg",
    "$RECYCLE.BIN", "System Volume Information", ".idea",
}


class SearchWorker(QThread):
    result_found = pyqtSignal(dict)
    finished     = pyqtSignal(int)      # total de resultados encontrados

    MAX_RESULTS = 500

    def __init__(self, query: str, root: str):
        super().__init__()
        self._query = query.lower()
        self._root  = root
        self._stop  = False

    def run(self):
        count = 0
        # os.walk() equivale a "find /ruta -name archivo" en Linux
        # recorre recursivamente todas las carpetas y subcarpetas
        # devuelve: dirpath (ruta actual), dirs (subcarpetas), files (archivos)
        for dirpath, dirs, files in os.walk(self._root):
            if self._stop:
                break
            # filtra carpetas ocultas (que empiezan con ".") y las de _SKIP
            # en Linux las carpetas ocultas empiezan con "." ejemplo: .git, .ssh
            dirs[:] = [d for d in dirs
                       if not d.startswith('.') and d not in _SKIP]
            for name in dirs + files:
                if self._stop:
                    break
                if self._query in name.lower():
                    # os.path.join() construye la ruta completa del archivo
                    # equivale a concatenar rutas: /home/user + archivo.txt
                    full = os.path.join(dirpath, name)
                    try:
                        # os.stat() equivale a "stat archivo" en Linux
                        # lee los metadatos del archivo: tamaño, fecha de modificación
                        st = os.stat(full)
                        self.result_found.emit({
                            "name":   name,
                            "path":   full,
                            "size":   st.st_size,
                            # os.path.isdir() equivale a "test -d ruta" en Linux
                            # verifica si es una carpeta
                            "is_dir": os.path.isdir(full),
                            "mtime":  st.st_mtime,
                        })
                        count += 1
                        if count >= self.MAX_RESULTS:
                            break
                    except Exception:
                        pass
            if count >= self.MAX_RESULTS:
                break
        self.finished.emit(count)

    def stop(self):
        self._stop = True
