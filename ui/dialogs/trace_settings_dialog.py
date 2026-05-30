from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt
from core.tracker import get_settings, save_settings, clear_cache
from pathlib import Path
import json


class TraceSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Ajustes de Rastreo')
        self.resize(500, 400)
        layout = QVBoxLayout(self)

        self.label = QLabel('Raíces de búsqueda:')
        layout.addWidget(self.label)
        self.roots_list = QListWidget()
        layout.addWidget(self.roots_list)
        h = QHBoxLayout()
        self.root_input = QLineEdit()
        self.btn_add_root = QPushButton('Añadir')
        self.btn_browse = QPushButton('Examinar')
        h.addWidget(self.root_input)
        h.addWidget(self.btn_browse)
        h.addWidget(self.btn_add_root)
        layout.addLayout(h)

        layout.addWidget(QLabel('Excluir carpetas (patrones):'))
        self.exclude_list = QListWidget()
        layout.addWidget(self.exclude_list)
        eh = QHBoxLayout()
        self.exclude_input = QLineEdit()
        self.btn_add_exclude = QPushButton('Añadir')
        eh.addWidget(self.exclude_input)
        eh.addWidget(self.btn_add_exclude)
        layout.addLayout(eh)

        layout.addWidget(QLabel('Excluir patrones de archivo:'))
        self.pat_list = QListWidget()
        layout.addWidget(self.pat_list)
        ph = QHBoxLayout()
        self.pat_input = QLineEdit()
        self.btn_add_pat = QPushButton('Añadir')
        ph.addWidget(self.pat_input)
        ph.addWidget(self.btn_add_pat)
        layout.addLayout(ph)

        self.chk_persist = QCheckBox('Persistir cache en disco')
        layout.addWidget(self.chk_persist)

        btns = QHBoxLayout()
        self.btn_clear_cache = QPushButton('Borrar cache')
        self.btn_save = QPushButton('Guardar')
        self.btn_cancel = QPushButton('Cancelar')
        btns.addWidget(self.btn_clear_cache)
        btns.addStretch()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_add_root.clicked.connect(self._add_root)
        self.btn_browse.clicked.connect(self._browse_root)
        self.btn_add_exclude.clicked.connect(self._add_exclude)
        self.btn_add_pat.clicked.connect(self._add_pat)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear_cache.clicked.connect(self._on_clear_cache)

        self._load()

    def _load(self):
        s = get_settings()
        roots = s.get('roots', [])
        excludes = s.get('exclude_dirs', [])
        pats = s.get('exclude_file_patterns', [])
        persist = s.get('persist_cache', True)
        for r in roots:
            self.roots_list.addItem(QListWidgetItem(r))
        for e in excludes:
            self.exclude_list.addItem(QListWidgetItem(e))
        for p in pats:
            self.pat_list.addItem(QListWidgetItem(p))
        self.chk_persist.setChecked(persist)

    def _add_root(self):
        v = self.root_input.text().strip()
        if v:
            self.roots_list.addItem(QListWidgetItem(v))
            self.root_input.clear()

    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, 'Selecciona carpeta', str(Path.home()))
        if d:
            self.root_input.setText(d)

    def _add_exclude(self):
        v = self.exclude_input.text().strip()
        if v:
            self.exclude_list.addItem(QListWidgetItem(v))
            self.exclude_input.clear()

    def _add_pat(self):
        v = self.pat_input.text().strip()
        if v:
            self.pat_list.addItem(QListWidgetItem(v))
            self.pat_input.clear()

    def _on_clear_cache(self):
        reply = QMessageBox.question(self, 'Confirmar', 'Borrar cache en disco?')
        if reply == QMessageBox.Yes:
            clear_cache()
            QMessageBox.information(self, 'Cache', 'Cache borrada')

    def _on_save(self):
        roots = [self.roots_list.item(i).text() for i in range(self.roots_list.count())]
        excludes = [self.exclude_list.item(i).text() for i in range(self.exclude_list.count())]
        pats = [self.pat_list.item(i).text() for i in range(self.pat_list.count())]
        persist = self.chk_persist.isChecked()
        new = {
            'roots': roots,
            'exclude_dirs': excludes,
            'exclude_file_patterns': pats,
            'persist_cache': persist,
        }
        save_settings(new)
        QMessageBox.information(self, 'Guardado', 'Ajustes guardados')
        self.accept()