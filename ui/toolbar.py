from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont


class Toolbar(QWidget):
    def __init__(self, on_up, on_home, on_root, on_new_folder, on_new_file):
        super().__init__()
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        btn_up         = QPushButton("⬆  Subir")
        btn_home       = QPushButton("🏠  Home")
        btn_root       = QPushButton("💻  Raíz")
        btn_new_folder = QPushButton("📁  Nueva carpeta")
        btn_new_file   = QPushButton("📄  Nuevo archivo")

        for btn in [btn_up, btn_home, btn_root, btn_new_folder, btn_new_file]:
            btn.setFixedHeight(30)

        btn_up.clicked.connect(on_up)
        btn_home.clicked.connect(on_home)
        btn_root.clicked.connect(on_root)
        btn_new_folder.clicked.connect(on_new_folder)
        btn_new_file.clicked.connect(on_new_file)

        self.path_label = QLabel()
        self.path_label.setFont(QFont("Monospace", 9))

        layout.addWidget(btn_up)
        layout.addWidget(btn_home)
        layout.addWidget(btn_root)
        layout.addWidget(btn_new_folder)
        layout.addWidget(btn_new_file)
        layout.addSpacing(12)
        layout.addWidget(self.path_label, stretch=1)

    def set_path(self, path: str):
        self.path_label.setText(path)