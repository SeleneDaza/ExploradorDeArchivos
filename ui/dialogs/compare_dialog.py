from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from pathlib import Path
import hashlib
import difflib


def compute_hash(path: str, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def first_diff_offset(a: str, b: str, chunk_size: int = 4096):
    with open(a, 'rb') as fa, open(b, 'rb') as fb:
        offset = 0
        while True:
            ba = fa.read(chunk_size)
            bb = fb.read(chunk_size)
            if not ba and not bb:
                return None
            if ba == bb:
                offset += len(ba)
                continue
            # find first differing byte
            for i in range(min(len(ba), len(bb))):
                if ba[i] != bb[i]:
                    return offset + i
            return offset + min(len(ba), len(bb))


class CompareDialog(QDialog):
    def __init__(self, file_a: str, file_b: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Comparar archivos')
        self.resize(800, 600)
        a = Path(file_a)
        b = Path(file_b)

        layout = QVBoxLayout(self)

        info = QLabel(f"A: {a}\nB: {b}")
        layout.addWidget(info)

        # choose viewer based on type
        img_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        if a.suffix.lower() in img_exts and b.suffix.lower() in img_exts:
            h = QHBoxLayout()
            left = QLabel()
            right = QLabel()
            left.setAlignment(Qt.AlignCenter)
            right.setAlignment(Qt.AlignCenter)
            pix_a = QPixmap(str(a))
            pix_b = QPixmap(str(b))
            left.setPixmap(pix_a.scaled(380, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            right.setPixmap(pix_b.scaled(380, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            h.addWidget(left)
            h.addWidget(right)
            layout.addLayout(h)
        else:
            # try text diff
            try:
                with open(str(a), 'r', encoding='utf-8', errors='ignore') as fa:
                    a_lines = fa.readlines()
                with open(str(b), 'r', encoding='utf-8', errors='ignore') as fb:
                    b_lines = fb.readlines()
                diff = difflib.unified_diff(a_lines, b_lines, fromfile=str(a), tofile=str(b), lineterm='')
                te = QTextEdit()
                te.setReadOnly(True)
                te.setPlainText('\n'.join(list(diff)) or 'No textual differences found.')
                layout.addWidget(te)
            except Exception:
                # binary summary
                ha = compute_hash(str(a))
                hb = compute_hash(str(b))
                sz_a = a.stat().st_size
                sz_b = b.stat().st_size
                off = first_diff_offset(str(a), str(b))
                s = f"Hash A: {ha}\nHash B: {hb}\nSize A: {sz_a}\nSize B: {sz_b}\n"
                if off is None:
                    s += "Files are identical"
                else:
                    s += f"First differing byte offset: {off}"
                te = QTextEdit()
                te.setReadOnly(True)
                te.setPlainText(s)
                layout.addWidget(te)

        btns = QHBoxLayout()
        ok = QPushButton('Cerrar')
        ok.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(ok)
        layout.addLayout(btns)
