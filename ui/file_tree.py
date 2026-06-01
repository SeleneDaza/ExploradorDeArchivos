from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
    QSplitter, QPushButton, QLabel, QFileSystemModel, QHeaderView,
)
from PyQt5.QtCore import Qt, QDir, QModelIndex, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QLinearGradient

from ui.theme import DARK, S
from core.personalizer import COLORS


class _SpanishFSModel(QFileSystemModel):
    """QFileSystemModel con cabeceras de columna en español."""
    _HEADERS = ("Nombre", "Tamaño", "Tipo", "Fecha de modificación")

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self._HEADERS):
                return self._HEADERS[section]
        return super().headerData(section, orientation, role)


class _HeatLegend(QWidget):
    """Barra de degradado verde→amarillo→naranja→rojo con etiquetas."""
    _STOPS = [(0.00, (100,210,120)), (0.40, (230,215,75)),
              (0.70, (240,148,54)),  (1.00, (228,82,82))]
    _LABELS = [("Pequeño", 0.0), ("Medio", 0.4), ("Grande", 0.75), ("Muy grande", 1.0)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 20)
        self.setToolTip("Mapa de calor: verde = archivos pequeños, rojo = muy grandes")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bar_h = 6
        bar_y = (h - bar_h) // 2

        grad = QLinearGradient(0, 0, w, 0)
        for t, (r, g, b) in self._STOPS:
            grad.setColorAt(t, QColor(r, g, b))
        p.setPen(Qt.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(QRect(0, bar_y, w, bar_h), 3, 3)

        p.setPen(QColor(150, 150, 170))
        f = p.font(); f.setPointSize(7); p.setFont(f)
        for label, t in self._LABELS:
            x = int(t * (w - 1))
            p.drawLine(x, bar_y - 1, x, bar_y + bar_h + 1)


class FileTree(QWidget):
    path_changed = pyqtSignal(str)

    def __init__(self, filesystem):
        super().__init__()
        self.fs = filesystem
        self._color_btns: dict[str, QPushButton] = {}
        self._sort_bar:   QWidget = None
        self._delegate    = None
        self._T = DARK
        self._build_ui()

    # ── construcción ─────────────────────────────────────────

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # ── árbol de directorios (panel izquierdo) ────────────
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
        self.tree_view.setMinimumWidth(180)
        self.tree_view.clicked.connect(self._on_tree_clicked)
        splitter.addWidget(self.tree_view)

        # ── panel derecho: filtros + vista detalle ─────────────
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._sort_bar = self._make_filter_bar()
        rl.addWidget(self._sort_bar)

        # modelo con cabeceras en español
        self.list_model = _SpanishFSModel()
        self.list_model.setRootPath(self.fs.get_home())
        self.list_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.list_model.directoryLoaded.connect(lambda _: self._update_size_range())

        # vista detalle (columnas)
        self.list_view = QTreeView()
        self.list_view.setModel(self.list_model)
        self.list_view.setRootIsDecorated(False)   # sin flechas de expansión
        self.list_view.setItemsExpandable(False)   # sin expandir
        self.list_view.setSortingEnabled(True)
        self.list_view.setSelectionMode(QTreeView.ExtendedSelection)
        self.list_view.setIconSize(QSize(S(20), S(20)))
        self.list_view.doubleClicked.connect(self._on_list_double_clicked)
        self._configure_header()

        from ui.delegates.file_delegate import FileItemDelegate
        self._delegate = FileItemDelegate(self.list_model, self.list_view)
        self.list_view.setItemDelegate(self._delegate)

        rl.addWidget(self.list_view)
        splitter.addWidget(right)
        splitter.setSizes([220, 680])
        layout.addWidget(splitter)

    def _configure_header(self):
        h = self.list_view.header()
        h.setSortIndicatorShown(True)
        h.setSectionsClickable(True)
        h.setStretchLastSection(False)
        # Nombre se expande; el resto tiene ancho fijo
        h.setSectionResizeMode(0, QHeaderView.Stretch)
        h.setSectionResizeMode(1, QHeaderView.Fixed)
        h.setSectionResizeMode(2, QHeaderView.Fixed)
        h.setSectionResizeMode(3, QHeaderView.Fixed)
        h.resizeSection(1, 90)    # Tamaño
        h.resizeSection(2, 150)   # Tipo
        h.resizeSection(3, 170)   # Fecha
        self._apply_header_theme(self._T)

    def _apply_header_theme(self, T: dict):
        self.list_view.header().setStyleSheet(f"""
            QHeaderView::section {{
                background: {T['panel']};
                color: {T['text_sub']};
                border: none;
                border-bottom: 1px solid {T['border']};
                border-right: 1px solid {T['border']};
                padding: {S(5)}px {S(10)}px;
                font-size: {S(13)}px;
                font-weight: 600;
            }}
            QHeaderView::section:hover {{
                background: {T['overlay']};
                color: {T['text']};
            }}
            QHeaderView::section:checked {{
                background: {T['overlay']};
                color: {T['accent']};
            }}
        """)

    # ── barra de filtros de color ─────────────────────────────

    def _make_filter_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(36)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(6)

        lbl = QLabel("Filtrar:")
        self._filter_lbl = lbl
        lay.addWidget(lbl)

        for color_key, (hex_c, label) in COLORS.items():
            cb = QPushButton()
            cb.setFixedSize(14, 14)
            cb.setCheckable(True)
            cb.setToolTip(f"Filtrar por color: {label}")
            cb.setStyleSheet(
                f"QPushButton {{ background:{hex_c}; border:2px solid transparent;"
                f"border-radius:7px; }}"
                f"QPushButton:hover {{ border-color:#ffffff88; }}"
                f"QPushButton:checked {{ border-color:#ffffffcc; }}"
            )
            cb.clicked.connect(lambda _, k=color_key: self._on_color_filter(k))
            lay.addWidget(cb)
            self._color_btns[color_key] = cb

        self._clear_filter_btn = QPushButton("×")
        self._clear_filter_btn.setFixedSize(18, 18)
        self._clear_filter_btn.setToolTip("Quitar filtro")
        self._clear_filter_btn.setVisible(False)
        self._clear_filter_btn.clicked.connect(lambda: self._on_color_filter(None))
        lay.addWidget(self._clear_filter_btn)

        lay.addStretch()
        self._heat_legend = _HeatLegend()
        lay.addWidget(self._heat_legend)
        self._apply_filter_theme(bar, self._T)
        return bar

    def _apply_filter_theme(self, bar: QWidget, T: dict):
        bar.setStyleSheet(
            f"background:{T['surface']}; border-bottom:1px solid {T['border']};"
        )
        self._filter_lbl.setStyleSheet(
            f"color:{T['text_dim']}; font-size:12px; background:transparent;"
        )
        clr = f"""
            QPushButton {{
                background: {T['overlay']}; color: {T['text_dim']};
                border: none; border-radius: 9px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background:{T['accent']}; color:{T['bg']}; }}
        """
        self._clear_filter_btn.setStyleSheet(clr)

    # ── filtro de color ───────────────────────────────────────

    def _on_color_filter(self, color_key: str | None):
        for k, b in self._color_btns.items():
            b.setChecked(k == color_key)
        self._clear_filter_btn.setVisible(color_key is not None)
        if self._delegate:
            self._delegate.set_filter(color_key)
            self.list_view.viewport().update()

    def refresh_view(self):
        self.list_view.viewport().update()

    # ── tema ──────────────────────────────────────────────────

    def set_theme(self, T: dict):
        self._T = T
        self._apply_filter_theme(self._sort_bar, T)
        self._apply_header_theme(T)

    def update_zoom(self):
        self._apply_filter_theme(self._sort_bar, self._T)
        self._apply_header_theme(self._T)
        self.list_view.setIconSize(QSize(S(20), S(20)))
        self._sort_bar.setFixedHeight(S(36))

    # ── navegación ────────────────────────────────────────────

    def _update_size_range(self):
        if not self._delegate:
            return
        root_idx = self.list_view.rootIndex()
        sizes = []
        for row in range(self.list_model.rowCount(root_idx)):
            idx = self.list_model.index(row, 0, root_idx)
            info = self.list_model.fileInfo(idx)
            if info.isFile():
                sizes.append(info.size())
        self._delegate.set_size_range(
            min(sizes) if sizes else 0,
            max(sizes) if sizes else 0,
        )
        self.list_view.viewport().update()

    def navigate_to(self, path: str):
        if self.fs.navigate_to(path):
            self.list_view.setRootIndex(self.list_model.index(path))
            self.list_model.setRootPath(path)

            tree_index = self.tree_model.index(path)
            self.tree_view.setCurrentIndex(tree_index)
            self.tree_view.scrollTo(tree_index)
            self.tree_view.expand(tree_index)

            self.path_changed.emit(path)
            self._update_size_range()

    def _on_tree_clicked(self, index: QModelIndex):
        self.navigate_to(self.tree_model.filePath(index))

    # ── selección ─────────────────────────────────────────────

    def get_selected_path(self) -> str | None:
        index = self.list_view.currentIndex()
        if index.isValid():
            # asegurar columna 0 para obtener la ruta correcta
            col0 = self.list_model.index(index.row(), 0, index.parent())
            return self.list_model.filePath(col0)
        return None

    def get_selected_paths(self) -> list[str]:
        # con QTreeView, selectedIndexes devuelve todas las columnas — filtrar col 0
        return [
            self.list_model.filePath(i)
            for i in self.list_view.selectedIndexes()
            if i.column() == 0
        ]

    # ── doble clic en lista ───────────────────────────────────

    def _on_list_double_clicked(self, index: QModelIndex):
        col0 = self.list_model.index(index.row(), 0, index.parent())
        path = self.list_model.filePath(col0)
        if self.list_model.fileInfo(col0).isDir():
            self.navigate_to(path)
        else:
            self.path_changed.emit(f"Archivo: {path}")
