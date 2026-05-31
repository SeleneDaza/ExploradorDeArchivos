import os
import sys
import stat
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from ui.theme import DARK, btn_qss, global_qss, R_SM


def _get_owner_group(st) -> tuple:
    """Returns (owner, group) strings, cross-platform."""
    if sys.platform == "win32":
        try:
            import win32security
            sd = win32security.GetFileSecurity(
                ..., win32security.OWNER_SECURITY_INFORMATION
            )
        except Exception:
            pass
        try:
            owner = os.getlogin()
        except Exception:
            owner = "N/A"
        return owner, "N/A"
    else:
        import pwd, grp
        try:
            owner = pwd.getpwuid(st.st_uid).pw_name
        except KeyError:
            owner = str(st.st_uid)
        try:
            group = grp.getgrgid(st.st_gid).gr_name
        except KeyError:
            group = str(st.st_gid)
        return owner, group


def _symbolic(mode: int) -> str:
    flags = [
        (stat.S_IRUSR, "r"), (stat.S_IWUSR, "w"), (stat.S_IXUSR, "x"),
        (stat.S_IRGRP, "r"), (stat.S_IWGRP, "w"), (stat.S_IXGRP, "x"),
        (stat.S_IROTH, "r"), (stat.S_IWOTH, "w"), (stat.S_IXOTH, "x"),
    ]
    return "".join(c if mode & f else "-" for f, c in flags)


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _fmt_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y  %H:%M:%S")


_EXT_NAMES = {
    ".py": "Script Python", ".js": "Script JavaScript", ".ts": "TypeScript",
    ".txt": "Texto plano", ".md": "Markdown", ".pdf": "PDF",
    ".jpg": "Imagen JPEG", ".jpeg": "Imagen JPEG", ".png": "Imagen PNG",
    ".gif": "Imagen GIF", ".webp": "Imagen WebP",
    ".zip": "Archivo ZIP", ".tar": "Archivo TAR", ".gz": "Archivo GZ",
    ".csv": "Datos CSV", ".json": "JSON", ".xml": "XML",
    ".html": "HTML", ".css": "CSS", ".sh": "Script Shell",
    ".c": "Código C", ".cpp": "Código C++", ".java": "Código Java",
    ".mp4": "Video MP4", ".mp3": "Audio MP3", ".wav": "Audio WAV",
}


class PropertiesDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._T = DARK
        self.path = Path(path)
        self.setWindowTitle(f"Propiedades — {self.path.name}")
        self.setMinimumWidth(440)
        self.setStyleSheet(global_qss(self._T))
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        group = QGroupBox("Información general")
        grid = QGridLayout(group)
        grid.setSpacing(10)
        grid.setColumnMinimumWidth(0, 110)

        st = self.path.stat()
        owner, group_name = _get_owner_group(st)

        tipo = (
            "Carpeta"
            if self.path.is_dir()
            else _EXT_NAMES.get(self.path.suffix.lower(), f"Archivo {self.path.suffix}")
        )
        size = _fmt_size(st.st_size) if self.path.is_file() else self._dir_size()

        rows = [
            ("Nombre:",      self.path.name),
            ("Tipo:",        tipo),
            ("Ubicación:",   str(self.path.parent)),
            ("Tamaño:",      size),
            ("Modificado:",  _fmt_ts(st.st_mtime)),
            ("Creado:",      _fmt_ts(st.st_ctime)),
            ("Propietario:", owner),
            ("Grupo:",       group_name),
            ("Permisos:",    f"{_symbolic(st.st_mode)}  ({oct(st.st_mode)[-3:]})"),
        ]

        T = self._T
        for i, (label, value) in enumerate(rows):
            key = QLabel(label)
            key.setStyleSheet(
                f"color:{T['text_dim']}; font-weight:600; font-size:12px;"
            )
            val = QLabel(value)
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            val.setStyleSheet(f"color:{T['text']}; font-size:13px;")
            grid.addWidget(key, i, 0, Qt.AlignTop)
            grid.addWidget(val, i, 1, Qt.AlignTop)

        root.addWidget(group)

        btn_row = QHBoxLayout()
        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(34)
        btn_close.setStyleSheet(btn_qss(T))
        btn_close.clicked.connect(self.close)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _dir_size(self) -> str:
        try:
            total = sum(f.stat().st_size for f in self.path.rglob("*") if f.is_file())
            return _fmt_size(total)
        except Exception:
            return "—"
