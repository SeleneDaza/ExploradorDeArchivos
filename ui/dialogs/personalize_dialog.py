from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

from core.personalizer import Personalizer, COLORS, BADGES, _BADGE_COLORS
from ui.theme import global_qss, S


class PersonalizeDialog(QDialog):
    def __init__(self, path: str, T: dict, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self._path = path
        self._T    = T
        self._p    = Personalizer()
        self.setWindowTitle(f"Personalizar — {Path(path).name}")
        self.setMinimumWidth(S(420))
        self.setStyleSheet(global_qss(T))
        self._build()

    # ── construcción ─────────────────────────────────────────

    def _build(self):
        T    = self._T
        data = self._p.get(self._path)

        root = QVBoxLayout(self)
        root.setContentsMargins(S(24), S(20), S(24), S(20))
        root.setSpacing(S(18))

        # ── nombre del archivo ─────────────────────────────
        name_lbl = QLabel(Path(self._path).name)
        name_lbl.setStyleSheet(
            f"color:{T['text']}; font-size:{S(13)}px; font-weight:600;"
        )
        root.addWidget(name_lbl)

        root.addWidget(self._sep())

        # ── selector de color ──────────────────────────────
        color_title = QLabel("Etiqueta de color")
        color_title.setStyleSheet(
            f"color:{T['text_dim']}; font-size:{S(11)}px; font-weight:700;"
            f"letter-spacing:0.8px;"
        )
        root.addWidget(color_title)

        color_row = QHBoxLayout()
        color_row.setSpacing(S(6))
        self._color_btns: dict[str, QPushButton] = {}
        current_color = data.get("color")

        for key, (hex_c, label) in COLORS.items():
            b = QPushButton()
            b.setFixedSize(S(28), S(28))
            b.setToolTip(label)
            b.setCheckable(True)
            b.setChecked(key == current_color)
            b.setStyleSheet(self._color_btn_style(hex_c, key == current_color, T))
            b.clicked.connect(lambda _, k=key: self._on_color(k))
            color_row.addWidget(b)
            self._color_btns[key] = b

        # Botón "sin color"
        none_c = QPushButton("×")
        none_c.setFixedSize(S(28), S(28))
        none_c.setToolTip("Sin color")
        none_c.setCheckable(True)
        none_c.setChecked(not current_color)
        none_c.setStyleSheet(
            f"QPushButton {{ background:{T['overlay']}; color:{T['text_dim']};"
            f"border:2px solid {''+T['accent'] if not current_color else T['border']};"
            f"border-radius:{S(14)}px; font-size:{S(13)}px; }}"
            f"QPushButton:hover {{ border-color:{T['accent']}; }}"
        )
        none_c.clicked.connect(lambda: self._on_color(None))
        color_row.addWidget(none_c)
        self._none_color_btn = none_c
        color_row.addStretch()
        root.addLayout(color_row)

        root.addWidget(self._sep())

        # ── selector de insignia ───────────────────────────
        badge_title = QLabel("Insignia")
        badge_title.setStyleSheet(
            f"color:{T['text_dim']}; font-size:{S(11)}px; font-weight:700;"
            f"letter-spacing:0.8px;"
        )
        root.addWidget(badge_title)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(S(6))
        self._badge_btns: dict[str, QPushButton] = {}
        current_badge = data.get("badge")

        for key, (sym, label) in BADGES.items():
            b = QPushButton(sym)
            b.setFixedSize(S(36), S(32))
            b.setToolTip(label)
            b.setCheckable(True)
            b.setChecked(key == current_badge)
            b_col = _BADGE_COLORS.get(key, T["accent"])
            b.setStyleSheet(self._badge_btn_style(b_col, key == current_badge, T))
            b.clicked.connect(lambda _, k=key: self._on_badge(k))
            badge_row.addWidget(b)
            self._badge_btns[key] = b

        none_b = QPushButton("—")
        none_b.setFixedSize(S(36), S(32))
        none_b.setToolTip("Sin insignia")
        none_b.setCheckable(True)
        none_b.setChecked(not current_badge)
        none_b.setStyleSheet(
            f"QPushButton {{ background:{T['overlay']}; color:{T['text_dim']};"
            f"border:2px solid {''+T['accent'] if not current_badge else T['border']};"
            f"border-radius:{S(6)}px; font-size:{S(13)}px; }}"
            f"QPushButton:hover {{ border-color:{T['accent']}; }}"
        )
        none_b.clicked.connect(lambda: self._on_badge(None))
        badge_row.addWidget(none_b)
        self._none_badge_btn = none_b
        badge_row.addStretch()
        root.addLayout(badge_row)

        root.addWidget(self._sep())

        # ── botones de acción ──────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(S(8))

        clear_btn = QPushButton("Limpiar todo")
        clear_btn.setFixedHeight(S(34))
        clear_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{T['warning']};"
            f"border:1.5px solid {T['warning']}; border-radius:{S(7)}px;"
            f"font-size:{S(13)}px; padding:{S(4)}px {S(12)}px; }}"
            f"QPushButton:hover {{ background:{T['warning']}; color:{T['bg']}; }}"
        )
        clear_btn.clicked.connect(self._on_clear)

        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        done_btn = QPushButton("Cerrar")
        done_btn.setFixedHeight(S(34))
        done_btn.setMinimumWidth(S(90))
        done_btn.setDefault(True)
        done_btn.setStyleSheet(
            f"QPushButton {{ background:{T['accent']}; color:{T['bg']};"
            f"border:none; border-radius:{S(7)}px; font-size:{S(13)}px;"
            f"padding:{S(4)}px {S(14)}px; }}"
            f"QPushButton:hover {{ background:{T['accent2']}; color:{T['bg']}; }}"
        )
        done_btn.clicked.connect(self.accept)
        btn_row.addWidget(done_btn)

        root.addLayout(btn_row)

    # ── slots ──────────────────────────────────────────────

    def _on_color(self, key: str | None):
        self._p.set_color(self._path, key)
        for k, b in self._color_btns.items():
            hex_c, _ = COLORS[k]
            b.setChecked(k == key)
            b.setStyleSheet(self._color_btn_style(hex_c, k == key, self._T))
        self._none_color_btn.setChecked(not key)
        T = self._T
        self._none_color_btn.setStyleSheet(
            f"QPushButton {{ background:{T['overlay']}; color:{T['text_dim']};"
            f"border:2px solid {''+T['accent'] if not key else T['border']};"
            f"border-radius:{S(14)}px; font-size:{S(13)}px; }}"
            f"QPushButton:hover {{ border-color:{T['accent']}; }}"
        )

    def _on_badge(self, key: str | None):
        self._p.set_badge(self._path, key)
        for k, b in self._badge_btns.items():
            b_col = _BADGE_COLORS.get(k, self._T["accent"])
            b.setChecked(k == key)
            b.setStyleSheet(self._badge_btn_style(b_col, k == key, self._T))
        T = self._T
        self._none_badge_btn.setChecked(not key)
        self._none_badge_btn.setStyleSheet(
            f"QPushButton {{ background:{T['overlay']}; color:{T['text_dim']};"
            f"border:2px solid {''+T['accent'] if not key else T['border']};"
            f"border-radius:{S(6)}px; font-size:{S(13)}px; }}"
            f"QPushButton:hover {{ border-color:{T['accent']}; }}"
        )

    def _on_clear(self):
        self._p.clear(self._path)
        self._on_color(None)
        self._on_badge(None)

    # ── helpers de estilo ─────────────────────────────────

    @staticmethod
    def _color_btn_style(hex_c: str, active: bool, T: dict) -> str:
        border = f"3px solid {T['text']}" if active else f"2px solid transparent"
        return (
            f"QPushButton {{ background:{hex_c}; border:{border};"
            f"border-radius:{S(14)}px; }}"
            f"QPushButton:hover {{ border:2px solid {T['text']}; }}"
        )

    @staticmethod
    def _badge_btn_style(col: str, active: bool, T: dict) -> str:
        bg = col if active else T["overlay"]
        fg = T["bg"] if active else T["text_sub"]
        border = f"2px solid {col}" if active else f"1.5px solid {T['border']}"
        return (
            f"QPushButton {{ background:{bg}; color:{fg}; border:{border};"
            f"border-radius:{S(6)}px; font-size:{S(13)}px; font-weight:700; }}"
            f"QPushButton:hover {{ background:{col}; color:{T['bg']}; "
            f"border-color:{col}; }}"
        )

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background:{self._T['border']};")
        return f
