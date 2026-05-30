from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from pathlib import Path
import os
import pwd
import grp
import stat
from datetime import datetime

DARK = {
    "bg":      "#1e1e2e",
    "accent":  "#cba6f7",
    "text":    "#cdd6f4",
    "text_dim":"#6c7086",
    "hover":   "#313244",
    "border":  "#313244",
    "panel":   "#24243e",
}


class PropertiesDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = Path(path)
        self.setWindowTitle(f"Propiedades — {self.path.name}")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"""
            QDialog {{ background: {DARK['bg']}; color: {DARK['text']}; }}
            QGroupBox {{
                color: {DARK['accent']};
                border: 1px solid {DARK['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding: 8px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
            QLabel {{ color: {DARK['text']}; font-size: 13px; }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ── info general ─────────────────────────────────────
        info_group = QGroupBox("General")
        grid = QGridLayout(info_group)
        grid.setSpacing(8)

        st = self.path.stat()

        tipo = "Carpeta" if self.path.is_dir() else self._get_type()
        size = self._format_size(st.st_size) if self.path.is_file() else self._dir_size()
        modified = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        created  = datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S")

        try:
            owner = pwd.getpwuid(st.st_uid).pw_name
        except KeyError:
            owner = str(st.st_uid)

        try:
            group = grp.getgrgid(st.st_gid).gr_name
        except KeyError:
            group = str(st.st_gid)

        mode = st.st_mode
        symbolic = self._to_symbolic(mode)
        octal    = oct(mode)[-3:]

        rows = [
            ("Nombre:",       self.path.name),
            ("Tipo:",         tipo),
            ("Ubicación:",    str(self.path.parent)),
            ("Tamaño:",       size),
            ("Modificado:",   modified),
            ("Creado:",       created),
            ("Propietario:",  owner),
            ("Grupo:",        group),
            ("Permisos:",     f"{symbolic}  ({octal})"),
        ]

        for i, (label, value) in enumerate(rows):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {DARK['text_dim']}; font-weight: bold;")
            val = QLabel(value)
            val.setWordWrap(True)
            grid.addWidget(lbl, i, 0, Qt.AlignTop)
            grid.addWidget(val, i, 1, Qt.AlignTop)

        layout.addWidget(info_group)

        # botón cerrar
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(32)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: {DARK['hover']};
                color: {DARK['text']};
                border: none;
                border-radius: 6px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {DARK['accent']};
                color: {DARK['bg']};
            }}
        """)
        btn_close.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _get_type(self):
        ext = self.path.suffix.lower()
        types = {
            ".py": "Script Python", ".js": "Script JavaScript",
            ".txt": "Texto plano", ".md": "Markdown",
            ".pdf": "PDF", ".jpg": "Imagen JPEG",
            ".png": "Imagen PNG", ".zip": "Archivo ZIP",
            ".tar": "Archivo TAR", ".gz": "Archivo GZ",
            ".csv": "Datos CSV", ".json": "JSON",
            ".html": "HTML", ".css": "CSS",
            ".sh": "Script Shell", ".c": "Código C",
            ".cpp": "Código C++", ".java": "Código Java",
        }
        return types.get(ext, f"Archivo {ext}" if ext else "Archivo")

    def _dir_size(self):
        try:
            total = sum(
                f.stat().st_size
                for f in self.path.rglob("*")
                if f.is_file()
            )
            return self._format_size(total)
        except:
            return "—"

    @staticmethod
    def _format_size(size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024**2:.1f} MB"
        else:
            return f"{size / 1024**3:.1f} GB"

    @staticmethod
    def _to_symbolic(mode):
        flags = [
            (stat.S_IRUSR,'r'),(stat.S_IWUSR,'w'),(stat.S_IXUSR,'x'),
            (stat.S_IRGRP,'r'),(stat.S_IWGRP,'w'),(stat.S_IXGRP,'x'),
            (stat.S_IROTH,'r'),(stat.S_IWOTH,'w'),(stat.S_IXOTH,'x'),
        ]
        return "".join(c if mode & f else '-' for f, c in flags)