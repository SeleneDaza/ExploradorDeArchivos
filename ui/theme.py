"""
Sistema de diseño centralizado — ExploradorDeArchivos
Paletas: DARK (Linear/VSCode), LIGHT (Notion/macOS), RETRO (pastel cálido)
Zoom:    S(n) escala cualquier valor de píxel; set_zoom() reconstruye toda la UI
"""
import sys

# ── Fuentes por plataforma ────────────────────────────────────

if sys.platform == "win32":
    FONT_UI   = "Segoe UI"
    FONT_MONO = "Cascadia Code, Consolas, Courier New"
elif sys.platform == "darwin":
    FONT_UI   = "SF Pro Display"
    FONT_MONO = "SF Mono, Menlo, Monaco"
else:
    FONT_UI   = "Inter, Ubuntu, sans-serif"
    FONT_MONO = "JetBrains Mono, Ubuntu Mono, monospace"

# ── Sistema de zoom (Ctrl+= / Ctrl+- / Ctrl+0) ───────────────

_ZOOM: float = 1.0


def S(n: float) -> int:
    """Escala un valor de píxeles por el zoom actual."""
    return max(1, round(n * _ZOOM))


def get_zoom() -> float:
    return _ZOOM


def set_zoom(factor: float):
    global _ZOOM
    _ZOOM = max(0.75, min(2.5, factor))


# ── Paleta oscura — inspirada en Linear / VSCode ─────────────

DARK = {
    "bg":       "#0e0e14",
    "surface":  "#141420",
    "panel":    "#1a1a28",
    "overlay":  "#24243a",
    "accent":   "#7b6cf6",
    "accent2":  "#4fa4f8",
    "accent3":  "#2ec4a0",
    "text":     "#ebebf5",
    "text_sub": "#8888aa",
    "text_dim": "#44446a",
    "success":  "#2ec4a0",
    "warning":  "#f26d6a",
    "caution":  "#f5a742",
    "border":   "#24243a",
    "sel_bg":   "rgba(123,108,246,0.18)",
    "sel_text": "#a99df8",
    "sidebar":  "#0b0b12",
    "hover":    "#24243a",
}

# ── Paleta clara — inspirada en Notion / macOS ───────────────

LIGHT = {
    "bg":       "#ffffff",
    "surface":  "#fafafd",
    "panel":    "#f2f2fa",
    "overlay":  "#e8e8f4",
    "accent":   "#5244cc",
    "accent2":  "#2171e8",
    "accent3":  "#09a87a",
    "text":     "#12122a",
    "text_sub": "#52527a",
    "text_dim": "#9898ba",
    "success":  "#09a87a",
    "warning":  "#d93a3a",
    "caution":  "#d07820",
    "border":   "#e2e2f0",
    "sel_bg":   "rgba(82,68,204,0.11)",
    "sel_text": "#5244cc",
    "sidebar":  "#f5f5fd",
    "hover":    "#e8e8f4",
}

# ── Paleta retro — pastel cálido ─────────────────────────────

RETRO = {
    "bg":       "#faf5e8",
    "surface":  "#f5edd8",
    "panel":    "#f0dfd2",
    "overlay":  "#ecddd0",
    "accent":   "#e87570",
    "accent2":  "#5bc4b0",
    "accent3":  "#f0c040",
    "text":     "#3d2b1f",
    "text_sub": "#6b4c3b",
    "text_dim": "#a08060",
    "success":  "#6bbf6b",
    "warning":  "#e87570",
    "caution":  "#f0a040",
    "border":   "#d4b0a0",
    "sel_bg":   "rgba(232,117,112,0.18)",
    "sel_text": "#e87570",
    "sidebar":  "#f0e4d0",
    "hover":    "#ecddd0",
    "toolbar":          "#e8a098",
    "scrollbar_handle": "#f0c040",
}

# ── Radios de borde (tokens fijos) ────────────────────────────
# Para código Python que usa setFixedHeight, etc.
R_XS = 4
R_SM = 6
R_MD = 8
R_LG = 12

# ── Builder: QSS global ───────────────────────────────────────

