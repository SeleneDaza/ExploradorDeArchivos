from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont


class Toolbar(QWidget):
    def __init__(self, on_up, on_home, on_root):
        super().__init__()
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        btn_up   = QPushButton("⬆  Subir")
        btn_home = QPushButton("🏠  Home")
        btn_root = QPushButton("💻  Raíz")

        for btn in [btn_up, btn_home, btn_root]:
            btn.setFixedHeight(30)

        btn_up.clicked.connect(on_up)
        btn_home.clicked.connect(on_home)
        btn_root.clicked.connect(on_root)

        self.path_label = QLabel()
        self.path_label.setFont(QFont("Monospace", 9))

        layout.addWidget(btn_up)
        layout.addWidget(btn_home)
        layout.addWidget(btn_root)
        layout.addSpacing(12)
        layout.addWidget(self.path_label, stretch=1)

    def set_path(self, path: str):
        self.path_label.setText(path)