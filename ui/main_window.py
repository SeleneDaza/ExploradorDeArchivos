from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStatusBar,
    QMessageBox, QInputDialog, QMenu
)
from PyQt5.QtCore import Qt
from core.filesystem import FileSystem
from core.operations import Operations
from ui.toolbar import Toolbar
from ui.file_tree import FileTree


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fs = FileSystem()
        self.ops = Operations()
        self.setWindowTitle("Explorador de Archivos")
        self.setMinimumSize(900, 600)
        self._build_ui()
        # Navegar al mismo path que usa el botón Home
        self._go_home()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = Toolbar(
            on_up=self._go_up,
            on_home=self._go_home,
            on_root=self._go_root,
            on_new_folder=self._new_folder,
            on_new_file=self._new_file,
        )
        layout.addWidget(self.toolbar)

        self.file_tree = FileTree(self.fs)
        self.file_tree.path_changed.connect(self._on_path_changed)
        self.file_tree.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.list_view.customContextMenuRequested.connect(self._context_menu)
        layout.addWidget(self.file_tree)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    # ── navegación ───────────────────────────────────────────

    def _go_up(self):
        from pathlib import Path
        parent = str(Path(self.fs.get_current_path()).parent)
        self.file_tree.navigate_to(parent)

    def _go_home(self):
        self.file_tree.navigate_to(self.fs.get_home())

    def _go_root(self):
        self.file_tree.navigate_to(self.fs.get_root())

    def _on_path_changed(self, path: str):
        self.toolbar.set_path(path)
        self.status.showMessage(f"  {path}")

    # ── menú contextual ──────────────────────────────────────

    def _context_menu(self, pos):
        selected = self.file_tree.get_selected_path()
        menu = QMenu(self)

        if selected:
            menu.addAction("Renombrar",  lambda: self._rename(selected))
            menu.addAction("Copiar",      lambda: self._copy(selected))
            menu.addAction("Mover",       lambda: self._move(selected))
            menu.addSeparator()
            menu.addAction("Eliminar",    lambda: self._delete(selected))
            menu.addSeparator()
            menu.addAction("Permisos",    lambda: self._show_permissions(selected))
        else:
            menu.addAction("Nueva carpeta", self._new_folder)
            menu.addAction("Nuevo archivo", self._new_file)

        menu.exec_(self.file_tree.list_view.mapToGlobal(pos))

    # ── operaciones ──────────────────────────────────────────

    def _new_folder(self):
        name, ok = QInputDialog.getText(self, "Nueva carpeta", "Nombre:")
        if ok and name:
            result = self.ops.create_folder(self.fs.get_current_path(), name)
            self._show_result(result)

    def _new_file(self):
        name, ok = QInputDialog.getText(self, "Nuevo archivo", "Nombre:")
        if ok and name:
            result = self.ops.create_file(self.fs.get_current_path(), name)
            self._show_result(result)

    def _rename(self, path):
        from pathlib import Path
        name, ok = QInputDialog.getText(
            self, "Renombrar", "Nuevo nombre:",
            text=Path(path).name
        )
        if ok and name:
            result = self.ops.rename(path, name)
            self._show_result(result)

    def _copy(self, path):
        dest, ok = QInputDialog.getText(
            self, "Copiar", "Destino (ruta completa):",
            text=self.fs.get_current_path()
        )
        if ok and dest:
            result = self.ops.copy(path, dest)
            self._show_result(result)

    def _move(self, path):
        dest, ok = QInputDialog.getText(
            self, "Mover", "Destino (ruta completa):",
            text=self.fs.get_current_path()
        )
        if ok and dest:
            result = self.ops.move(path, dest)
            self._show_result(result)

    def _delete(self, path):
        from pathlib import Path
        reply = QMessageBox.question(
            self, "Eliminar",
            f"¿Eliminar '{Path(path).name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            result = self.ops.delete(path)
            self._show_result(result)

    # ── permisos ─────────────────────────────────────────────

    def _show_permissions(self, path):
        from ui.dialogs.permissions_dialog import PermissionsDialog
        dialog = PermissionsDialog(path, parent=self)
        dialog.exec_()

    # ── helpers ──────────────────────────────────────────────

    def _show_result(self, result: dict):
        if result["ok"]:
            self.status.showMessage(f"  {result['result']}")
        else:
            QMessageBox.warning(self, "Error", result["error"])