"""
Sistema de diseño centralizado para ExploradorDeArchivos.
Todos los archivos UI importan colores, fuentes y builders QSS desde aquí.
"""
import sys

# ── Fuentes por plataforma ────────────────────────────────────

if sys.platform == "win32":
    FONT_UI   = "Segoe UI"
    FONT_MONO = "Cascadia Code, Consolas, Courier New"
elif sys.platform == "darwin":
    FONT_UI   = "SF Pro Text"
    FONT_MONO = "SF Mono, Menlo"
else:
    FONT_UI   = "Ubuntu, Cantarell, sans-serif"
    FONT_MONO = "Ubuntu Mono, DejaVu Sans Mono, monospace"

# ── Paleta oscura (Catppuccin Mocha) ─────────────────────────

DARK = {
    "bg":       "#1e1e2e",
    "surface":  "#181825",
    "panel":    "#24243e",
    "overlay":  "#313244",
    "accent":   "#cba6f7",
    "accent2":  "#89b4fa",
    "accent3":  "#74c7ec",
    "text":     "#cdd6f4",
    "text_sub": "#bac2de",
    "text_dim": "#6c7086",
    "success":  "#a6e3a1",
    "warning":  "#f38ba8",
    "caution":  "#fab387",
    "border":   "#313244",
    "sel_bg":   "rgba(203,166,247,0.15)",
    "sel_text": "#cba6f7",
    # alias para compatibilidad legacy
    "sidebar":  "#181825",
    "hover":    "#313244",
}

# ── Paleta clara (Catppuccin Latte) ──────────────────────────

LIGHT = {
    "bg":       "#eff1f5",
    "surface":  "#e6e9ef",
    "panel":    "#dce0e8",
    "overlay":  "#ccd0da",
    "accent":   "#8839ef",
    "accent2":  "#1e66f5",
    "accent3":  "#04a5e5",
    "text":     "#4c4f69",
    "text_sub": "#5c5f77",
    "text_dim": "#9ca0b0",
    "success":  "#40a02b",
    "warning":  "#d20f39",
    "caution":  "#fe640b",
    "border":   "#ccd0da",
    "sel_bg":   "rgba(136,57,239,0.12)",
    "sel_text": "#8839ef",
    "sidebar":  "#e6e9ef",
    "hover":    "#ccd0da",
}

# ── Radio de borde ────────────────────────────────────────────

R_XS = 4
R_SM = 6
R_MD = 8
R_LG = 12

# ── Builder: botón ───────────────────────────────────────────

def btn_qss(T: dict, variant: str = "default") -> str:
    if variant == "accent":
        bg, fg = T["accent"], T["bg"]
        hbg, hfg = T["accent2"], T["bg"]
    elif variant == "ghost":
        bg, fg = "transparent", T["text_sub"]
        hbg, hfg = T["overlay"], T["text"]
    elif variant == "danger":
        bg, fg = T["overlay"], T["warning"]
        hbg, hfg = T["warning"], T["bg"]
    else:
        bg, fg = T["overlay"], T["text"]
        hbg, hfg = T["accent"], T["bg"]
    return f"""
QPushButton {{
    background: {bg}; color: {fg};
    border: none; border-radius: {R_SM}px;
    font-family: "{FONT_UI}"; font-size: 13px;
    padding: 5px 14px;
}}
QPushButton:hover {{ background: {hbg}; color: {hfg}; }}
QPushButton:pressed {{ background: {T['accent2']}; color: {T['bg']}; }}
QPushButton:disabled {{ background: {T['surface']}; color: {T['text_dim']}; }}
"""

# ── Builder: input ────────────────────────────────────────────

def input_qss(T: dict) -> str:
    return f"""
QLineEdit {{
    background: {T['panel']}; color: {T['text']};
    border: 1.5px solid {T['border']}; border-radius: {R_SM}px;
    font-family: "{FONT_UI}"; font-size: 13px;
    padding: 5px 12px;
    selection-background-color: {T['accent']}; selection-color: {T['bg']};
}}
QLineEdit:focus {{ border: 1.5px solid {T['accent']}; background: {T['surface']}; }}
QLineEdit:hover:!focus {{ border: 1.5px solid {T['text_dim']}; }}
"""

