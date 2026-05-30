import os
import stat
import pwd
import grp
from pathlib import Path


class Permissions:

    def get_info(self, path: str) -> dict:
        target = Path(path)

        if not target.exists():
            return {"ok": False, "error": f"No existe: {path}"}

        try:
            st = target.stat()
            mode = st.st_mode

            try:
                owner = pwd.getpwuid(st.st_uid).pw_name
            except KeyError:
                owner = str(st.st_uid)

            try:
                group = grp.getgrgid(st.st_gid).gr_name
            except KeyError:
                group = str(st.st_gid)

            return {
                "ok":       True,
                "path":     str(target),
                "owner":    owner,
                "group":    group,
                "uid":      st.st_uid,
                "gid":      st.st_gid,
                "octal":    oct(mode)[-3:],
                "symbolic": self._to_symbolic(mode),
                "bits": {
                    "owner": {
                        "read":    bool(mode & stat.S_IRUSR),
                        "write":   bool(mode & stat.S_IWUSR),
                        "execute": bool(mode & stat.S_IXUSR),
                    },
                    "group": {
                        "read":    bool(mode & stat.S_IRGRP),
                        "write":   bool(mode & stat.S_IWGRP),
                        "execute": bool(mode & stat.S_IXGRP),
                    },
                    "others": {
                        "read":    bool(mode & stat.S_IROTH),
                        "write":   bool(mode & stat.S_IWOTH),
                        "execute": bool(mode & stat.S_IXOTH),
                    },
                }
            }

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def chmod(self, path: str, octal: str) -> dict:
        target = Path(path)

        if not target.exists():
            return {"ok": False, "error": f"No existe: {path}"}

        if not self._valid_octal(octal):
            return {"ok": False, "error": f"Octal inválido: {octal}"}

        try:
            os.chmod(path, int(octal, 8))
            return {
                "ok":       True,
                "result":   f"Permisos cambiados a {octal}",
                "new_info": self.get_info(path),
            }

        except PermissionError:
            return {"ok": False, "error": "Permiso denegado"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def chmod_from_bits(self, path: str, bits: dict) -> dict:
        try:
            mode = 0
            mapping = {
                "owner":  (stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR),
                "group":  (stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP),
                "others": (stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH),
            }
            for who, flags in mapping.items():
                r, w, x = flags
                if bits.get(who, {}).get("read"):    mode |= r
                if bits.get(who, {}).get("write"):   mode |= w
                if bits.get(who, {}).get("execute"): mode |= x

            return self.chmod(path, oct(mode)[-3:])

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def chown(self, path: str, owner: str = None, group: str = None) -> dict:
        target = Path(path)

        if not target.exists():
            return {"ok": False, "error": f"No existe: {path}"}

        if not owner and not group:
            return {"ok": False, "error": "Debes especificar owner, group o ambos"}

        try:
            uid = pwd.getpwnam(owner).pw_uid if owner else -1
            gid = grp.getgrnam(group).gr_gid if group else -1
            os.chown(path, uid, gid)
            return {
                "ok":       True,
                "result":   f"Propietario cambiado → {owner or 'sin cambio'}:{group or 'sin cambio'}",
                "new_info": self.get_info(path),
            }

        except KeyError as e:
            return {"ok": False, "error": f"Usuario o grupo no existe: {e}"}
        except PermissionError:
            return {"ok": False, "error": "Permiso denegado — necesitas ser root"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    def _to_symbolic(mode: int) -> str:
        flags = [
            (stat.S_IRUSR, 'r'), (stat.S_IWUSR, 'w'), (stat.S_IXUSR, 'x'),
            (stat.S_IRGRP, 'r'), (stat.S_IWGRP, 'w'), (stat.S_IXGRP, 'x'),
            (stat.S_IROTH, 'r'), (stat.S_IWOTH, 'w'), (stat.S_IXOTH, 'x'),
        ]
        return "".join(c if mode & f else '-' for f, c in flags)

    @staticmethod
    def _valid_octal(octal: str) -> bool:
        return len(octal) in (3, 4) and all(c in "01234567" for c in octal)