from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from ui.theme import DARK, FONT_UI, btn_qss, input_qss, R_SM

_T = DARK


class SearchBar(QWidget):
    search_triggered = pyqtSignal(str)
    search_cleared   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(44)
        self._build()
        self.set_theme(_T)

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 6, 14, 6)
        lay.setSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText("  Buscar por nombre o extensión...  (Ctrl+F)")
        self.input.setFixedHeight(32)
        self.input.returnPressed.connect(self._on_search)
        self.input.textChanged.connect(self._on_changed)

        self._btn_search = QPushButton("Buscar")
        self._btn_search.setFixedHeight(32)
        self._btn_search.clicked.connect(self._on_search)

        self._btn_clear = QPushButton("✕")
        self._btn_clear.setFixedSize(32, 32)
        self._btn_clear.setToolTip("Limpiar búsqueda  (Esc)")
        self._btn_clear.clicked.connect(self._on_clear)

        lay.addWidget(self.input, 1)
        lay.addWidget(self._btn_search)
        lay.addWidget(self._btn_clear)

    def set_theme(self, T: dict):
        self.setStyleSheet(f"background: {T['bg']}; border-bottom: 1px solid {T['border']};")
        self.input.setStyleSheet(input_qss(T))
        self._btn_search.setStyleSheet(btn_qss(T, variant="accent"))
        self._btn_clear.setStyleSheet(btn_qss(T))

    def _on_search(self):
        text = self.input.text().strip()
        if text:
            self.search_triggered.emit(text)

    def _on_changed(self, text: str):
        if not text:
            self.search_cleared.emit()

    def _on_clear(self):
        self.input.clear()
        self.search_cleared.emit()
        self.input.setFocus()
