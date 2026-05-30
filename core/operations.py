import os
import shutil
from pathlib import Path


class Operations:

    # ── COPIAR ──────────────────────────────────────────────────────────────

    def copy(self, source: str, destination: str) -> dict:
        """
        Copia archivo o carpeta.
        Si destination es un directorio existente, copia dentro de él.
        """
        src = Path(source)
        dst = Path(destination)

        if not src.exists():
            return {"ok": False, "error": f"No existe: {source}"}

        try:
            # si el destino es carpeta existente, construye la ruta final
            if dst.is_dir():
                dst = dst / src.name

            if dst.exists():
                return {"ok": False, "error": f"Ya existe en destino: {dst.name}"}

            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

            return {"ok": True, "result": str(dst)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── MOVER ───────────────────────────────────────────────────────────────

    def move(self, source: str, destination: str) -> dict:
        """
        Mueve archivo o carpeta.
        Si destination es directorio existente, mueve dentro de él.
        """
        src = Path(source)
        dst = Path(destination)

        if not src.exists():
            return {"ok": False, "error": f"No existe: {source}"}

        try:
            if dst.is_dir():
                dst = dst / src.name

            if dst.exists():
                return {"ok": False, "error": f"Ya existe en destino: {dst.name}"}

            shutil.move(str(src), str(dst))
            return {"ok": True, "result": str(dst)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── RENOMBRAR ───────────────────────────────────────────────────────────

    def rename(self, source: str, new_name: str) -> dict:
        """
        Renombra un archivo o carpeta. new_name es solo el nombre, no la ruta.
        """
        src = Path(source)

        if not src.exists():
            return {"ok": False, "error": f"No existe: {source}"}

        # evita que pasen rutas completas como nuevo nombre
        if os.sep in new_name or "/" in new_name:
            return {"ok": False, "error": "El nuevo nombre no puede contener separadores de ruta"}

        if not new_name.strip():
            return {"ok": False, "error": "El nombre no puede estar vacío"}

        dst = src.parent / new_name

        if dst.exists():
            return {"ok": False, "error": f"Ya existe un archivo con ese nombre: {new_name}"}

        try:
            src.rename(dst)
            return {"ok": True, "result": str(dst)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── ELIMINAR ────────────────────────────────────────────────────────────

    def delete(self, path: str) -> dict:
        """
        Elimina archivo o carpeta (recursivo si es carpeta).
        """
        target = Path(path)

        if not target.exists():
            return {"ok": False, "error": f"No existe: {path}"}

        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

            return {"ok": True, "result": f"Eliminado: {target.name}"}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── CREAR CARPETA ────────────────────────────────────────────────────────

    def create_folder(self, parent_path: str, folder_name: str) -> dict:
        """
        Crea una carpeta nueva dentro de parent_path.
        """
        if not folder_name.strip():
            return {"ok": False, "error": "El nombre no puede estar vacío"}

        if os.sep in folder_name or "/" in folder_name:
            return {"ok": False, "error": "El nombre no puede contener separadores de ruta"}

        target = Path(parent_path) / folder_name

        if target.exists():
            return {"ok": False, "error": f"Ya existe: {folder_name}"}

        try:
            target.mkdir(parents=False, exist_ok=False)
            return {"ok": True, "result": str(target)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── CREAR ARCHIVO ────────────────────────────────────────────────────────

    def create_file(self, parent_path: str, file_name: str) -> dict:
        """
        Crea un archivo vacío dentro de parent_path.
        """
        if not file_name.strip():
            return {"ok": False, "error": "El nombre no puede estar vacío"}

        if os.sep in file_name or "/" in file_name:
            return {"ok": False, "error": "El nombre no puede contener separadores de ruta"}

        target = Path(parent_path) / file_name

        if target.exists():
            return {"ok": False, "error": f"Ya existe: {file_name}"}

        try:
            target.touch()
            return {"ok": True, "result": str(target)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}