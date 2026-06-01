from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea,
    QWidget, QFrame,
)
from PyQt5.QtCore import Qt

from core.personalizer import Personalizer, COLORS, BADGES
from ui.theme import global_qss, S


class MyPersonalizationsDialog(QDialog):
    def __init__(self, T: dict, on_navigate=None, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self._T           = T
        self._p           = Personalizer()
        self._on_navigate = on_navigate
        self.setWindowTitle("Mis Personalizaciones")
        self.setMinimumSize(S(520), S(460))
        self.setStyleSheet(global_qss(T))
        self._build()

    def _build(self):
        T    = self._T
        root = QVBoxLayout(self)
        root.setContentsMargins(S(20), S(16), S(20), S(16))
        root.setSpacing(S(12))

        # título + botón limpiar todo
        top = QHBoxLayout()
        title = QLabel("Personalizaciones guardadas")
        title.setStyleSheet(
            f"color:{T['text']}; font-size:{S(14)}px; font-weight:700;"
        )
        top.addWidget(title)
        top.addStretch()

        clear_all = QPushButton("Limpiar todo")
        clear_all.setFixedHeight(S(30))
        clear_all.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{T['warning']};"
            f"border:1.5px solid {T['warning']}; border-radius:{S(6)}px;"
            f"font-size:{S(12)}px; padding:0 {S(10)}px; }}"
            f"QPushButton:hover {{ background:{T['warning']}; color:{T['bg']}; }}"
        )
        clear_all.clicked.connect(self._clear_all)
        top.addWidget(clear_all)
        root.addLayout(top)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{T['border']};")
        root.addWidget(sep)

        # área scrollable con las filas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;")

        self._content = QWidget()
        self._content.setStyleSheet("background:transparent;")
        self._rows_lay = QVBoxLayout(self._content)
        self._rows_lay.setContentsMargins(0, 0, 0, 0)
        self._rows_lay.setSpacing(S(4))

        scroll.setWidget(self._content)
        root.addWidget(scroll, 1)

        # botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setFixedHeight(S(34))
        close_btn.setMinimumWidth(S(90))
        close_btn.setStyleSheet(
            f"QPushButton {{ background:{T['accent']}; color:{T['bg']};"
            f"border:none; border-radius:{S(7)}px; font-size:{S(13)}px;"
            f"padding:{S(4)}px {S(14)}px; }}"
            f"QPushButton:hover {{ background:{T['accent2']}; color:{T['bg']}; }}"
        )
        close_btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(close_btn)
        root.addLayout(row)

        self._refresh()

    # ── renderizar filas ──────────────────────────────────────

    def _refresh(self):
        T = self._T
        # limpiar filas anteriores
        while self._rows_lay.count():
            item = self._rows_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self._p.all_personalized()
        if not items:
            empty = QLabel("No hay personalizaciones guardadas.")
            empty.setStyleSheet(
                f"color:{T['text_dim']}; font-size:{S(13)}px; padding:{S(20)}px;"
            )
            empty.setAlignment(Qt.AlignCenter)
            self._rows_lay.addWidget(empty)
        else:
            for path, data in sorted(items, key=lambda x: Path(x[0]).name.lower()):
                self._rows_lay.addWidget(self._make_row(path, data))

        self._rows_lay.addStretch()

    def _make_row(self, path: str, data: dict) -> QWidget:
        T   = self._T
        row = QWidget()
        row.setStyleSheet(
            f"background:{T['surface']}; border-radius:{S(8)}px;"
        )
        lay = QHBoxLayout(row)
        lay.setContentsMargins(S(12), S(8), S(8), S(8))
        lay.setSpacing(S(10))

        # punto de color
        color_key = data.get("color")
        dot = QLabel()
        dot.setFixedSize(S(12), S(12))
        if color_key and color_key in COLORS:
            hex_c, _ = COLORS[color_key]
            dot.setStyleSheet(
                f"background:{hex_c}; border-radius:{S(6)}px;"
            )
        else:
            dot.setStyleSheet(
                f"background:{T['border']}; border-radius:{S(6)}px;"
            )
        lay.addWidget(dot)

        # nombre + ruta
        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(Path(path).name)
        name_lbl.setStyleSheet(
            f"color:{T['text']}; font-size:{S(13)}px; font-weight:600;"
            f"background:transparent;"
        )
        path_lbl = QLabel(path)
        path_lbl.setStyleSheet(
            f"color:{T['text_dim']}; font-size:{S(11)}px; background:transparent;"
        )
        path_lbl.setWordWrap(False)
        info.addWidget(name_lbl)
        info.addWidget(path_lbl)
        lay.addLayout(info, 1)

        # insignia texto
        badge_key = data.get("badge")
        if badge_key and badge_key in BADGES:
            sym, label = BADGES[badge_key]
            b_lbl = QLabel(f"{sym} {label}")
            b_lbl.setStyleSheet(
                f"color:{T['text_sub']}; font-size:{S(11)}px; background:transparent;"
            )
            lay.addWidget(b_lbl)

        # acción ir a ubicación
        if self._on_navigate:
            go_btn = QPushButton("Ir")
            go_btn.setFixedSize(S(40), S(26))
            go_btn.setToolTip("Navegar a la carpeta")
            go_btn.setStyleSheet(
                f"QPushButton {{ background:{T['overlay']}; color:{T['text_sub']};"
                f"border:none; border-radius:{S(5)}px; font-size:{S(11)}px; }}"
                f"QPushButton:hover {{ background:{T['accent']}; color:{T['bg']}; }}"
            )
            _p = path
            go_btn.clicked.connect(
                lambda _, p=_p: (
                    self._on_navigate(str(Path(p).parent)), self.accept()
                )
            )
            lay.addWidget(go_btn)

        # limpiar
        del_btn = QPushButton("×")
        del_btn.setFixedSize(S(28), S(26))
        del_btn.setToolTip("Quitar personalización")
        del_btn.setStyleSheet(
            f"QPushButton {{ background:{T['overlay']}; color:{T['text_dim']};"
            f"border:none; border-radius:{S(5)}px; font-size:{S(13)}px; }}"
            f"QPushButton:hover {{ background:{T['warning']}; color:{T['bg']}; }}"
        )
        _p = path
        del_btn.clicked.connect(lambda _, p=_p: self._remove(p))
        lay.addWidget(del_btn)

        return row

    # ── acciones ──────────────────────────────────────────────

    def _remove(self, path: str):
        self._p.clear(path)
        self._refresh()

    def _clear_all(self):
        for path, _ in self._p.all_personalized():
            self._p.clear(path)
        self._refresh()
