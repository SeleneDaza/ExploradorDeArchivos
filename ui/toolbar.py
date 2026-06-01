from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import Qt, QSize
from ui.theme import DARK, btn_qss, S
from ui.icons import tinted_icon

_T = DARK

# Ícono que se muestra en el botón de tema según el modo ACTIVO
_THEME_ICON = ["moon", "sun", "palette"]
_THEME_LABEL = ["Oscuro", "Claro", "Retro"]

# (nombre_icono, texto_label_o_None, tooltip, argumento_slot)
_NAV_BTNS = [
    ("arrow-left",  None,    "Atrás          Alt+←"),
    ("arrow-right", None,    "Adelante       Alt+→"),
    ("arrow-up",    None,    "Subir          Alt+↑"),
]
_LOC_BTNS = [
    ("house",       None,    "Inicio         Ctrl+H"),
    ("hard-drive",  "Raíz",  "Directorio raíz"),
]
_NEW_BTNS = [
    ("folder-plus", "Carpeta", "Nueva carpeta   Ctrl+N"),
    ("file-plus",   "Archivo", "Nuevo archivo   Ctrl+Shift+N"),
]


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setFixedSize(1, 22)
    f.setStyleSheet(f"background:{_T['border']}; margin:0 4px;")
    return f


class Toolbar(QWidget):
    def __init__(self, on_up, on_home, on_root,
                 on_new_folder, on_new_file,
                 on_back, on_forward,
                 on_toggle_theme=None, theme_idx: int = 0,
                 on_toggle_preview=None,
                 on_zoom_in=None, on_zoom_out=None, on_zoom_reset=None):
        super().__init__()
        self._theme_idx  = theme_idx
        self._all_btns:  list[QPushButton] = []
        self._seps:      list[QFrame]      = []
        self._icon_btns: dict[QPushButton, str] = {}   # btn → nombre de ícono
        self.setFixedHeight(52)
        self._build(on_up, on_home, on_root, on_new_folder, on_new_file,
                    on_back, on_forward, on_toggle_theme, on_toggle_preview)
        self._apply_theme(_T)

    # ── construcción ─────────────────────────────────────────

    def _build(self, on_up, on_home, on_root, on_new_folder, on_new_file,
               on_back, on_forward, on_toggle_theme, on_toggle_preview):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(3)

        slots_nav  = [on_back, on_forward, on_up]
        slots_loc  = [on_home, on_root]
        slots_new  = [on_new_folder, on_new_file]

        def _btn(icon_name: str, label: str | None, tip: str,
                 slot=None, fixed_w: int | None = None) -> QPushButton:
            b = QPushButton()
            if label:
                b.setText(f"  {label}")
            b.setToolTip(tip)
            b.setFixedHeight(34)
            if fixed_w:
                b.setFixedWidth(fixed_w)
            b.setCursor(Qt.PointingHandCursor)
            if slot:
                b.clicked.connect(slot)
            self._all_btns.append(b)
            self._icon_btns[b] = icon_name
            lay.addWidget(b)
            return b

        def sep():
            s = _sep()
            self._seps.append(s)
            lay.addWidget(s)

        # Navegación (solo ícono)
        for (iname, lbl, tip), slot in zip(_NAV_BTNS, slots_nav):
            _btn(iname, lbl, tip, slot, fixed_w=34)
        sep()

        # Ubicación
        for (iname, lbl, tip), slot in zip(_LOC_BTNS, slots_loc):
            _btn(iname, lbl, tip, slot, fixed_w=34 if not lbl else None)
        sep()

        # Crear
        for (iname, lbl, tip), slot in zip(_NEW_BTNS, slots_new):
            _btn(iname, lbl, tip, slot)

        lay.addStretch()

        # Tema (ícono del modo activo)
        self._btn_theme = _btn(
            _THEME_ICON[self._theme_idx], None,
            "Cambiar tema  (Oscuro → Claro → Retro)",
            on_toggle_theme, fixed_w=34,
        )
        sep()

        # Vista previa (ícono + texto)
        _btn("panel-right", "Vista previa",
             "Mostrar/ocultar panel de vista previa  (Ctrl+P)",
             on_toggle_preview)

    # ── estilos ───────────────────────────────────────────

    def _apply_theme(self, T: dict):
        toolbar_bg = T.get("toolbar", T["bg"])
        self.setStyleSheet(
            f"background:{toolbar_bg}; border-bottom:1px solid {T['border']};"
        )
        qss = btn_qss(T)
        tint = T["text_sub"]
        icon_size = QSize(17, 17)
        for b in self._all_btns:
            b.setStyleSheet(qss)
            name = self._icon_btns.get(b)
            if name:
                b.setIcon(tinted_icon(name, tint))
                b.setIconSize(icon_size)
        for s in self._seps:
            s.setStyleSheet(f"background:{T['border']}; margin:0 4px;")

    def set_theme(self, T: dict, theme_idx: int = 0):
        self._theme_idx = theme_idx
        # actualizar ícono del botón de tema
        self._icon_btns[self._btn_theme] = _THEME_ICON[theme_idx]
        self._apply_theme(T)

    def update_zoom(self, zoom_pct: int = 100):
        pass

    def set_path(self, path: str):
        pass

    def set_theme_button(self, theme_idx: int = 0):
        self._icon_btns[self._btn_theme] = _THEME_ICON[theme_idx]