def global_qss(T: dict) -> str:
    _scroll = T.get("scrollbar_handle", T["overlay"])
    _toolbar_bg = T.get("toolbar", T["bg"])
    return f"""
* {{ font-family: "{FONT_UI}"; }}

QMainWindow, QDialog {{ background: {T['bg']}; color: {T['text']}; }}

/* ── Árbol y lista ── */
QTreeView, QListView {{
    background: {T['surface']};
    color: {T['text']};
    border: none;
    font-size: {S(13)}px;
    outline: none;
    show-decoration-selected: 1;
    padding: {S(3)}px;
}}
QTreeView::item, QListView::item {{
    padding: {S(5)}px {S(9)}px;
    border-radius: {S(7)}px;
    min-height: {S(26)}px;
}}
QTreeView::item:hover:!selected, QListView::item:hover:!selected {{
    background: {T['overlay']};
}}
QTreeView::item:selected, QListView::item:selected {{
    background: {T['sel_bg']};
    color: {T['sel_text']};
    font-weight: 600;
}}
QTreeView::branch {{ background: {T['surface']}; }}
QTreeView::branch:selected {{ background: {T['sel_bg']}; }}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: transparent; width: {S(10)}px; margin: {S(4)}px 0;
}}
QScrollBar::handle:vertical {{
    background: {_scroll}; border-radius: {S(5)}px;
    min-height: {S(36)}px; margin: 0 {S(2)}px;
}}
QScrollBar::handle:vertical:hover {{ background: {T['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent; height: {S(10)}px; margin: 0 {S(4)}px;
}}
QScrollBar::handle:horizontal {{
    background: {_scroll}; border-radius: {S(5)}px;
    min-width: {S(36)}px; margin: {S(2)}px 0;
}}
QScrollBar::handle:horizontal:hover {{ background: {T['accent']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Menú contextual ── */
QMenu {{
    background: {T['panel']};
    color: {T['text']};
    border: 1px solid {T['border']};
    border-radius: {S(12)}px;
    padding: {S(6)}px {S(4)}px;
}}
QMenu::item {{
    padding: {S(9)}px {S(28)}px;
    border-radius: {S(8)}px;
    font-size: {S(14)}px;
    margin: {S(1)}px {S(4)}px;
}}
QMenu::item:selected {{ background: {T['overlay']}; color: {T['text']}; }}
QMenu::separator {{
    background: {T['border']}; height: 1px;
    margin: {S(4)}px {S(8)}px;
}}

/* ── Tooltip ── */
QToolTip {{
    background: {T['panel']};
    color: {T['text_sub']};
    border: 1px solid {T['border']};
    border-radius: {S(8)}px;
    padding: {S(5)}px {S(10)}px;
    font-size: {S(12)}px;
}}

/* ── GroupBox (diálogos) ── */
QGroupBox {{
    color: {T['accent']};
    border: 1px solid {T['border']};
    border-radius: {S(10)}px;
    margin-top: {S(14)}px;
    padding: {S(10)}px {S(8)}px {S(8)}px {S(8)}px;
    font-weight: 700;
    font-size: {S(12)}px;
    letter-spacing: 0.8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: {S(14)}px; padding: 0 {S(6)}px;
}}

/* ── CheckBox ── */
QCheckBox {{ color: {T['text']}; spacing: {S(8)}px; font-size: {S(13)}px; }}
QCheckBox::indicator {{
    width: {S(18)}px; height: {S(18)}px;
    border-radius: {S(5)}px;
    border: 1.5px solid {T['border']};
    background: {T['panel']};
}}
QCheckBox::indicator:checked {{
    background: {T['accent']}; border-color: {T['accent']};
}}
QCheckBox::indicator:hover {{ border-color: {T['accent']}; }}

/* ── LineEdit global ── */
QLineEdit {{
    background: {T['panel']}; color: {T['text']};
    border: 1.5px solid {T['border']}; border-radius: {S(8)}px;
    padding: {S(6)}px {S(12)}px; font-size: {S(14)}px;
    selection-background-color: {T['accent']}; selection-color: {T['bg']};
}}
QLineEdit:focus {{ border: 1.5px solid {T['accent']}; background: {T['surface']}; }}
QLineEdit:hover:!focus {{ border: 1.5px solid {T['text_dim']}; }}

/* ── QListWidget (diálogos) ── */
QListWidget {{
    background: {T['surface']}; color: {T['text']};
    border: 1px solid {T['border']}; border-radius: {S(8)}px;
    outline: none; padding: {S(4)}px;
}}
QListWidget::item {{
    padding: {S(6)}px {S(10)}px; border-radius: {S(6)}px;
    min-height: {S(24)}px;
}}
QListWidget::item:selected {{ background: {T['sel_bg']}; color: {T['sel_text']}; }}
QListWidget::item:hover:!selected {{ background: {T['overlay']}; }}

/* ── Splitter ── */
QSplitter::handle {{ background: {T['border']}; width: 1px; height: 1px; }}

/* ── Barra de estado ── */
QStatusBar {{
    background: {T['surface']};
    color: {T['text_dim']};
    font-size: {S(12)}px;
    padding: 0 {S(8)}px;
    border-top: 1px solid {T['border']};
    min-height: {S(28)}px;
}}
QStatusBar::item {{ border: none; }}

/* ── ProgressBar ── */
QProgressBar {{
    background: {T['overlay']}; border-radius: {S(4)}px;
    border: none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {T['accent']}, stop:1 {T['accent2']});
    border-radius: {S(4)}px;
}}

/* ── SpinBox / ComboBox ── */
QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {T['panel']}; color: {T['text']};
    border: 1.5px solid {T['border']}; border-radius: {S(8)}px;
    padding: {S(5)}px {S(10)}px; font-size: {S(14)}px;
    min-height: {S(32)}px;
}}
QSpinBox:focus, QComboBox:focus {{ border-color: {T['accent']}; }}
QComboBox::drop-down {{ border: none; padding-right: {S(8)}px; }}
QComboBox QAbstractItemView {{
    background: {T['panel']}; color: {T['text']};
    border: 1px solid {T['border']}; border-radius: {S(8)}px;
    selection-background-color: {T['sel_bg']};
}}
"""


