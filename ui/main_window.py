from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMessageBox, QInputDialog, QMenu,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from core.filesystem import FileSystem
from core.operations import Operations
from ui.toolbar import Toolbar
from ui.file_tree import FileTree

DARK = {
    "bg":          "#1e1e2e",
    "sidebar":     "#181825",
    "panel":       "#24243e",
    "accent":      "#cba6f7",
    "accent2":     "#89b4fa",
    "text":        "#cdd6f4",
    "text_dim":    "#6c7086",
    "hover":       "#313244",
    "border":      "#313244",
    "success":     "#a6e3a1",
    "warning":     "#f38ba8",
}


def apply_dark_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(DARK["bg"]))
    palette.setColor(QPalette.WindowText,      QColor(DARK["text"]))
    palette.setColor(QPalette.Base,            QColor(DARK["panel"]))
    palette.setColor(QPalette.AlternateBase,   QColor(DARK["sidebar"]))
    palette.setColor(QPalette.Text,            QColor(DARK["text"]))
    palette.setColor(QPalette.Button,          QColor(DARK["hover"]))
    palette.setColor(QPalette.ButtonText,      QColor(DARK["text"]))
    palette.setColor(QPalette.Highlight,       QColor(DARK["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor(DARK["bg"]))
    palette.setColor(QPalette.ToolTipBase,     QColor(DARK["panel"]))
    palette.setColor(QPalette.ToolTipText,     QColor(DARK["text"]))
    app.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fs  = FileSystem()
        self.ops = Operations()
        self.setWindowTitle("Explorador de Archivos")
        self.setMinimumSize(1000, 650)
        self._build_ui()
        # Navegar al mismo path que usa el botón Home
        self._go_home()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {DARK['bg']};
            }}
            QTreeView, QListView {{
                background: {DARK['sidebar']};
                color: {DARK['text']};
                border: none;
                font-size: 13px;
                outline: none;
            }}
            QTreeView::item:hover, QListView::item:hover {{
                background: {DARK['hover']};
                border-radius: 6px;
            }}
            QTreeView::item:selected, QListView::item:selected {{
                background: {DARK['accent']};
                color: {DARK['bg']};
                border-radius: 6px;
            }}
            QScrollBar:vertical {{
                background: {DARK['bg']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {DARK['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {DARK['bg']};
                height: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {DARK['border']};
                border-radius: 4px;
            }}
            QMenu {{
                background: {DARK['panel']};
                color: {DARK['text']};
                border: 1px solid {DARK['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background: {DARK['hover']};
            }}
            QMenu::separator {{
                background: {DARK['border']};
                height: 1px;
                margin: 4px 8px;
            }}
            QDialog {{
                background: {DARK['bg']};
                color: {DARK['text']};
            }}
            QGroupBox {{
                color: {DARK['accent']};
                border: 1px solid {DARK['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding: 8px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
            QCheckBox {{
                color: {DARK['text']};
            }}
            QCheckBox::indicator:checked {{
                background: {DARK['accent']};
                border-radius: 3px;
            }}
            QLineEdit {{
                background: {DARK['panel']};
                color: {DARK['text']};
                border: 1px solid {DARK['border']};
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {DARK['accent']};
            }}
            QMessageBox {{
                background: {DARK['bg']};
                color: {DARK['text']};
            }}
            QInputDialog {{
                background: {DARK['bg']};
                color: {DARK['text']};
            }}
            QStatusBar {{
                background: {DARK['sidebar']};
                color: {DARK['text_dim']};
                font-size: 12px;
            }}
            QSplitter::handle {{
                background: {DARK['border']};
                width: 1px;
            }}
        """)

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

        # breadcrumb
        self.breadcrumb = BreadcrumbBar()
        self.breadcrumb.path_clicked.connect(self._on_breadcrumb_clicked)
        layout.addWidget(self.breadcrumb)

        # separador
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {DARK['border']}; max-height: 1px;")
        layout.addWidget(line)

        # árbol + lista
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
        self.breadcrumb.set_path(path)
        self.status.showMessage(f"   {path}")

    def _on_breadcrumb_clicked(self, path: str):
        self.file_tree.navigate_to(path)

    # ── menú contextual ──────────────────────────────────────

    def _context_menu(self, pos):
        selected = self.file_tree.get_selected_path()
        menu = QMenu(self)

        if selected:
            menu.addAction("✏   Renombrar",  lambda: self._rename(selected))
            menu.addAction("📋  Copiar",      lambda: self._copy(selected))
            menu.addAction("✂   Mover",       lambda: self._move(selected))
            menu.addSeparator()
            menu.addAction("🗑   Eliminar",    lambda: self._delete(selected))
            menu.addSeparator()
            menu.addAction("🔒  Permisos",    lambda: self._show_permissions(selected))
        else:
            menu.addAction("📁  Nueva carpeta", self._new_folder)
            menu.addAction("📄  Nuevo archivo", self._new_file)

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

    def _show_permissions(self, path):
        from ui.dialogs.permissions_dialog import PermissionsDialog
        dialog = PermissionsDialog(path, parent=self)
        dialog.exec_()

    def _show_result(self, result: dict):
        if result["ok"]:
            self.status.showMessage(f"   ✅  {result['result']}")
        else:
            QMessageBox.warning(self, "Error", result["error"])


# ── Breadcrumb ───────────────────────────────────────────────

from PyQt5.QtCore import pyqtSignal as Signal


class BreadcrumbBar(QWidget):
    path_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(32)
        self.setStyleSheet(f"background: {DARK['bg']};")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 12, 0)
        self.layout.setSpacing(2)
        self.layout.addStretch()

    def set_path(self, path: str):
        # limpia
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from pathlib import Path
        parts = Path(path).parts
        accumulated = ""

        for i, part in enumerate(parts):
            accumulated = str(Path(accumulated) / part) if accumulated else part

            btn = QPushButton(part)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(24)

            _path = accumulated
            btn.clicked.connect(lambda _, p=_path: self.path_clicked.emit(p))

            if i == len(parts) - 1:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {DARK['accent']};
                        font-weight: bold;
                        font-size: 12px;
                        border: none;
                        padding: 0 4px;
                        background: transparent;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {DARK['text_dim']};
                        font-size: 12px;
                        border: none;
                        padding: 0 4px;
                        background: transparent;
                    }}
                    QPushButton:hover {{
                        color: {DARK['text']};
                    }}
                """)

            self.layout.insertWidget(self.layout.count() - 1, btn)

            if i < len(parts) - 1:
                sep = QLabel("›")
                sep.setStyleSheet(f"color: {DARK['text_dim']}; font-size: 14px;")
                self.layout.insertWidget(self.layout.count() - 1, sep)
