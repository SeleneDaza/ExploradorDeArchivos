from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from ui.theme import DARK, FONT_UI, S

_T = DARK


class SearchBar(QWidget):
    search_triggered = pyqtSignal(str)
    search_cleared   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(S(52))
        self._build()
        self.set_theme(_T)

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(S(16), S(8), S(16), S(8))
        lay.setSpacing(S(8))

        self.input = QLineEdit()
        self.input.setPlaceholderText("Buscar por nombre o extensión...   Ctrl+F")
        self.input.setFixedHeight(S(36))
        self.input.returnPressed.connect(self._on_search)
        self.input.textChanged.connect(self._on_changed)

        self._btn_clear = QPushButton("×")
        self._btn_clear.setFixedSize(S(28), S(28))
        self._btn_clear.setToolTip("Limpiar  Esc")
        self._btn_clear.setCursor(Qt.PointingHandCursor)
        self._btn_clear.clicked.connect(self._on_clear)

        lay.addWidget(self.input, 1)
        lay.addWidget(self._btn_clear)

    def set_theme(self, T: dict):
        global _T
        _T = T
        self.setStyleSheet(
            f"background: {T['bg']}; border-bottom: 1px solid {T['border']};"
        )
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {T['panel']}; color: {T['text']};
                border: 1.5px solid {T['border']}; border-radius: {S(18)}px;
                font-family: "{FONT_UI}"; font-size: {S(14)}px;
                padding: {S(4)}px {S(16)}px;
                selection-background-color: {T['accent']}; selection-color: {T['bg']};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {T['accent']};
                background: {T['surface']};
            }}
            QLineEdit:hover:!focus {{ border: 1.5px solid {T['text_dim']}; }}
        """)
        self._btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {T['text_dim']};
                border: none; border-radius: {S(14)}px;
                font-size: {S(13)}px;
            }}
            QPushButton:hover {{ background: {T['overlay']}; color: {T['text']}; }}
        """)

    def update_zoom(self):
        self.setFixedHeight(S(52))
        self.input.setFixedHeight(S(36))
        self._btn_clear.setFixedSize(S(28), S(28))

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