# ── Builder: botón ────────────────────────────────────────────

def btn_qss(T: dict, variant: str = "default") -> str:
    if variant == "accent":
        bg, fg     = T["accent"],   T["bg"]
        hbg, hfg   = T["accent2"],  T["bg"]
    elif variant == "ghost":
        bg, fg     = "transparent", T["text_sub"]
        hbg, hfg   = T["overlay"],  T["text"]
    elif variant == "danger":
        bg, fg     = T["overlay"],  T["warning"]
        hbg, hfg   = T["warning"],  T["bg"]
    else:
        bg, fg     = T["overlay"],  T["text"]
        hbg, hfg   = T["accent"],   T["bg"]
    return f"""
QPushButton {{
    background: {bg}; color: {fg};
    border: none; border-radius: {S(7)}px;
    font-family: "{FONT_UI}"; font-size: {S(13)}px;
    padding: {S(5)}px {S(14)}px;
    min-height: {S(30)}px;
}}
QPushButton:hover    {{ background: {hbg}; color: {hfg}; }}
QPushButton:pressed  {{ background: {T['accent2']}; color: {T['bg']}; }}
QPushButton:disabled {{ background: {T['surface']}; color: {T['text_dim']}; opacity: 0.5; }}
"""


# ── Builder: input ────────────────────────────────────────────

def input_qss(T: dict) -> str:
    return f"""
QLineEdit {{
    background: {T['panel']}; color: {T['text']};
    border: 1.5px solid {T['border']}; border-radius: {S(22)}px;
    font-family: "{FONT_UI}"; font-size: {S(14)}px;
    padding: {S(7)}px {S(18)}px;
    selection-background-color: {T['accent']}; selection-color: {T['bg']};
}}
QLineEdit:focus {{
    border: 1.5px solid {T['accent']};
    background: {T['surface']};
}}
QLineEdit:hover:!focus {{ border: 1.5px solid {T['text_dim']}; }}
"""


# ── QPalette ─────────────────────────────────────────────────

def apply_palette(app, T: dict):
    app.setStyle("Fusion")
    from PyQt5.QtGui import QPalette, QColor, QFont
    p = QPalette()
    p.setColor(QPalette.Window,          QColor(T["bg"]))
    p.setColor(QPalette.WindowText,      QColor(T["text"]))
    p.setColor(QPalette.Base,            QColor(T["surface"]))
    p.setColor(QPalette.AlternateBase,   QColor(T["panel"]))
    p.setColor(QPalette.Text,            QColor(T["text"]))
    p.setColor(QPalette.BrightText,      QColor(T["text"]))
    p.setColor(QPalette.Button,          QColor(T["overlay"]))
    p.setColor(QPalette.ButtonText,      QColor(T["text"]))
    p.setColor(QPalette.Highlight,       QColor(T["accent"]))
    p.setColor(QPalette.HighlightedText, QColor(T["bg"]))
    p.setColor(QPalette.ToolTipBase,     QColor(T["panel"]))
    p.setColor(QPalette.ToolTipText,     QColor(T["text_sub"]))
    p.setColor(QPalette.PlaceholderText, QColor(T["text_dim"]))
    app.setPalette(p)
    app.setFont(QFont(FONT_UI, S(10)))
