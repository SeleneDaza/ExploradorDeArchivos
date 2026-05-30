from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from pathlib import Path

DARK = {
    "bg":      "#181825",
    "accent":  "#cba6f7",
    "accent2": "#89b4fa",
    "text":    "#cdd6f4",
    "text_dim":"#6c7086",
    "hover":   "#313244",
    "border":  "#313244",
}

DEFAULT_FAVORITES = [
    ("⌂  Home",       str(Path.home())),
    ("📄  Documentos", str(Path.home() / "Documents")),
    ("⬇  Descargas",  str(Path.home() / "Downloads")),
    ("🖼  Imágenes",   str(Path.home() / "Pictures")),
    ("💻  Raíz",       "/"),
    ("⚙  etc",        "/etc"),
    ("📦  var",        "/var"),
]


class FavoritesPanel(QWidget):
    path_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(180)
        self.setStyleSheet(f"background: {DARK['bg']};")
        self.favorites = list(DEFAULT_FAVORITES)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)

        title = QLabel("  Favoritos")
        title.setStyleSheet(f"""
            color: {DARK['text_dim']};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {DARK['border']}; max-height: 1px; margin: 4px 0;")
        layout.addWidget(line)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(2)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        btn_add = QPushButton("＋  Agregar actual")
        btn_add.setFixedHeight(28)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {DARK['accent']};
                border: 1px solid {DARK['accent']};
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {DARK['accent']};
                color: {DARK['bg']};
            }}
        """)
        btn_add.clicked.connect(self.add_requested)
        layout.addWidget(btn_add)

        self._refresh_buttons()

    def _refresh_buttons(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for name, path in self.favorites:
            btn = QPushButton(name)
            btn.setFixedHeight(32)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {DARK['text']};
                    text-align: left;
                    padding: 0 8px;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    background: transparent;
                }}
                QPushButton:hover {{
                    background: {DARK['hover']};
                    color: {DARK['accent']};
                }}
            """)
            _path = path
            btn.clicked.connect(lambda _, p=_path: self.path_selected.emit(p))
            self.container_layout.addWidget(btn)

        self.container_layout.addStretch()

    def add_favorite(self, path: str):
        name = f"📁  {Path(path).name or path}"
        if (name, path) not in self.favorites:
            self.favorites.append((name, path))
            self._refresh_buttons()

    def add_requested(self):
        self.path_selected.emit("__add_current__")