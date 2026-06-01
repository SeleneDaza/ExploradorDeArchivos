import os
import sys
import shutil
import subprocess
from pathlib import Path


class Operations:

    def sudo_run(self, cmd: list[str], password: str) -> dict:
        """Ejecuta cmd con sudo -S en Linux, pasando la contraseña por stdin."""
        if sys.platform != "linux":
            return {"ok": False, "error": "Elevación de privilegios solo disponible en Linux"}
        try:
            r = subprocess.run(
                ["sudo", "-S", "--"] + cmd,
                input=password + "\n",
                capture_output=True,
                text=True,
                timeout=15,
            )
            if r.returncode == 0:
                return {"ok": True, "result": "Operación completada con privilegios de administrador"}
            stderr = r.stderr.lower()
            if any(x in stderr for x in ("incorrect password", "wrong password",
                                          "authentication failure", "no password")):
                return {"ok": False, "error": "Contraseña incorrecta"}
            return {"ok": False, "error": (r.stderr.strip() or "Error al ejecutar con sudo")}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Tiempo de espera agotado"}
        except FileNotFoundError:
            return {"ok": False, "error": "sudo no encontrado en el sistema"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

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
            cmd = ["cp", "-r", str(src), str(dst)] if src.is_dir() else ["cp", str(src), str(dst)]
            return {"ok": False, "error": "Permiso denegado", "needs_sudo": True, "sudo_cmd": cmd}
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
            return {"ok": False, "error": "Permiso denegado", "needs_sudo": True,
                    "sudo_cmd": ["mv", str(src), str(dst)]}
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
            return {"ok": False, "error": "Permiso denegado", "needs_sudo": True,
                    "sudo_cmd": ["mv", str(src), str(dst)]}
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
            cmd = ["rm", "-rf", str(target)] if target.is_dir() else ["rm", str(target)]
            return {"ok": False, "error": "Permiso denegado", "needs_sudo": True, "sudo_cmd": cmd}
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
            return {"ok": False, "error": "Permiso denegado", "needs_sudo": True,
                    "sudo_cmd": ["mkdir", str(target)]}
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
            return {"ok": False, "error": "Permiso denegado", "needs_sudo": True,
                    "sudo_cmd": ["touch", str(target)]}
        except Exception as e:
            return {"ok": False, "error": str(e)}