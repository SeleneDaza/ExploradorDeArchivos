from pathlib import Path


class FileSystem:
    def __init__(self):
        # Path.home() equivale a "cd ~" en Linux
        # obtiene la carpeta del usuario actual
        self.current_path = Path.home()

    def get_current_path(self):
        # retorna la ruta actual como texto
        return str(self.current_path)

    def navigate_to(self, path: str):
        target = Path(path)
        # Path.exists() equivale a "test -e ruta" en Linux
        # verifica si la ruta existe en el sistema de archivos
        # Path.is_dir() equivale a "test -d ruta" en Linux
        # verifica si la ruta es una carpeta (no un archivo)
        if target.exists() and target.is_dir():
            self.current_path = target
            return True
        return False

    def go_up(self):
        # Path.parent equivale a "cd .." en Linux
        # obtiene la carpeta que contiene a la carpeta actual
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            return True
        return False

    def get_home(self):
        # Path.home() equivale a "echo $HOME" en Linux
        # retorna siempre la carpeta del usuario
        return str(Path.home())

    def get_root(self):
        # Retorna la raíz del sistema de archivos.
        # En Windows devuelve la unidad actual (ej: 'C:\\'), en POSIX '/'.
        try:
            anchor = Path(self.current_path).anchor
            if anchor:
                return str(anchor)
        except Exception:
            pass
        return "/"