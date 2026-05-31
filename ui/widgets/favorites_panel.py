from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from pathlib import Path
from ui.theme import DARK, FONT_UI, btn_qss, R_XS, R_SM

_T = DARK

DEFAULT_FAVORITES = [
    ("⌂  Home",        str(Path.home())),
    ("📄  Documentos",  str(Path.home() / "Documents")),
    ("⬇  Descargas",   str(Path.home() / "Downloads")),
    ("🖼  Imágenes",    str(Path.home() / "Pictures")),
    ("💻  Raíz",        "/"),
]


class FavoritesPanel(QWidget):
    path_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(186)
        self.favorites = list(DEFAULT_FAVORITES)
        self._build_ui()
        self.set_theme(_T)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 14, 8, 10)
        lay.setSpacing(4)

        # título de sección
        self._title = QLabel("FAVORITOS")
        lay.addWidget(self._title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        self._sep = line
        lay.addWidget(line)

        # lista scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent;")

        self._container = QWidget()
        self._container.setStyleSheet("background:transparent;")
        self._cl = QVBoxLayout(self._container)
        self._cl.setContentsMargins(0, 0, 0, 0)
        self._cl.setSpacing(2)
        scroll.setWidget(self._container)
        lay.addWidget(scroll)

        self._btn_add = QPushButton("＋  Agregar carpeta actual")
        self._btn_add.setFixedHeight(30)
        self._btn_add.clicked.connect(lambda: self.path_selected.emit("__add_current__"))
        lay.addWidget(self._btn_add)

        self._refresh_buttons()

    def set_theme(self, T: dict):
        global _T
        _T = T
        self.setStyleSheet(f"background:{T['surface']}; border-right:1px solid {T['border']};")
        self._title.setStyleSheet(
            f"color:{T['text_dim']}; font-size:10px; font-weight:700;"
            f"letter-spacing:1.2px; padding-left:4px;"
        )
        self._sep.setStyleSheet(f"background:{T['border']};")
        self._btn_add.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {T['accent']};
                border: 1px solid {T['accent']};
                border-radius: {R_SM}px;
                font-size: 12px;
                padding: 3px 6px;
            }}
            QPushButton:hover {{ background: {T['accent']}; color: {T['bg']}; }}
        """)
        self._refresh_buttons()

    def _refresh_buttons(self):
        T = _T
        while self._cl.count():
            item = self._cl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for name, path in self.favorites:
            btn = QPushButton(name)
            btn.setFixedHeight(32)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(path)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {T['text_sub']};
                    text-align: left;
                    padding: 0 10px;
                    border: none;
                    border-radius: {R_XS}px;
                    font-size: 13px;
                    background: transparent;
                }}
                QPushButton:hover {{
                    background: {T['overlay']};
                    color: {T['text']};
                }}
                QPushButton:pressed {{
                    background: {T['sel_bg']};
                    color: {T['sel_text']};
                }}
            """)
            _path = path
            btn.clicked.connect(lambda _, p=_path: self.path_selected.emit(p))
            self._cl.addWidget(btn)

        self._cl.addStretch()

    def add_favorite(self, path: str):
        name = f"📁  {Path(path).name or path}"
        if (name, path) not in self.favorites:
            self.favorites.append((name, path))
            self._refresh_buttons()

    def add_requested(self):
        self.path_selected.emit("__add_current__")
