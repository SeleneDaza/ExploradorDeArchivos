import os
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMessageBox, QMenu,
    QLabel, QPushButton, QFrame, QSplitter, QShortcut,
    QApplication,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QKeySequence, QFont, QColor, QPalette

from ui.theme import DARK, LIGHT, RETRO, FONT_UI, global_qss, apply_palette, btn_qss, S, get_zoom, set_zoom, R_XS
from core.filesystem import FileSystem
from core.operations import Operations
from ui.toolbar import Toolbar
from ui.file_tree import FileTree
from ui.widgets.favorites_panel import FavoritesPanel
from ui.widgets.search_bar import SearchBar
from ui.widgets.preview_panel import PreviewPanel

# re-exportar para main.py
__all__ = ["MainWindow", "apply_palette", "DARK", "LIGHT"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fs  = FileSystem()
        self.ops = Operations()
        self.history       = []
        self.history_index = -1
        self._theme_idx    = 0          # 0=DARK  1=LIGHT  2=RETRO
        self.current_theme = DARK
        self._preview_anim  = None
        self.setWindowTitle("Explorador de Archivos")
        self.setMinimumSize(1140, 700)
        self._build_ui()
        self._setup_shortcuts()
        self._go_home()

    # ── construcción ─────────────────────────────────────────

    def _build_ui(self):
        self._apply_qss(self.current_theme)
        app = QApplication.instance()
        if app:
            apply_palette(app, self.current_theme)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.toolbar = Toolbar(
            on_up=self._go_up,
            on_home=self._go_home,
            on_root=self._go_root,
            on_new_folder=self._new_folder,
            on_new_file=self._new_file,
            on_back=self._go_back,
            on_forward=self._go_forward,
            on_toggle_theme=self.toggle_theme,
            theme_idx=self._theme_idx,
            on_toggle_preview=self._toggle_preview,
        )
        root.addWidget(self.toolbar)

        self.search_bar = SearchBar()
        self.search_bar.search_triggered.connect(self._on_search)
        self.search_bar.search_cleared.connect(self._on_search_cleared)
        root.addWidget(self.search_bar)

        self.breadcrumb = BreadcrumbBar()
        self.breadcrumb.path_clicked.connect(self._on_breadcrumb_clicked)
        root.addWidget(self.breadcrumb)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{DARK['border']};")
        self._main_sep = sep
        root.addWidget(sep)

        # splitter: favoritos | árbol | vista previa
        self._splitter = QSplitter(Qt.Horizontal)

        self.favorites = FavoritesPanel()
        self.favorites.path_selected.connect(self._on_favorite_selected)
        self._splitter.addWidget(self.favorites)

        self.file_tree = FileTree(self.fs)
        self.file_tree.path_changed.connect(self._on_path_changed)
        self.file_tree.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.list_view.customContextMenuRequested.connect(self._context_menu)
        self.file_tree.list_view.doubleClicked.connect(self._on_double_click)
        self.file_tree.list_view.clicked.connect(self._on_file_clicked)
        self.file_tree.list_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self._splitter.addWidget(self.file_tree)

        self.preview = PreviewPanel()
        self.preview.request_search.connect(lambda p: self._on_search(Path(p).name))
        self.preview.request_trace.connect(self._start_trace)
        self.preview.request_favorite.connect(lambda p: self.favorites.add_favorite(p))
        self.preview.request_unfavorite.connect(lambda p: self.favorites.remove_favorite(p))
        self.preview.request_location.connect(self._navigate)
        self._splitter.addWidget(self.preview)

        self._splitter.setSizes([186, 620, 300])
        root.addWidget(self._splitter, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _setup_shortcuts(self):
        def sc(seq, fn):
            QShortcut(QKeySequence(seq), self).activated.connect(fn)

        sc("Ctrl+F",       self._focus_search)
        sc("Ctrl+N",       self._new_folder)
        sc("Ctrl+Shift+N", self._new_file)
        sc("Delete",       self._delete_selected)
        sc("F2",           self._rename_selected)
        sc("Alt+Left",     self._go_back)
        sc("Alt+Right",    self._go_forward)
        sc("Alt+Up",       self._go_up)
        sc("Ctrl+H",       self._go_home)
        sc("Ctrl+P",       self._toggle_preview)
        sc("Escape",       self._on_escape)
        sc("Ctrl+=",       self._zoom_in)
        sc("Ctrl++",       self._zoom_in)
        sc("Ctrl+-",       self._zoom_out)
        sc("Ctrl+0",       self._zoom_reset)

    # ── navegación ────────────────────────────────────────────

    def _navigate(self, path: str):
        if path == self.fs.get_current_path():
            return
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(path)
        self.history_index = len(self.history) - 1
        self.file_tree.navigate_to(path)

    def _go_up(self):
        parent = str(Path(self.fs.get_current_path()).parent)
        self._navigate(parent)

    def _go_home(self):
        self._navigate(self.fs.get_home())

    def _go_root(self):
        self._navigate(self.fs.get_root())

    def _go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.file_tree.navigate_to(self.history[self.history_index])

    def _go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.file_tree.navigate_to(self.history[self.history_index])

    def _on_path_changed(self, path: str):
        self.toolbar.set_path(path)
        self.breadcrumb.set_path(path)
        self.status.showMessage(f"   {path}")
        if not self.history or self.history[self.history_index] != path:
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index = len(self.history) - 1

    def _on_breadcrumb_clicked(self, path: str):
        self._navigate(path)

    def _on_favorite_selected(self, path: str):
        if path == "__add_current__":
            self.favorites.add_favorite(self.fs.get_current_path())
        else:
            self._navigate(path)

    # ── búsqueda ──────────────────────────────────────────────

    def _on_search(self, query: str):
        self.file_tree.list_model.setNameFilters([f"*{query}*"])
        self.file_tree.list_model.setNameFilterDisables(False)
        self.status.showMessage(f"   Buscando: '{query}'")

    def _on_search_cleared(self):
        self.file_tree.list_model.setNameFilters(["*"])
        self.file_tree.list_model.setNameFilterDisables(True)
        self.status.showMessage(f"   {self.fs.get_current_path()}")

    # ── selección ─────────────────────────────────────────────

    def _on_file_clicked(self, index):
        path = self.file_tree.list_model.filePath(index)
        if Path(path).is_file():
            self.preview.set_file(path)

    def _on_selection_changed(self):
        paths = self.file_tree.get_selected_paths()
        n = len(paths)
        if n > 1:
            self.status.showMessage(f"   {n} elementos seleccionados")
        elif n == 1:
            self.status.showMessage(f"   {paths[0]}")
        else:
            self.status.showMessage(f"   {self.fs.get_current_path()}")

    def _focus_search(self):
        self.search_bar.input.setFocus()
        self.search_bar.input.selectAll()

    def _on_escape(self):
        if self.search_bar.input.text():
            self.search_bar._on_clear()
        else:
            self.file_tree.list_view.clearSelection()
            self.preview.clear()

    # ── doble clic ────────────────────────────────────────────

    def _on_double_click(self, index):
        path = self.file_tree.list_model.filePath(index)
        info = self.file_tree.list_model.fileInfo(index)
        if info.isDir():
            self._navigate(path)
        else:
            try:
                if os.name == "nt":
                    os.startfile(path)
                else:
                    subprocess.Popen(["xdg-open", path])
            except Exception as e:
                self.status.showMessage(f"   No se pudo abrir: {e}")

    # ── panel de vista previa ─────────────────────────────────

    def _toggle_preview(self):
        if self.preview.isVisible():
            anim = QPropertyAnimation(self.preview, b"maximumWidth")
            anim.setDuration(180)
            anim.setStartValue(self.preview.width())
            anim.setEndValue(0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.finished.connect(self.preview.hide)
            anim.finished.connect(lambda: self.preview.setMaximumWidth(440))
            anim.start(QPropertyAnimation.DeleteWhenStopped)
            self._preview_anim = anim
        else:
            self.preview.setMaximumWidth(0)
            self.preview.show()
            anim = QPropertyAnimation(self.preview, b"maximumWidth")
            anim.setDuration(180)
            anim.setStartValue(0)
            anim.setEndValue(300)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.finished.connect(lambda: self.preview.setMaximumWidth(440))
            anim.start(QPropertyAnimation.DeleteWhenStopped)
            self._preview_anim = anim

    # ── menú contextual ───────────────────────────────────────

    def _context_menu(self, pos):
        paths = self.file_tree.get_selected_paths()
        menu = QMenu(self)

        if len(paths) > 1:
            n = len(paths)
            menu.addAction(f"Copiar {n} elementos",   lambda: self._copy_multi(paths))
            menu.addAction(f"Mover {n} elementos",    lambda: self._move_multi(paths))
            menu.addSeparator()
            menu.addAction(f"Eliminar {n} elementos", lambda: self._delete_multi(paths))
        elif len(paths) == 1:
            selected = paths[0]
            if Path(selected).is_file():
                menu.addAction("Rastrear uso", lambda: self._start_trace(selected))
                menu.addSeparator()
            menu.addAction("Renombrar       F2",  lambda: self._rename(selected))
            menu.addAction("Copiar",              lambda: self._copy(selected))
            menu.addAction("Mover",               lambda: self._move(selected))
            menu.addSeparator()
            menu.addAction("Eliminar        Del", lambda: self._delete(selected))
            menu.addSeparator()
            menu.addAction("Permisos",            lambda: self._show_permissions(selected))
            menu.addAction("Propiedades",         lambda: self._show_properties(selected))
        else:
            menu.addAction("Nueva carpeta   Ctrl+N",       self._new_folder)
            menu.addAction("Nuevo archivo   Ctrl+Shift+N", self._new_file)

        menu.exec_(self.file_tree.list_view.mapToGlobal(pos))

    # ── operaciones ───────────────────────────────────────────

    def _new_folder(self):
        from ui.dialogs.name_dialog import NameDialog
        name, ok = NameDialog.ask(
            self, "Nueva carpeta", "Nombre de la carpeta",
            confirm_text="Crear", placeholder="mi-carpeta",
            T=self.current_theme,
        )
        if ok and name:
            self._show_result(self.ops.create_folder(self.fs.get_current_path(), name))

    def _new_file(self):
        from ui.dialogs.name_dialog import NameDialog
        name, ok = NameDialog.ask(
            self, "Nuevo archivo", "Nombre del archivo",
            confirm_text="Crear", placeholder="archivo.txt",
            T=self.current_theme,
        )
        if ok and name:
            self._show_result(self.ops.create_file(self.fs.get_current_path(), name))

    def _rename(self, path):
        from ui.dialogs.name_dialog import NameDialog
        name, ok = NameDialog.ask(
            self, "Renombrar", "Nuevo nombre",
            confirm_text="Renombrar", initial=Path(path).name,
            T=self.current_theme,
        )
        if ok and name:
            self._show_result(self.ops.rename(path, name))

    def _rename_selected(self):
        path = self.file_tree.get_selected_path()
        if path:
            self._rename(path)

    def _delete_selected(self):
        paths = self.file_tree.get_selected_paths()
        if len(paths) > 1:
            self._delete_multi(paths)
        elif len(paths) == 1:
            self._delete(paths[0])

    def _pick_folder(self, title: str) -> str | None:
        from ui.dialogs.folder_picker_dialog import FolderPickerDialog
        dlg = FolderPickerDialog(title, self.fs.get_current_path(), parent=self)
        dlg.setStyleSheet(global_qss(self.current_theme))
        return dlg.selected_path() if dlg.exec_() else None

    def _copy(self, path):
        dest = self._pick_folder("Copiar a...")
        if dest:
            self._show_result(self.ops.copy(path, dest))

    def _move(self, path):
        dest = self._pick_folder("Mover a...")
        if dest:
            self._show_result(self.ops.move(path, dest))

    def _copy_multi(self, paths: list):
        dest = self._pick_folder(f"Copiar {len(paths)} elementos a...")
        if not dest:
            return
        errors = [r["error"] for p in paths if not (r := self.ops.copy(p, dest)).get("ok")]
        if errors:
            self.status.showMessage(f"   {len(paths)-len(errors)} copiados, {len(errors)} con error")
        else:
            self.status.showMessage(f"   {len(paths)} elementos copiados a {Path(dest).name}")

    def _move_multi(self, paths: list):
        dest = self._pick_folder(f"Mover {len(paths)} elementos a...")
        if not dest:
            return
        errors = [r["error"] for p in paths if not (r := self.ops.move(p, dest)).get("ok")]
        if errors:
            self.status.showMessage(f"   {len(paths)-len(errors)} movidos, {len(errors)} con error")
        else:
            self.status.showMessage(f"   {len(paths)} elementos movidos a {Path(dest).name}")

    def _delete_multi(self, paths: list):
        from ui.dialogs.name_dialog import NameDialog
        from PyQt5.QtWidgets import QDialog
        dlg = NameDialog(
            "Eliminar",
            f"¿Eliminar {len(paths)} elementos seleccionados?",
            confirm_text="Eliminar",
            T=self.current_theme,
            parent=self,
        )
        dlg._input.hide()
        dlg._btn_ok.setStyleSheet(btn_qss(self.current_theme, "danger"))
        dlg._result = "confirm"
        if dlg.exec_() != QDialog.Accepted:
            return
        errors = [r["error"] for p in paths if not (r := self.ops.delete(p)).get("ok")]
        if errors:
            self.status.showMessage(f"   {len(paths)-len(errors)} eliminados, {len(errors)} con error")
        else:
            self.status.showMessage(f"   {len(paths)} elementos eliminados")

    def _delete(self, path):
        from ui.dialogs.name_dialog import NameDialog
        from PyQt5.QtWidgets import QDialog
        dlg = NameDialog(
            "Eliminar",
            f"¿Eliminar '{Path(path).name}'?",
            confirm_text="Eliminar",
            T=self.current_theme,
            parent=self,
        )
        # El diálogo de confirmación no necesita input — ocultamos el campo
        dlg._input.hide()
        dlg._btn_ok.setStyleSheet(btn_qss(self.current_theme, "danger"))
        dlg._result = "confirm"
        if dlg.exec_() == QDialog.Accepted:
            self._show_result(self.ops.delete(path))

    def _show_permissions(self, path):
        from ui.dialogs.permissions_dialog import PermissionsDialog
        PermissionsDialog(path, parent=self).exec_()

    def _show_properties(self, path):
        from ui.dialogs.properties_dialog import PropertiesDialog
        PropertiesDialog(path, parent=self).exec_()

    def _show_result(self, result: dict):
        if result["ok"]:
            self.status.showMessage(f"   {result['result']}")
        else:
            QMessageBox.warning(self, "Error", result["error"])

    def _start_trace(self, path: str):
        try:
            from ui.widgets.file_trace_panel import FileTracePanel
            dlg = FileTracePanel(parent=self)
            roots = [self.fs.get_current_path(), str(Path.home())]
            exclude = [".git", "node_modules", "__pycache__", ".venv", "venv"]
            exc_pat = ["*.pyc", "*.pyo", "*.class", "*.exe"]
            dlg.start_trace(path, roots=roots, exclude_dirs=exclude,
                            exclude_file_patterns=exc_pat)
            dlg.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo iniciar el rastreo: {e}")

    # ── tema ──────────────────────────────────────────────────

    def toggle_theme(self):
        _themes = [DARK, LIGHT, RETRO]
        self._theme_idx    = (self._theme_idx + 1) % 3
        self.current_theme = _themes[self._theme_idx]
        self._propagate_theme()

    def _propagate_theme(self):
        T   = self.current_theme
        app = QApplication.instance()
        if app:
            apply_palette(app, T)
        self._apply_qss(T)
        self.toolbar.set_theme(T, self._theme_idx)
        self.search_bar.set_theme(T)
        self.breadcrumb.set_theme(T)
        self.favorites.set_theme(T)
        self.file_tree.set_theme(T)
        self.preview.set_theme(T)
        self._main_sep.setStyleSheet(f"background:{T['border']};")

    # ── zoom ──────────────────────────────────────────────────

    def _zoom_apply(self, factor: float):
        set_zoom(factor)
        pct = round(get_zoom() * 100)
        self._propagate_theme()
        self.toolbar.update_zoom(pct)
        self.search_bar.update_zoom()
        self.breadcrumb.update_zoom()
        self.favorites.update_zoom()
        self.file_tree.update_zoom()
        self.status.showMessage(
            f"   Zoom {pct}%  —  use Ctrl+0 para restablecer"
        )

    def _zoom_in(self):
        self._zoom_apply(round(get_zoom() + 0.1, 2))

    def _zoom_out(self):
        self._zoom_apply(round(max(0.75, get_zoom() - 0.1), 2))

    def _zoom_reset(self):
        self._zoom_apply(1.0)

    def _apply_qss(self, T: dict):
        self.setStyleSheet(global_qss(T))

    # ── acciones del breadcrumb ───────────────────────────────

    def _on_breadcrumb_clicked(self, path: str):
        self._navigate(path)


# ── BreadcrumbBar ─────────────────────────────────────────────

class BreadcrumbBar(QWidget):
    path_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._T    = DARK
        self._path = ""
        self.setFixedHeight(S(36))
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(S(16), 0, S(16), 0)
        self._layout.setSpacing(S(2))
        self._layout.addStretch()
        self.set_theme(DARK)

    def update_zoom(self):
        self.setFixedHeight(S(36))
        if self._path:
            self.set_path(self._path)

    def set_theme(self, T: dict):
        self._T = T
        self.setStyleSheet(
            f"background:{T['bg']}; border-bottom: 1px solid {T['border']};"
        )
        if self._path:
            self.set_path(self._path)

    def set_path(self, path: str):
        self._path = path
        # limpiar
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        T = self._T
        parts       = Path(path).parts
        accumulated = ""

        for i, part in enumerate(parts):
            accumulated = str(Path(accumulated) / part) if accumulated else part
            is_last = (i == len(parts) - 1)

            btn = QPushButton(part)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(S(26))

            if is_last:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {T['accent']}; font-weight: 700; font-size: {S(13)}px;
                        border: none; padding: 0 {S(6)}px; background: transparent;
                        border-radius: {S(6)}px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {T['text_dim']}; font-size: {S(13)}px;
                        border: none; padding: 0 {S(6)}px; background: transparent;
                        border-radius: {S(6)}px;
                    }}
                    QPushButton:hover {{
                        color: {T['text']}; background: {T['overlay']};
                    }}
                """)

            _p = accumulated
            btn.clicked.connect(lambda _, p=_p: self.path_clicked.emit(p))
            self._layout.insertWidget(self._layout.count() - 1, btn)

            if not is_last:
                sep = QLabel("›")
                sep.setStyleSheet(f"color:{T['text_dim']}; font-size:{S(15)}px; background:transparent;")
                self._layout.insertWidget(self._layout.count() - 1, sep)
