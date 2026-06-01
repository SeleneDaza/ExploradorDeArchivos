from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeView,
    QPushButton, QLabel, QFileSystemModel,
)
from PyQt5.QtCore import Qt, QDir


class FolderPickerDialog(QDialog):
    def __init__(self, title: str, start_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(420, 480)
        self._selected = start_path
        self._build_ui(start_path)

    def _build_ui(self, start_path: str):
        lay = QVBoxLayout(self)
        lay.setSpacing(8)

        self._lbl = QLabel(f"Destino:  {start_path}")
        self._lbl.setWordWrap(True)
        lay.addWidget(self._lbl)

        self._model = QFileSystemModel()
        self._model.setRootPath(self._model.myComputer())
        self._model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Drives)

        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.hideColumn(1)
        self._tree.hideColumn(2)
        self._tree.hideColumn(3)
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)

        # expand and scroll to start_path
        idx = self._model.index(start_path)
        self._tree.setCurrentIndex(idx)
        self._tree.scrollTo(idx)
        self._tree.expand(idx)

        self._tree.clicked.connect(self._on_clicked)
        lay.addWidget(self._tree, 1)

        # buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok = QPushButton("Seleccionar")
        ok.setDefault(True)
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        btn_row.addWidget(ok)
        lay.addLayout(btn_row)

    def _on_clicked(self, index):
        path = self._model.filePath(index)
        self._selected = path
        self._lbl.setText(f"Destino:  {path}")

    def selected_path(self) -> str:
        return self._selected
