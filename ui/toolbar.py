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
    QPushButton:pressed {{
        background: {DARK['accent2']};
    }}
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
    def __init__(self, on_up, on_home, on_root, on_new_folder, on_new_file):
        super().__init__()
        self.setFixedHeight(48)
        self.setStyleSheet(f"background: {DARK['bg']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        btn_up         = QPushButton("⬆  Subir")
        btn_home       = QPushButton("⌂  Home")
        btn_root       = QPushButton("⬡  Raíz")
        btn_new_folder = QPushButton("＋ Carpeta")
        btn_new_file   = QPushButton("＋ Archivo")

        for btn in [btn_up, btn_home, btn_root]:
            btn.setFixedHeight(34)
            btn.setStyleSheet(BTN_STYLE)

        for btn in [btn_new_folder, btn_new_file]:
            btn.setFixedHeight(34)
            btn.setStyleSheet(BTN_ACTION_STYLE)

        btn_up.clicked.connect(on_up)
        btn_home.clicked.connect(on_home)
        btn_root.clicked.connect(on_root)
        btn_new_folder.clicked.connect(on_new_folder)
        btn_new_file.clicked.connect(on_new_file)

        self.path_label = QLabel()
        self.path_label.setFont(QFont("Monospace", 9))
        self.path_label.setStyleSheet(f"color: {DARK['text_dim']};")

        layout.addWidget(btn_up)
        layout.addWidget(btn_home)
        layout.addWidget(btn_root)
        layout.addSpacing(8)
        layout.addWidget(btn_new_folder)
        layout.addWidget(btn_new_file)
        layout.addStretch()

    def set_path(self, path: str):
        pass