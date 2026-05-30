from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QCheckBox, QLineEdit, QPushButton,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from core.permissions import Permissions


class PermissionsDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.perms = Permissions()
        self.setWindowTitle(f"Permisos — {path}")
        self.setMinimumWidth(400)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ── info general ─────────────────────────────────────
        info_group = QGroupBox("Información")
        info_layout = QGridLayout(info_group)

        self.lbl_owner    = QLabel()
        self.lbl_group    = QLabel()
        self.lbl_octal    = QLabel()
        self.lbl_symbolic = QLabel()

        info_layout.addWidget(QLabel("Propietario:"), 0, 0)
        info_layout.addWidget(self.lbl_owner,         0, 1)
        info_layout.addWidget(QLabel("Grupo:"),       1, 0)
        info_layout.addWidget(self.lbl_group,         1, 1)
        info_layout.addWidget(QLabel("Octal:"),       2, 0)
        info_layout.addWidget(self.lbl_octal,         2, 1)
        info_layout.addWidget(QLabel("Simbólico:"),   3, 0)
        info_layout.addWidget(self.lbl_symbolic,      3, 1)

        layout.addWidget(info_group)

        # ── checkboxes rwx ───────────────────────────────────
        perms_group = QGroupBox("Permisos")
        grid = QGridLayout(perms_group)

        grid.addWidget(QLabel(""),        0, 0)
        grid.addWidget(QLabel("Leer"),    0, 1, Qt.AlignCenter)
        grid.addWidget(QLabel("Escribir"),0, 2, Qt.AlignCenter)
        grid.addWidget(QLabel("Ejecutar"),0, 3, Qt.AlignCenter)

        self.checks = {}
        for row, who in enumerate(["owner", "group", "others"], start=1):
            label = {"owner": "Propietario", "group": "Grupo", "others": "Otros"}[who]
            grid.addWidget(QLabel(label), row, 0)
            self.checks[who] = {}
            for col, perm in enumerate(["read", "write", "execute"], start=1):
                cb = QCheckBox()
                cb.stateChanged.connect(self._update_octal_preview)
                grid.addWidget(cb, row, col, Qt.AlignCenter)
                self.checks[who][perm] = cb

        layout.addWidget(perms_group)

        # ── octal directo ────────────────────────────────────
        octal_group = QGroupBox("Cambiar por octal")
        octal_layout = QHBoxLayout(octal_group)
        self.octal_input = QLineEdit()
        self.octal_input.setMaxLength(4)
        self.octal_input.setFixedWidth(60)
        self.octal_input.setPlaceholderText("755")
        octal_layout.addWidget(QLabel("Octal:"))
        octal_layout.addWidget(self.octal_input)
        octal_layout.addStretch()
        layout.addWidget(octal_group)

        # ── botones ──────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_apply  = QPushButton("Aplicar")
        btn_close  = QPushButton("Cerrar")
        btn_apply.clicked.connect(self._apply)
        btn_close.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _load(self):
        info = self.perms.get_info(self.path)
        if not info["ok"]:
            QMessageBox.warning(self, "Error", info["error"])
            return

        self.lbl_owner.setText(info["owner"])
        self.lbl_group.setText(info["group"])
        self.lbl_octal.setText(info["octal"])
        self.lbl_symbolic.setText(info["symbolic"])
        self.octal_input.setText(info["octal"])

        for who in ["owner", "group", "others"]:
            for perm in ["read", "write", "execute"]:
                self.checks[who][perm].setChecked(info["bits"][who][perm])

    def _update_octal_preview(self):
        bits = {
            who: {p: self.checks[who][p].isChecked() for p in ["read","write","execute"]}
            for who in ["owner","group","others"]
        }
        import stat as st
        mode = 0
        mapping = {
            "owner":  (st.S_IRUSR, st.S_IWUSR, st.S_IXUSR),
            "group":  (st.S_IRGRP, st.S_IWGRP, st.S_IXGRP),
            "others": (st.S_IROTH, st.S_IWOTH, st.S_IXOTH),
        }
        for who, flags in mapping.items():
            r, w, x = flags
            if bits[who]["read"]:    mode |= r
            if bits[who]["write"]:   mode |= w
            if bits[who]["execute"]: mode |= x
        self.octal_input.setText(oct(mode)[-3:])

    def _apply(self):
        octal = self.octal_input.text().strip()
        result = self.perms.chmod(self.path, octal)
        if result["ok"]:
            self._load()
            QMessageBox.information(self, "Éxito", result["result"])
        else:
            QMessageBox.warning(self, "Error", result["error"])