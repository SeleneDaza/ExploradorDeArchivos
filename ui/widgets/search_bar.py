from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt

DARK = {
    "bg":      "#1e1e2e",
    "accent":  "#cba6f7",
    "text":    "#cdd6f4",
    "hover":   "#313244",
    "border":  "#313244",
    "panel":   "#24243e",
}


class SearchBar(QWidget):
    search_triggered = pyqtSignal(str)
    search_cleared   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.setStyleSheet(f"background: {DARK['bg']};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(6)

        self.input = QLineEdit()
        self.input.setPlaceholderText("🔍  Buscar en carpeta actual...")
        self.input.setFixedHeight(28)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {DARK['panel']};
                color: {DARK['text']};
                border: 1px solid {DARK['border']};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {DARK['accent']};
            }}
        """)
        self.input.returnPressed.connect(self._on_search)
        self.input.textChanged.connect(self._on_text_changed)

        btn_search = QPushButton("Buscar")
        btn_search.setFixedHeight(28)
        btn_search.setStyleSheet(f"""
            QPushButton {{
                background: {DARK['accent']};
                color: {DARK['bg']};
                border: none;
                border-radius: 6px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {DARK['hover']};
                color: {DARK['text']};
            }}
        """)
        btn_search.clicked.connect(self._on_search)

        btn_clear = QPushButton("✕")
        btn_clear.setFixedSize(28, 28)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: {DARK['hover']};
                color: {DARK['text']};
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {DARK['accent']};
                color: {DARK['bg']};
            }}
        """)
        btn_clear.clicked.connect(self._on_clear)

        layout.addWidget(self.input)
        layout.addWidget(btn_search)
        layout.addWidget(btn_clear)

    def _on_search(self):
        text = self.input.text().strip()
        if text:
            self.search_triggered.emit(text)

    def _on_text_changed(self, text):
        if not text:
            self.search_cleared.emit()

    def _on_clear(self):
        self.input.clear()
        self.search_cleared.emit()