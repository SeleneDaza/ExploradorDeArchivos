from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

DARK = {
    "bg":       "#1e1e2e",
    "accent":   "#cba6f7",
    "accent2":  "#89b4fa",
    "text":     "#cdd6f4",
    "text_dim": "#6c7086",
    "hover":    "#313244",
    "border":   "#313244",
}

BTN_STYLE = f"""
    QPushButton {{
        background: {DARK['hover']};
        color: {DARK['text']};
        border: none;
        border-radius: 6px;
        padding: 0 14px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: {DARK['accent']};
        color: {DARK['bg']};
    }}
    QPushButton:pressed {{ background: {DARK['accent2']}; }}
"""

BTN_ACTION_STYLE = f"""
    QPushButton {{
        background: transparent;
        color: {DARK['accent']};
        border: 1px solid {DARK['accent']};
        border-radius: 6px;
        padding: 0 14px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: {DARK['accent']};
        color: {DARK['bg']};
    }}
"""


class Toolbar(QWidget):
    def __init__(self, on_up, on_home, on_root,
                 on_new_folder, on_new_file,
                 on_back, on_forward,
                 on_toggle_theme=None, is_dark=True):
        super().__init__()
        self.setFixedHeight(48)
        self.setStyleSheet(f"background: {DARK['bg']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        btn_back    = QPushButton("◀")
        btn_forward = QPushButton("▶")
        btn_up      = QPushButton("⬆  Subir")
        btn_home    = QPushButton("⌂  Home")
        btn_root    = QPushButton("⬡  Raíz")
        btn_folder  = QPushButton("＋ Carpeta")
        btn_file    = QPushButton("＋ Archivo")

        btn_back.setFixedSize(34, 34)
        btn_forward.setFixedSize(34, 34)

        for btn in [btn_back, btn_forward, btn_up, btn_home, btn_root]:
            btn.setStyleSheet(BTN_STYLE)

        for btn in [btn_folder, btn_file]:
            btn.setFixedHeight(34)
            btn.setStyleSheet(BTN_ACTION_STYLE)

        btn_back.clicked.connect(on_back)
        btn_forward.clicked.connect(on_forward)
        btn_up.clicked.connect(on_up)
        btn_home.clicked.connect(on_home)
        btn_root.clicked.connect(on_root)
        btn_folder.clicked.connect(on_new_folder)
        btn_file.clicked.connect(on_new_file)

        # theme toggle button (sun / moon)
        btn_theme = QPushButton("🌙" if is_dark else "🌞")
        btn_theme.setCheckable(True)
        btn_theme.setFixedSize(48, 34)
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.setStyleSheet(BTN_STYLE)
        if on_toggle_theme:
            btn_theme.clicked.connect(on_toggle_theme)

        layout.addWidget(btn_back)
        layout.addWidget(btn_forward)
        layout.addSpacing(4)
        layout.addWidget(btn_up)
        layout.addWidget(btn_home)
        layout.addWidget(btn_root)
        layout.addSpacing(8)
        layout.addWidget(btn_folder)
        layout.addWidget(btn_file)
        layout.addWidget(btn_theme)
        layout.addStretch()

        self._btn_theme = btn_theme

    def set_path(self, path: str):
        pass

    def set_theme_button(self, is_dark: bool):
        if hasattr(self, "_btn_theme"):
            self._btn_theme.setText("🌙" if is_dark else "🌞")