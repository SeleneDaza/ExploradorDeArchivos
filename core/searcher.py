"""
Hilo de búsqueda recursiva por nombre de archivo.
Emite cada resultado conforme lo encuentra para actualizar la UI en tiempo real.
"""
import os
from PyQt5.QtCore import QThread, pyqtSignal

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
        for dirpath, dirs, files in os.walk(self._root):
            if self._stop:
                break
            dirs[:] = [d for d in dirs
                       if not d.startswith('.') and d not in _SKIP]
            for name in dirs + files:
                if self._stop:
                    break
                if self._query in name.lower():
                    full = os.path.join(dirpath, name)
                    try:
                        st = os.stat(full)
                        self.result_found.emit({
                            "name":   name,
                            "path":   full,
                            "size":   st.st_size,
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
