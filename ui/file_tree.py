from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTreeView, QListView,
    QSplitter, QPushButton, QLabel, QFileSystemModel,
)
from PyQt5.QtCore import Qt, QDir, QModelIndex, pyqtSignal, QSize

from ui.theme import DARK, S
from core.personalizer import COLORS

_SORT_LABELS = ("Nombre", "Tamaño", "Tipo", "Fecha")


class FileTree(QWidget):
    path_changed = pyqtSignal(str)

    def __init__(self, filesystem):
        super().__init__()
        self.fs = filesystem
        self._sort_col = 0
        self._sort_asc = True
        self._icon_mode = True
        self._sort_btns:    list[QPushButton] = []
        self._color_btns:   dict[str, QPushButton] = {}
        self._sort_bar:     QWidget = None
        self._sort_lbl:     QLabel  = None
        self._btn_list_mode: QPushButton = None
        self._btn_icon_mode: QPushButton = None
        self._delegate = None
        self._T = DARK
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
        self.tree_view.setRootIndex(self.tree_model.index(self.fs.get_root()))
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setMinimumWidth(200)
        self.tree_view.clicked.connect(self._on_tree_clicked)

        # ── panel derecho: barra de orden + lista ───────────────
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._sort_bar = self._make_sort_bar()
        rl.addWidget(self._sort_bar)

        self.list_model = QFileSystemModel()
        self.list_model.setRootPath(self.fs.get_home())
        self.list_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)

        self.list_view = QListView()
        self.list_view.setModel(self.list_model)
        self.list_view.setSelectionMode(QListView.ExtendedSelection)
        self.list_view.doubleClicked.connect(self._on_list_double_clicked)
        self._apply_view_mode()

        # delegate de personalización visual
        from ui.delegates.file_delegate import FileItemDelegate
        self._delegate = FileItemDelegate(self.list_model, self.list_view)
        self.list_view.setItemDelegate(self._delegate)

        rl.addWidget(self.list_view)

        splitter.addWidget(self.tree_view)
        splitter.addWidget(right)
        splitter.setSizes([220, 680])

        layout.addWidget(splitter)

    def _make_sort_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(6)

        self._sort_lbl = QLabel("Ordenar:")
        lay.addWidget(self._sort_lbl)

        for i, name in enumerate(_SORT_LABELS):
            b = QPushButton(name)
            b.setFixedHeight(26)
            b.setCheckable(True)
            b.clicked.connect(lambda _, col=i: self._sort_by(col))
            lay.addWidget(b)
            self._sort_btns.append(b)

        self._sort_btns[0].setChecked(True)
        lay.addStretch()

        # ── toggle vista ──
        from ui.icons import tinted_icon as _ti
        _vsz = QSize(14, 14)
        _vtint = self._T["text_sub"]

        self._btn_list_mode = QPushButton()
        self._btn_list_mode.setFixedSize(28, 26)
        self._btn_list_mode.setToolTip("Vista lista")
        self._btn_list_mode.setIcon(_ti("list", _vtint))
        self._btn_list_mode.setIconSize(_vsz)
        self._btn_list_mode.setCheckable(True)
        self._btn_list_mode.clicked.connect(lambda: self._set_view_mode(False))

        self._btn_icon_mode = QPushButton()
        self._btn_icon_mode.setFixedSize(28, 26)
        self._btn_icon_mode.setToolTip("Vista iconos")
        self._btn_icon_mode.setIcon(_ti("layout-grid", _vtint))
        self._btn_icon_mode.setIconSize(_vsz)
        self._btn_icon_mode.setCheckable(True)
        self._btn_icon_mode.setChecked(True)
        self._btn_icon_mode.clicked.connect(lambda: self._set_view_mode(True))

        lay.addWidget(self._btn_list_mode)
        lay.addWidget(self._btn_icon_mode)

        # ── separador + filtros de color ──
        sep = QPushButton()
        sep.setFixedSize(1, 20)
        sep.setEnabled(False)
        lay.addSpacing(6)

        for color_key, (hex_c, label) in COLORS.items():
            cb = QPushButton()
            cb.setFixedSize(14, 14)
            cb.setCheckable(True)
            cb.setToolTip(f"Filtrar: {label}")
            cb.setStyleSheet(
                f"QPushButton {{ background:{hex_c}; border:2px solid transparent;"
                f"border-radius:7px; }}"
                f"QPushButton:hover {{ border-color:#ffffff88; }}"
                f"QPushButton:checked {{ border-color:#ffffffcc; }}"
            )
            cb.clicked.connect(lambda _, k=color_key: self._on_color_filter(k))
            lay.addWidget(cb)
            self._color_btns[color_key] = cb

        # botón quitar filtro
        self._clear_filter_btn = QPushButton("×")
        self._clear_filter_btn.setFixedSize(18, 18)
        self._clear_filter_btn.setToolTip("Quitar filtro de color")
        self._clear_filter_btn.setVisible(False)
        self._clear_filter_btn.clicked.connect(lambda: self._on_color_filter(None))
        lay.addWidget(self._clear_filter_btn)

        self._apply_sort_theme(bar, T=self._T)
        return bar

    def _apply_sort_theme(self, bar: QWidget, T: dict):
        bar.setStyleSheet(
            f"background:{T['surface']}; border-bottom:1px solid {T['border']};"
        )
        self._sort_lbl.setStyleSheet(
            f"color:{T['text_dim']}; font-size:12px; background:transparent;"
        )
        sort_style = f"""
            QPushButton {{
                background: transparent; color: {T['text_sub']};
                border: none; font-size: 12px;
                padding: 0 8px; border-radius: 4px;
            }}
            QPushButton:hover {{ background: {T['overlay']}; color: {T['text']}; }}
            QPushButton:checked {{
                background: {T['overlay']}; color: {T['accent']}; font-weight: bold;
            }}
        """
        for b in self._sort_btns:
            b.setStyleSheet(sort_style)

        view_style = f"""
            QPushButton {{
                background: transparent; color: {T['text_dim']};
                border: 1px solid {T['border']}; border-radius: 3px;
                font-size: 13px; padding: 0;
            }}
            QPushButton:hover {{ background: {T['overlay']}; color: {T['text']}; }}
            QPushButton:checked {{
                background: {T['accent']}; color: {T['bg']}; border-color: {T['accent']};
            }}
        """
        if self._btn_list_mode:
            self._btn_list_mode.setStyleSheet(view_style)
        if self._btn_icon_mode:
            self._btn_icon_mode.setStyleSheet(view_style)

    def _apply_view_mode(self):
        if self._icon_mode:
            self.list_view.setViewMode(QListView.IconMode)
            self.list_view.setMovement(QListView.Static)      # evita drag; habilita click
            self.list_view.setResizeMode(QListView.Adjust)
            self.list_view.setIconSize(QSize(S(56), S(56)))
            self.list_view.setGridSize(QSize(S(96), S(86)))
            self.list_view.setWordWrap(True)
            self.list_view.setUniformItemSizes(True)
            self.list_view.setSpacing(S(4))
        else:
            self.list_view.setViewMode(QListView.ListMode)
            self.list_view.setMovement(QListView.Static)
            self.list_view.setResizeMode(QListView.Fixed)
            self.list_view.setIconSize(QSize(S(20), S(20)))
            self.list_view.setGridSize(QSize())
            self.list_view.setWordWrap(False)
            self.list_view.setUniformItemSizes(False)
            self.list_view.setSpacing(0)

    def _set_view_mode(self, icon_mode: bool):
        self._icon_mode = icon_mode
        self._apply_view_mode()
        if self._btn_icon_mode:
            self._btn_icon_mode.setChecked(icon_mode)
        if self._btn_list_mode:
            self._btn_list_mode.setChecked(not icon_mode)

    def _on_color_filter(self, color_key: str | None):
        # desmarcar todos los color buttons
        for k, b in self._color_btns.items():
            b.setChecked(k == color_key)
        self._clear_filter_btn.setVisible(color_key is not None)
        if self._delegate:
            self._delegate.set_filter(color_key)
            self.list_view.viewport().update()

    def refresh_view(self):
        """Repinta la lista para reflejar cambios de personalización."""
        self.list_view.viewport().update()

    def set_theme(self, T: dict):
        self._T = T
        self._apply_sort_theme(self._sort_bar, T)
        self._apply_view_mode()
        if self._btn_list_mode and self._btn_icon_mode:
            from ui.icons import tinted_icon as _ti
            _vsz = QSize(14, 14)
            tint = T["text_sub"]
            self._btn_list_mode.setIcon(_ti("list", tint))
            self._btn_list_mode.setIconSize(_vsz)
            self._btn_icon_mode.setIcon(_ti("layout-grid", tint))
            self._btn_icon_mode.setIconSize(_vsz)

    def update_zoom(self):
        self._apply_sort_theme(self._sort_bar, self._T)
        self._apply_view_mode()
        self._sort_bar.setFixedHeight(S(36))

    def _sort_by(self, col: int):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True

        for i, b in enumerate(self._sort_btns):
            b.setChecked(i == col)
            arrow = (" ▲" if self._sort_asc else " ▼") if i == col else ""
            b.setText(_SORT_LABELS[i] + arrow)

        order = Qt.AscendingOrder if self._sort_asc else Qt.DescendingOrder
        self.list_model.sort(col, order)

    def navigate_to(self, path: str):
        if self.fs.navigate_to(path):
            self.list_view.setRootIndex(self.list_model.index(path))
            self.list_model.setRootPath(path)

            tree_index = self.tree_model.index(path)
            self.tree_view.setCurrentIndex(tree_index)
            self.tree_view.scrollTo(tree_index)
            self.tree_view.expand(tree_index)

            self.path_changed.emit(path)
            order = Qt.AscendingOrder if self._sort_asc else Qt.DescendingOrder
            self.list_model.sort(self._sort_col, order)

    def get_selected_path(self) -> str | None:
        index = self.list_view.currentIndex()
        if index.isValid():
            return self.list_model.filePath(index)
        return None

    def get_selected_paths(self) -> list[str]:
        return [self.list_model.filePath(i) for i in self.list_view.selectedIndexes()]

    def _on_tree_clicked(self, index: QModelIndex):
        self.navigate_to(self.tree_model.filePath(index))

    def _on_list_double_clicked(self, index: QModelIndex):
        path = self.list_model.filePath(index)
        if self.list_model.fileInfo(index).isDir():
            self.navigate_to(path)
        else:
            self.path_changed.emit(f"Archivo: {path}")
