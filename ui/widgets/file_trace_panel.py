from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QProgressBar, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
import subprocess
import os
from pathlib import Path

from core import tracker


class TraceWorker(QThread):
    progress = pyqtSignal(int)
    duplicates_found = pyqtSignal(list)
    references_found = pyqtSignal(list)
    finished = pyqtSignal()

    def __init__(self, target_path: str, roots=None):
        super().__init__()
        self.target_path = target_path
        self.roots = roots
        self._stop = False

    def run(self):
        # Stage 1: duplicates
        self.progress.emit(5)
        dups = tracker.find_duplicates(self.target_path, roots=self.roots)
        if self._stop:
            self.finished.emit()
            return
        self.duplicates_found.emit(dups)
        self.progress.emit(50)

        # Stage 2: references (may be expensive)
        refs = tracker.find_references(self.target_path, roots=self.roots)
        if self._stop:
            self.finished.emit()
            return
        self.references_found.emit(refs)
        self.progress.emit(100)
        self.finished.emit()

    def stop(self):
        self._stop = True


class FileTracePanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Rastreo de Archivo", parent)
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.widget = QWidget()
        self.setWidget(self.widget)
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(8, 8, 8, 8)

        # Header info
        self.label_name = QLabel("Archivo: -")
        self.label_type = QLabel("Tipo: -")
        self.label_size = QLabel("Tamaño: -")
        self.label_mtime = QLabel("Modificado: -")

        self.layout.addWidget(self.label_name)
        self.layout.addWidget(self.label_type)
        self.layout.addWidget(self.label_size)
        self.layout.addWidget(self.label_mtime)

        # progress & controls
        h = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setEnabled(False)
        h.addWidget(self.progress)
        h.addWidget(self.btn_cancel)
        self.layout.addLayout(h)

        # summary
        self.label_summary = QLabel("Resumen: -")
        self.layout.addWidget(self.label_summary)

        # results list
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # actions
        self.btn_clear = QPushButton("Limpiar")
        self.layout.addWidget(self.btn_clear)

        self.worker = None
        self.target = None
        self.roots = [str(Path.home())]

        # connections
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_clear.clicked.connect(self._on_clear)
        self.list_widget.itemDoubleClicked.connect(self._on_item_open)

    def start_trace(self, path: str, roots=None):
        self.target = path
        if roots is not None:
            self.roots = roots
        # set header
        p = Path(path)
        self.label_name.setText(f"Archivo: {p.name}")
        self.label_type.setText(f"Tipo: {'Directorio' if p.is_dir() else p.suffix or 'Desconocido'}")
        try:
            st = p.stat()
            self.label_size.setText(f"Tamaño: {st.st_size} bytes")
            self.label_mtime.setText(f"Modificado: {st.st_mtime}")
        except Exception:
            pass

        # reset UI
        self.list_widget.clear()
        self.label_summary.setText("Resumen: buscando...")
        self.progress.setValue(0)
        self.btn_cancel.setEnabled(True)

        # start worker thread
        self.worker = TraceWorker(path, roots=self.roots)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.duplicates_found.connect(self._on_duplicates)
        self.worker.references_found.connect(self._on_references)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_duplicates(self, dups_list):
        # populate duplicates section
        self.list_widget.addItem("--- Duplicados ---")
        for d in dups_list:
            item = QListWidgetItem(f"{Path(d['path']).name} — {d['path']}")
            item.setData(Qt.UserRole, d)
            self.list_widget.addItem(item)
        self._update_summary(dups=len(dups_list))

    def _on_references(self, refs_list):
        self.list_widget.addItem("--- Referencias ---")
        for r in refs_list:
            text = f"{Path(r['path']).name} — {r['path']} (línea {r.get('line', '?')})"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, r)
            self.list_widget.addItem(item)
        self._update_summary(refs=len(refs_list))

    def _on_finished(self):
        self.btn_cancel.setEnabled(False)
        self.label_summary.setText(self.label_summary.text() + " — terminado")

    def _on_cancel(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)
            self.btn_cancel.setEnabled(False)
            self.label_summary.setText(self.label_summary.text() + " — cancelado")

    def _on_clear(self):
        self.list_widget.clear()
        self.label_summary.setText("Resumen: -")
        self.progress.setValue(0)

    def _on_item_open(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return
        path = data.get('path')
        if not path:
            return
        # show actions dialog
        menu = QMessageBox(self)
        menu.setWindowTitle("Acción")
        menu.setText(f"Acciones para:\n{path}")
        open_btn = menu.addButton("Abrir archivo", QMessageBox.AcceptRole)
        open_folder = menu.addButton("Abrir carpeta contenedora", QMessageBox.ActionRole)
        copy_path = menu.addButton("Copiar ruta", QMessageBox.ActionRole)
        delete_btn = menu.addButton("Eliminar", QMessageBox.DestructiveRole)
        cancel_btn = menu.addButton("Cancelar", QMessageBox.RejectRole)
        menu.exec_()
        clicked = menu.clickedButton()
        if clicked == open_btn:
            try:
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    subprocess.Popen(['xdg-open', path])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo abrir: {e}")
        elif clicked == open_folder:
            folder = str(Path(path).parent)
            try:
                if os.name == 'nt':
                    os.startfile(folder)
                else:
                    subprocess.Popen(['xdg-open', folder])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo abrir la carpeta: {e}")
        elif clicked == copy_path:
            try:
                from PyQt5.QtWidgets import QApplication
                QApplication.clipboard().setText(path)
            except Exception:
                pass
        elif clicked == delete_btn:
            reply = QMessageBox.question(self, "Eliminar", f"Eliminar '{Path(path).name}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    if Path(path).is_dir():
                        import shutil
                        shutil.rmtree(path)
                    else:
                        Path(path).unlink()
                    QMessageBox.information(self, "Eliminado", "Elemento eliminado")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"No se pudo eliminar: {e}")

    def _update_summary(self, dups=0, refs=0):
        # simplistic counters
        current = self.label_summary.text()
        # parse previous values if any
        self.label_summary.setText(f"Duplicados: {dups} — Referencias: {refs}")
