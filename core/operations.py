import os
import shutil
from pathlib import Path


class Operations:

    def copy(self, source: str, destination: str) -> dict:
        src = Path(source)
        dst = Path(destination)

        if not src.exists():
            return {"ok": False, "error": f"No existe: {source}"}

        try:
            if dst.is_dir():
                dst = dst / src.name

            if dst.exists():
                return {"ok": False, "error": f"Ya existe: {dst.name}"}

            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

            return {"ok": True, "result": str(dst)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def move(self, source: str, destination: str) -> dict:
        src = Path(source)
        dst = Path(destination)

        if not src.exists():
            return {"ok": False, "error": f"No existe: {source}"}

        try:
            if dst.is_dir():
                dst = dst / src.name

            if dst.exists():
                return {"ok": False, "error": f"Ya existe: {dst.name}"}

            shutil.move(str(src), str(dst))
            return {"ok": True, "result": str(dst)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def rename(self, source: str, new_name: str) -> dict:
        src = Path(source)

        if not src.exists():
            return {"ok": False, "error": f"No existe: {source}"}

        if not new_name.strip():
            return {"ok": False, "error": "El nombre no puede estar vacío"}

        if os.sep in new_name or "/" in new_name:
            return {"ok": False, "error": "El nombre no puede contener separadores"}

        dst = src.parent / new_name

        if dst.exists():
            return {"ok": False, "error": f"Ya existe: {new_name}"}

        try:
            src.rename(dst)
            return {"ok": True, "result": str(dst)}

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete(self, path: str) -> dict:
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

    def create_folder(self, parent_path: str, folder_name: str) -> dict:
        if not folder_name.strip():
            return {"ok": False, "error": "El nombre no puede estar vacío"}

        if os.sep in folder_name or "/" in folder_name:
            return {"ok": False, "error": "El nombre no puede contener separadores"}

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

    def create_file(self, parent_path: str, file_name: str) -> dict:
        if not file_name.strip():
            return {"ok": False, "error": "El nombre no puede estar vacío"}

        if os.sep in file_name or "/" in file_name:
            return {"ok": False, "error": "El nombre no puede contener separadores"}

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