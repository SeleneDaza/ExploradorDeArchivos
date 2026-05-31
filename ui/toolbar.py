from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame, QLabel
from PyQt5.QtCore import Qt
from ui.theme import DARK, FONT_UI, btn_qss, R_SM

_T = DARK   # módulo empieza en dark; toggle_theme() llama a set_theme()


def _btn(text: str, tip: str, slot, fixed_w: int = None) -> QPushButton:
    b = QPushButton(text)
    b.setToolTip(tip)
    b.setFixedHeight(34)
    if fixed_w:
        b.setFixedWidth(fixed_w)
    b.setStyleSheet(btn_qss(_T))
    b.setCursor(Qt.PointingHandCursor)
    if slot:
        b.clicked.connect(slot)
    return b


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setFixedWidth(1)
    f.setFixedHeight(22)
    f.setStyleSheet(f"background: {_T['border']}; margin: 0 4px;")
    return f


class Toolbar(QWidget):
    def __init__(self, on_up, on_home, on_root,
                 on_new_folder, on_new_file,
                 on_back, on_forward,
                 on_toggle_theme=None, is_dark=True,
                 on_toggle_preview=None):
        super().__init__()
        self._on_toggle_theme = on_toggle_theme
        self._is_dark = is_dark
        self._all_btns = []
        self.setFixedHeight(52)
        self._build(on_up, on_home, on_root, on_new_folder, on_new_file,
                    on_back, on_forward, on_toggle_theme, on_toggle_preview)
        self._apply_theme(_T)

    def _build(self, on_up, on_home, on_root, on_new_folder, on_new_file,
               on_back, on_forward, on_toggle_theme, on_toggle_preview):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(6)

        # ── grupo navegación ──
        self._btn_back    = _btn("◀",          "Atrás  (Alt+←)",    on_back,    fixed_w=34)
        self._btn_forward = _btn("▶",          "Adelante  (Alt+→)", on_forward, fixed_w=34)
        self._btn_up      = _btn("⬆  Subir",   "Subir  (Alt+↑)",    on_up)
        for b in (self._btn_back, self._btn_forward, self._btn_up):
            lay.addWidget(b)
            self._all_btns.append(b)

        lay.addWidget(_sep())

        # ── grupo ubicación ──
        self._btn_home = _btn("⌂  Home",    "Carpeta personal  (Ctrl+H)", on_home)
        self._btn_root = _btn("⬡  Raíz",    "Directorio raíz",            on_root)
        for b in (self._btn_home, self._btn_root):
            lay.addWidget(b)
            self._all_btns.append(b)

        lay.addWidget(_sep())

        # ── grupo creación ──
        self._btn_folder = _btn("＋ Carpeta", "Nueva carpeta  (Ctrl+N)",        on_new_folder)
        self._btn_file   = _btn("＋ Archivo", "Nuevo archivo  (Ctrl+Shift+N)",  on_new_file)
        for b in (self._btn_folder, self._btn_file):
            lay.addWidget(b)
            self._all_btns.append(b)

        lay.addStretch()

        # ── grupo vista ──
        self._btn_theme = _btn("🌙" if self._is_dark else "🌞",
                               "Cambiar tema", on_toggle_theme, fixed_w=40)
        self._btn_preview = _btn("👁  Vista", "Mostrar/ocultar vista previa  (Ctrl+P)",
                                 on_toggle_preview)
        for b in (self._btn_theme, self._btn_preview):
            lay.addWidget(b)
            self._all_btns.append(b)

    def _apply_theme(self, T: dict):
        self.setStyleSheet(f"background: {T['bg']}; border-bottom: 1px solid {T['border']};")
        style = btn_qss(T)
        for b in self._all_btns:
            b.setStyleSheet(style)
        # separadores
        for child in self.findChildren(QFrame):
            child.setStyleSheet(f"background: {T['border']}; margin: 0 4px;")

    def set_theme(self, T: dict, is_dark: bool):
        self._is_dark = is_dark
        _T_ref = T
        self._apply_theme(T)
        self._btn_theme.setText("🌙" if is_dark else "🌞")

    # backwards compat
    def set_path(self, path: str):
        pass

    def set_theme_button(self, is_dark: bool):
        self._btn_theme.setText("🌙" if is_dark else "🌞")
