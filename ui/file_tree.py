from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTreeView, QListView, QSplitter
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt, QDir, QModelIndex, pyqtSignal


class FileTree(QWidget):
    path_changed = pyqtSignal(str)

    def __init__(self, filesystem):
        super().__init__()
        self.fs = filesystem
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # ── sidebar: árbol de directorios ──────────────────────
        self.tree_model = QFileSystemModel()
        self.tree_model.setRootPath(self.fs.get_root())
        self.tree_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setRootIndex(
            self.tree_model.index(self.fs.get_root())
        )
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setMinimumWidth(200)
        self.tree_view.clicked.connect(self._on_tree_clicked)

        # ── panel derecho: contenido de carpeta ─────────────────
        self.list_model = QFileSystemModel()
        self.list_model.setRootPath(self.fs.get_home())
        self.list_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)

        self.list_view = QListView()
        self.list_view.setModel(self.list_model)
        self.list_view.doubleClicked.connect(self._on_list_double_clicked)

        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.list_view)
        splitter.setSizes([220, 680])

        layout.addWidget(splitter)

    def navigate_to(self, path: str):
        if self.fs.navigate_to(path):
            self.list_view.setRootIndex(self.list_model.index(path))
            self.list_model.setRootPath(path)

            tree_index = self.tree_model.index(path)
            self.tree_view.setCurrentIndex(tree_index)
            self.tree_view.scrollTo(tree_index)
            self.tree_view.expand(tree_index)

            self.path_changed.emit(path)

    def get_selected_path(self):
        index = self.list_view.currentIndex()
        if index.isValid():
            return self.list_model.filePath(index)
        return None

    def _on_tree_clicked(self, index: QModelIndex):
        path = self.tree_model.filePath(index)
        self.navigate_to(path)

    def _on_list_double_clicked(self, index: QModelIndex):
        path = self.list_model.filePath(index)
        info = self.list_model.fileInfo(index)
        if info.isDir():
            self.navigate_to(path)
        else:
            self.path_changed.emit(f"Archivo: {path}")