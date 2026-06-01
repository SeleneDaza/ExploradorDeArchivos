from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
)

from PyQt5.QtCore import Qt
from ui.theme import global_qss, btn_qss, input_qss, S


class NameDialog(QDialog):
    """
    Diálogo compacto y uniforme para ingresar un nombre.
    Reemplaza a QInputDialog.getText en toda la app.
    """

    def __init__(self, title: str, label: str,
                 confirm_text: str = "Aceptar",
                 initial: str = "",
                 placeholder: str = "",
                 T: dict = None,
                 confirm_only: bool = False,
                 password: bool = False,
                 parent=None):
        super().__init__(parent, Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setMinimumWidth(S(380))
        self.setMaximumWidth(S(520))
        self.setSizeGripEnabled(False)

        if T:
            self.setStyleSheet(global_qss(T))
        self._T            = T or {}
        self._confirm_only = confirm_only
        self._password     = password
        self._result: str  = ""
        self._build(label, confirm_text, initial, placeholder)

    # ── construcción ─────────────────────────────────────────

    def _build(self, label: str, confirm_text: str,
               initial: str, placeholder: str):
        T = self._T
        root = QVBoxLayout(self)
        root.setContentsMargins(S(24), S(20), S(24), S(20))
        root.setSpacing(S(14))

        # etiqueta
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{T.get('text','#ebebf5')}; font-size:{S(13)}px; font-weight:600;"
        )
        root.addWidget(lbl)

        # campo de texto
        self._input = QLineEdit(initial)
        self._input.setPlaceholderText(placeholder)
        self._input.setFixedHeight(S(38))
        if T:
            self._input.setStyleSheet(input_qss(T))
        if self._password:
            self._input.setEchoMode(QLineEdit.Password)
        if initial:
            self._input.selectAll()
        self._input.returnPressed.connect(self._accept)
        root.addWidget(self._input)

        # botones
        row = QHBoxLayout()
        row.setSpacing(S(8))
        row.addStretch()

        self._btn_cancel = QPushButton("Cancelar")
        self._btn_cancel.setFixedHeight(S(34))
        self._btn_cancel.setMinimumWidth(S(90))
        if T:
            self._btn_cancel.setStyleSheet(btn_qss(T, "ghost"))
        self._btn_cancel.clicked.connect(self.reject)

        self._btn_ok = QPushButton(confirm_text)
        self._btn_ok.setFixedHeight(S(34))
        self._btn_ok.setMinimumWidth(S(90))
        self._btn_ok.setDefault(True)
        if T:
            self._btn_ok.setStyleSheet(btn_qss(T, "accent"))
        self._btn_ok.clicked.connect(self._accept)

        row.addWidget(self._btn_cancel)
        row.addWidget(self._btn_ok)
        root.addLayout(row)

    # ── lógica ────────────────────────────────────────────────

    def _accept(self):
        if self._confirm_only:
            self._result = "confirm"
            self.accept()
            return
        text = self._input.text().strip()
        if text:
            self._result = text
            self.accept()

    def value(self) -> str:
        return self._result

    # ── API estática (reemplaza QInputDialog.getText) ─────────

    @staticmethod
    def ask(parent, title: str, label: str,
            confirm_text: str = "Aceptar",
            initial: str = "",
            placeholder: str = "",
            T: dict = None,
            password: bool = False) -> tuple[str, bool]:
        """Muestra el diálogo y retorna (texto, ok)."""
        dlg = NameDialog(title, label, confirm_text,
                         initial, placeholder, T, password=password, parent=parent)
        ok = dlg.exec_() == QDialog.Accepted
        return dlg.value(), ok
