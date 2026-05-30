from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStatusBar
from core.filesystem import FileSystem
from ui.toolbar import Toolbar
from ui.file_tree import FileTree


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fs = FileSystem()
        self.setWindowTitle("Explorador de Archivos")
        self.setMinimumSize(900, 600)
        self._build_ui()
        self.file_tree.navigate_to(self.fs.get_home())

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # toolbar
        self.toolbar = Toolbar(
            on_up=self._go_up,
            on_home=self._go_home,
            on_root=self._go_root,
        )
        layout.addWidget(self.toolbar)

        # árbol + lista
        self.file_tree = FileTree(self.fs)
        self.file_tree.path_changed.connect(self._on_path_changed)
        layout.addWidget(self.file_tree)

        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _go_up(self):
        from pathlib import Path
        current = self.fs.get_current_path()
        parent = str(Path(current).parent)
        self.file_tree.navigate_to(parent)

    def _go_home(self):
        self.file_tree.navigate_to(self.fs.get_home())

    def _go_root(self):
        self.file_tree.navigate_to(self.fs.get_root())

    def _on_path_changed(self, path: str):
        self.toolbar.set_path(path)
        self.status.showMessage(f"  {path}")