# ── Builder: QSS global para QMainWindow ─────────────────────

def global_qss(T: dict) -> str:
    return f"""
* {{ font-family: "{FONT_UI}"; }}

QMainWindow {{ background: {T['bg']}; }}

/* ── Vistas de lista / árbol ── */
QTreeView, QListView {{
    background: {T['surface']};
    color: {T['text']};
    border: none;
    font-size: 13px;
    outline: none;
    show-decoration-selected: 1;
}}
QTreeView::item, QListView::item {{
    padding: 5px 6px;
    border-radius: {R_XS}px;
    min-height: 22px;
}}
QTreeView::item:hover, QListView::item:hover {{
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
    background: transparent; width: 6px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {T['border']}; border-radius: 3px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: {T['text_dim']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent; height: 6px; margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {T['border']}; border-radius: 3px; min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{ background: {T['text_dim']}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Menú contextual ── */
QMenu {{
    background: {T['panel']};
    color: {T['text']};
    border: 1px solid {T['border']};
    border-radius: {R_MD}px;
    padding: 5px;
}}
QMenu::item {{ padding: 7px 22px; border-radius: {R_XS}px; font-size: 13px; }}
QMenu::item:selected {{ background: {T['overlay']}; color: {T['text']}; }}
QMenu::separator {{ background: {T['border']}; height: 1px; margin: 4px 10px; }}

/* ── Tooltip ── */
QToolTip {{
    background: {T['panel']};
    color: {T['text_sub']};
    border: 1px solid {T['border']};
    border-radius: {R_XS}px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ── Diálogos ── */
QDialog {{ background: {T['bg']}; color: {T['text']}; }}
QGroupBox {{
    color: {T['accent']};
    border: 1px solid {T['border']};
    border-radius: {R_LG}px;
    margin-top: 14px;
    padding: 10px 8px 8px 8px;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.5px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}

/* ── Checkboxes ── */
QCheckBox {{ color: {T['text']}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border-radius: {R_XS}px;
    border: 1.5px solid {T['border']};
    background: {T['panel']};
}}
QCheckBox::indicator:checked {{
    background: {T['accent']}; border: 1.5px solid {T['accent']};
}}
QCheckBox::indicator:hover {{ border: 1.5px solid {T['text_dim']}; }}

/* ── LineEdit (diálogos) ── */
QLineEdit {{
    background: {T['panel']}; color: {T['text']};
    border: 1.5px solid {T['border']}; border-radius: {R_SM}px;
    padding: 5px 10px; font-size: 13px;
    selection-background-color: {T['accent']}; selection-color: {T['bg']};
}}
QLineEdit:focus {{ border: 1.5px solid {T['accent']}; }}

/* ── QListWidget (dialogs) ── */
QListWidget {{
    background: {T['surface']}; color: {T['text']};
    border: 1px solid {T['border']}; border-radius: {R_SM}px;
    outline: none;
}}
QListWidget::item {{ padding: 5px 8px; border-radius: {R_XS}px; }}
QListWidget::item:selected {{ background: {T['sel_bg']}; color: {T['sel_text']}; }}
QListWidget::item:hover {{ background: {T['overlay']}; }}

/* ── Splitter ── */
QSplitter::handle {{ background: {T['border']}; width: 1px; }}

/* ── Status bar ── */
QStatusBar {{
    background: {T['surface']};
    color: {T['text_dim']};
    font-size: 12px;
    border-top: 1px solid {T['border']};
}}
QStatusBar::item {{ border: none; }}
"""


# ── Paleta QPalette ───────────────────────────────────────────

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
    font = QFont(FONT_UI, 10)
    app.setFont(font)
