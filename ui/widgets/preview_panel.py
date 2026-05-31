"""
Panel lateral de Vista Previa Inteligente.
Soporta: imagen, PDF, texto, código, video, audio y archivos desconocidos.
Dependencias opcionales: PyMuPDF (pdf), opencv-python (thumbnail video), mutagen (duración audio).
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QFrame, QProgressBar, QStackedWidget,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor, QSyntaxHighlighter, QTextCharFormat

# ── open-count persistence ────────────────────────────────────

_CACHE_DIR   = Path.home() / ".explorador_cache"
_COUNTS_FILE = _CACHE_DIR / "open_counts.json"
_counts: dict = {}


def _load_counts():
    global _counts
    try:
        if _COUNTS_FILE.exists():
            _counts = json.loads(_COUNTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        _counts = {}


def _save_counts():
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _COUNTS_FILE.write_text(json.dumps(_counts, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def increment_open_count(path: str):
    _counts[path] = _counts.get(path, 0) + 1
    _save_counts()


def get_open_count(path: str) -> int:
    return _counts.get(path, 0)


_load_counts()

# ── helpers ───────────────────────────────────────────────────

def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _fmt_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y  %H:%M")


# ── file-type detection ───────────────────────────────────────

_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico", ".tiff"}
_VIDEO = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"}
_AUDIO = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma", ".opus"}
_PDF   = {".pdf"}
_CODE  = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".htm", ".css", ".scss",
    ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".swift", ".go", ".rs",
    ".rb", ".php", ".sh", ".bash", ".bat", ".ps1", ".sql",
    ".json", ".yaml", ".yml", ".toml", ".xml", ".md",
}
_TEXT  = {".txt", ".log", ".csv", ".ini", ".cfg", ".conf", ".env", ".gitignore"}


def _file_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in _IMAGE: return "image"
    if ext in _VIDEO: return "video"
    if ext in _AUDIO: return "audio"
    if ext in _PDF:   return "pdf"
    if ext in _CODE:  return "code"
    if ext in _TEXT:  return "text"
    try:
        with open(path, "rb") as f:
            if b"\x00" not in f.read(512):
                return "text"
    except Exception:
        pass
    return "unknown"


def _lang(path: str) -> str:
    return {
        ".py": "python", ".js": "js", ".ts": "js", ".jsx": "js", ".tsx": "js",
        ".html": "html", ".htm": "html", ".css": "css", ".scss": "css",
        ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".sh": "shell", ".bash": "shell", ".bat": "shell", ".ps1": "shell",
        ".md": "markdown", ".xml": "html",
    }.get(Path(path).suffix.lower(), "generic")


# ── syntax highlighter ────────────────────────────────────────

_KW = {
    "python": (
        r"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|"
        r"elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|"
        r"not|or|pass|raise|return|self|try|while|with|yield)\b"
    ),
    "js": (
        r"\b(async|await|break|case|catch|class|const|continue|delete|do|else|export|"
        r"extends|false|finally|for|from|function|if|import|in|instanceof|let|new|null|"
        r"of|return|super|switch|this|throw|true|try|typeof|undefined|var|void|while|yield)\b"
    ),
    "html": r"(</?[A-Za-z][A-Za-z0-9]*)",
}


class _Highlighter(QSyntaxHighlighter):
    def __init__(self, doc, lang: str):
        super().__init__(doc)
        self._rules = []
        C = dict(kw="#cba6f7", s="#a6e3a1", c="#6c7086", n="#fab387", fn="#89b4fa", tag="#f38ba8")

        def f(color, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:   fmt.setFontWeight(QFont.Bold)
            if italic: fmt.setFontItalic(True)
            return fmt

        kw_pat = _KW.get(lang)
        if kw_pat and lang != "html":
            self._rules.append((re.compile(kw_pat), f(C["kw"], bold=True)))

        # strings
        self._rules += [
            (re.compile(r'"(?:[^"\\]|\\.)*"'),  f(C["s"])),
            (re.compile(r"'(?:[^'\\]|\\.)*'"),  f(C["s"])),
            (re.compile(r"`[^`]*`"),             f(C["s"])),
        ]
        # numbers
        self._rules.append((re.compile(r"\b\d+\.?\d*\b"), f(C["n"])))
        # function calls
        self._rules.append((re.compile(r"\b([A-Za-z_]\w*)\s*(?=\()"), f(C["fn"])))

        if lang == "html":
            self._rules.append((re.compile(r"</?[A-Za-z][A-Za-z0-9-]*"), f(C["tag"])))
            self._rules.append((re.compile(r"<!--.*?-->"),                 f(C["c"], italic=True)))
        elif lang == "python":
            self._rules.append((re.compile(r"#[^\n]*"), f(C["c"], italic=True)))
        elif lang in ("js", "css", "json"):
            self._rules.append((re.compile(r"//[^\n]*"), f(C["c"], italic=True)))
        elif lang == "shell":
            self._rules.append((re.compile(r"#[^\n]*"), f(C["c"], italic=True)))
        elif lang == "markdown":
            self._rules.append((re.compile(r"^#{1,6}.*", re.MULTILINE), f(C["kw"], bold=True)))

    def highlightBlock(self, text: str):
        for pat, fmt in self._rules:
            for m in pat.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# ── background file loader ────────────────────────────────────

class _FileLoader(QThread):
    result_ready = pyqtSignal(dict)
    _MAX_LINES = 200

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._path = path

    def run(self):
        path = self._path
        p = Path(path)
        out = {"path": path, "error": None}
        try:
            st = p.stat()
            out.update(
                name=p.name,
                ext=p.suffix.lower(),
                size=st.st_size,
                mtime=st.st_mtime,
                ctime=st.st_ctime,
                ftype=_file_type(path),
            )
            ftype = out["ftype"]
            if ftype == "image":
                self._image(path, out)
            elif ftype == "pdf":
                self._pdf(path, out)
            elif ftype in ("text", "code"):
                self._text(path, out)
            elif ftype == "video":
                self._video(path, out)
            elif ftype == "audio":
                self._audio(path, out)
        except Exception as e:
            out["error"] = str(e)
        self.result_ready.emit(out)

    @staticmethod
    def _image(path, out):
        px = QPixmap(path)
        if px.isNull():
            out["error"] = "No se pudo cargar la imagen"
        else:
            out["pixmap"] = px
            out["img_w"]  = px.width()
            out["img_h"]  = px.height()

    @staticmethod
    def _pdf(path, out):
        try:
            import fitz
            doc = fitz.open(path)
            out["page_count"] = len(doc)
            pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            px = QPixmap()
            px.loadFromData(pix.tobytes("png"))
            doc.close()
            out["pixmap"] = px
        except ImportError:
            out["error"] = "Instala PyMuPDF para vista previa PDF:\n pip install pymupdf"
        except Exception as e:
            out["error"] = str(e)

    def _text(self, path, out):
        try:
            lines = []
            total = 0
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    total += 1
                    if total <= self._MAX_LINES:
                        lines.append(line)
            out["lines"]      = lines
            out["line_count"] = total
            out["word_count"] = sum(len(l.split()) for l in lines)
            out["lang"]       = _lang(path)
        except Exception as e:
            out["error"] = str(e)

    @staticmethod
    def _video(path, out):
        try:
            import cv2
            cap   = cv2.VideoCapture(path)
            fps   = cap.get(cv2.CAP_PROP_FPS) or 1
            total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            out["vid_w"]    = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            out["vid_h"]    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out["duration"] = total / fps
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(total * 0.1)))
            ok, frame = cap.read()
            cap.release()
            if ok:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                from PyQt5.QtGui import QImage
                h, w, ch = rgb.shape
                qi = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                out["thumb"] = QPixmap.fromImage(qi)
        except ImportError:
            pass
        except Exception:
            pass

    @staticmethod
    def _audio(path, out):
        try:
            from mutagen import File as MFile
            mf = MFile(path)
            if mf and hasattr(mf.info, "length"):
                out["duration"] = mf.info.length
        except ImportError:
            pass
        except Exception:
            pass


# ── minimal media player ──────────────────────────────────────

class _MediaWidget(QWidget):
    def __init__(self, path: str, is_video: bool, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)
        self._player = None
        try:
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
            from PyQt5.QtCore import QUrl
            self._player = QMediaPlayer(self)
            self._player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            if is_video:
                try:
                    from PyQt5.QtMultimediaWidgets import QVideoWidget
                    vw = QVideoWidget()
                    vw.setMinimumHeight(130)
                    self._player.setVideoOutput(vw)
                    layout.addWidget(vw)
                except ImportError:
                    pass
            ctrl = QHBoxLayout()
            self._play_btn = QPushButton("▶")
            self._play_btn.setFixedSize(30, 26)
            self._play_btn.setStyleSheet(_BTN)
            self._play_btn.clicked.connect(self._toggle)
            stop_btn = QPushButton("⏹")
            stop_btn.setFixedSize(30, 26)
            stop_btn.setStyleSheet(_BTN)
            stop_btn.clicked.connect(lambda: self._player.stop())
            self._time_lbl = QLabel("0:00")
            self._time_lbl.setStyleSheet(f"color:{_T['text_dim']};font-size:11px;")
            ctrl.addWidget(self._play_btn)
            ctrl.addWidget(stop_btn)
            ctrl.addWidget(self._time_lbl)
            ctrl.addStretch()
            layout.addLayout(ctrl)
            self._player.positionChanged.connect(self._on_pos)
            self._player.stateChanged.connect(self._on_state)
        except ImportError:
            lbl = QLabel("QtMultimedia no disponible")
            lbl.setStyleSheet(f"color:{_T['text_dim']};font-size:11px;")
            layout.addWidget(lbl)

    def _toggle(self):
        from PyQt5.QtMultimedia import QMediaPlayer
        if self._player.state() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _on_pos(self, ms: int):
        s = ms // 1000
        self._time_lbl.setText(f"{s//60}:{s%60:02d}")

    def _on_state(self, state):
        from PyQt5.QtMultimedia import QMediaPlayer
        self._play_btn.setText("⏸" if state == QMediaPlayer.PlayingState else "▶")

    def stop(self):
        if self._player:
            try:
                self._player.stop()
            except Exception:
                pass


# ── theme constants ───────────────────────────────────────────

_T = {
    "bg":       "#1e1e2e",
    "sidebar":  "#181825",
    "panel":    "#24243e",
    "accent":   "#cba6f7",
    "accent2":  "#89b4fa",
    "text":     "#cdd6f4",
    "text_dim": "#6c7086",
    "hover":    "#313244",
    "border":   "#313244",
}

_BTN = f"""
QPushButton {{
    background:{_T['hover']}; color:{_T['text']};
    border:none; border-radius:5px;
    font-size:12px; padding:3px 8px;
}}
QPushButton:hover {{ background:{_T['accent']}; color:{_T['bg']}; }}
QPushButton:pressed {{ background:{_T['accent2']}; }}
"""

_BTN_PIN_ON = f"""
QPushButton {{
    background:{_T['accent']}; color:{_T['bg']};
    border:none; border-radius:5px;
    font-size:12px; padding:3px 8px; font-weight:bold;
}}
"""


# ── main panel ────────────────────────────────────────────────

class PreviewPanel(QWidget):
    request_search   = pyqtSignal(str)
    request_trace    = pyqtSignal(str)
    request_favorite = pyqtSignal(str)
    request_location = pyqtSignal(str)

    # QStackedWidget indices
    _EMPTY = 0; _IMAGE = 1; _TEXT = 2; _PDF = 3; _MEDIA = 4; _UNKNOWN = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(240)
        self.setMaximumWidth(440)
        self._pinned     = False
        self._current    = None
        self._loader     = None
        self._media_w    = None
        self._hl         = None   # syntax highlighter (keeps reference so GC doesn't kill it)
        self._build_ui()

    # ── build ui ─────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet(
            f"background:{_T['sidebar']}; border-left:1px solid {_T['border']};"
        )
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        # ── scrollable body ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent;")

        body = QWidget()
        body.setStyleSheet("background:transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(12, 8, 12, 8)
        bl.setSpacing(6)

        # file icon + name
        nr = QHBoxLayout()
        self._icon = QLabel("📄")
        self._icon.setStyleSheet("font-size:22px;")
        self._icon.setFixedWidth(30)
        self._name = QLabel("Sin selección")
        self._name.setStyleSheet(f"color:{_T['text']};font-size:13px;font-weight:bold;")
        self._name.setWordWrap(True)
        nr.addWidget(self._icon)
        nr.addWidget(self._name, 1)
        bl.addLayout(nr)
        bl.addWidget(self._sep())

        # loading bar
        self._bar = QProgressBar()
        self._bar.setRange(0, 0)
        self._bar.setFixedHeight(3)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(
            f"QProgressBar{{background:{_T['border']};border-radius:2px;border:none;}}"
            f"QProgressBar::chunk{{background:{_T['accent']};border-radius:2px;}}"
        )
        self._bar.hide()
        bl.addWidget(self._bar)

        # stacked content
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background:transparent;")

        # 0 empty
        ep = QLabel("Selecciona un archivo\npara ver su vista previa")
        ep.setAlignment(Qt.AlignCenter)
        ep.setStyleSheet(f"color:{_T['text_dim']};font-size:12px;")
        ep.setMinimumHeight(120)
        self._stack.addWidget(ep)

        # 1 image
        self._img_lbl = QLabel()
        self._img_lbl.setAlignment(Qt.AlignCenter)
        self._img_lbl.setStyleSheet("background:transparent;")
        self._stack.addWidget(self._img_lbl)

        # 2 text / code
        self._txt = QTextEdit()
        self._txt.setReadOnly(True)
        self._txt.setMinimumHeight(160)
        self._txt.setMaximumHeight(280)
        self._txt.setFont(QFont("Consolas", 10))
        self._txt.setStyleSheet(
            f"QTextEdit{{background:{_T['panel']};color:{_T['text']};"
            f"border:1px solid {_T['border']};border-radius:6px;padding:6px;}}"
        )
        self._stack.addWidget(self._txt)

        # 3 pdf
        self._pdf_lbl = QLabel()
        self._pdf_lbl.setAlignment(Qt.AlignCenter)
        self._pdf_lbl.setStyleSheet("background:transparent;")
        self._stack.addWidget(self._pdf_lbl)

        # 4 media (replaced dynamically)
        self._media_slot = QLabel()
        self._stack.addWidget(self._media_slot)

        # 5 unknown / error
        self._unk_lbl = QLabel()
        self._unk_lbl.setAlignment(Qt.AlignCenter)
        self._unk_lbl.setWordWrap(True)
        self._unk_lbl.setStyleSheet(f"color:{_T['text_dim']};font-size:11px;")
        self._stack.addWidget(self._unk_lbl)

        bl.addWidget(self._stack)
        bl.addWidget(self._sep())

        # metadata
        bl.addWidget(self._make_meta())
        bl.addStretch()

        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        root.addWidget(self._sep())
        root.addWidget(self._make_actions())

    def _make_header(self) -> QWidget:
        h = QWidget()
        h.setFixedHeight(36)
        h.setStyleSheet(f"background:{_T['panel']};border-bottom:1px solid {_T['border']};")
        lay = QHBoxLayout(h)
        lay.setContentsMargins(10, 4, 10, 4)

        title = QLabel("Vista Previa")
        title.setStyleSheet(
            f"color:{_T['accent']};font-size:12px;font-weight:bold;letter-spacing:0.5px;"
        )
        lay.addWidget(title)
        lay.addStretch()

        self._pin_btn = QPushButton("📌")
        self._pin_btn.setFixedSize(26, 26)
        self._pin_btn.setCheckable(True)
        self._pin_btn.setToolTip("Fijar vista previa")
        self._pin_btn.setStyleSheet(_BTN)
        self._pin_btn.clicked.connect(self._toggle_pin)
        lay.addWidget(self._pin_btn)

        hide = QPushButton("✕")
        hide.setFixedSize(26, 26)
        hide.setToolTip("Ocultar panel")
        hide.setStyleSheet(_BTN)
        hide.clicked.connect(self.hide)
        lay.addWidget(hide)
        return h

    def _make_meta(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        lbl = QLabel("INFORMACIÓN")
        lbl.setStyleSheet(
            f"color:{_T['text_dim']};font-size:10px;font-weight:bold;letter-spacing:1px;"
        )
        lay.addWidget(lbl)

        self._m_path  = self._meta_row(lay, "Ruta:")
        self._m_ctime = self._meta_row(lay, "Creado:")
        self._m_mtime = self._meta_row(lay, "Modificado:")
        self._m_size  = self._meta_row(lay, "Tamaño:")
        self._m_opens = self._meta_row(lay, "Abierto:")
        self._m_extra = self._meta_row(lay, "Detalle:")
        return w

    @staticmethod
    def _meta_row(parent_lay: QVBoxLayout, label: str) -> QLabel:
        row = QHBoxLayout()
        row.setSpacing(4)
        key = QLabel(label)
        key.setFixedWidth(72)
        key.setStyleSheet(f"color:{_T['text_dim']};font-size:11px;")
        val = QLabel("—")
        val.setWordWrap(True)
        val.setStyleSheet(f"color:{_T['text']};font-size:11px;")
        row.addWidget(key)
        row.addWidget(val, 1)
        parent_lay.addLayout(row)
        return val

    def _make_actions(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet(f"background:{_T['panel']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(6)
        for icon, tip, slot in (
            ("🔍", "Superbúsqueda inteligente", self._do_search),
            ("📍", "Rastrear uso del archivo",  self._do_trace),
            ("⭐", "Agregar a favoritos",        self._do_favorite),
            ("📂", "Abrir ubicación",            self._do_location),
        ):
            b = QPushButton(icon)
            b.setFixedSize(30, 28)
            b.setToolTip(tip)
            b.setStyleSheet(_BTN)
            b.clicked.connect(slot)
            lay.addWidget(b)
        lay.addStretch()
        return bar

    @staticmethod
    def _sep() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet(f"background:{_T['border']};max-height:1px;margin:2px 0;")
        return f

    # ── pin / action slots ────────────────────────────────────

    def _toggle_pin(self, checked: bool):
        self._pinned = checked
        self._pin_btn.setStyleSheet(_BTN_PIN_ON if checked else _BTN)
        self._pin_btn.setToolTip(
            "Fijado — la vista no se actualiza" if checked else "Fijar vista previa"
        )

    def _do_search(self):
        if self._current: self.request_search.emit(self._current)

    def _do_trace(self):
        if self._current: self.request_trace.emit(self._current)

    def _do_favorite(self):
        if self._current: self.request_favorite.emit(self._current)

    def _do_location(self):
        if self._current:
            self.request_location.emit(str(Path(self._current).parent))

    # ── public API ────────────────────────────────────────────

    def set_file(self, path: str):
        if self._pinned or path == self._current:
            return
        self._current = path
        increment_open_count(path)
        self._stop_media()
        self._hl = None
        self._bar.show()
        self._stack.setCurrentIndex(self._EMPTY)

        if self._loader and self._loader.isRunning():
            self._loader.result_ready.disconnect()
            self._loader.quit()

        self._loader = _FileLoader(path, parent=self)
        self._loader.result_ready.connect(self._on_result)
        self._loader.finished.connect(self._bar.hide)
        self._loader.start()

    def clear(self):
        self._current = None
        self._stop_media()
        self._stack.setCurrentIndex(self._EMPTY)
        self._name.setText("Sin selección")
        self._icon.setText("📄")

    # ── result handler ────────────────────────────────────────

    def _on_result(self, d: dict):
        if d["path"] != self._current:
            return

        _icons = {"image": "🖼", "video": "🎬", "audio": "🎵",
                  "pdf": "📕", "code": "💻", "text": "📄"}
        ftype = d.get("ftype", "unknown")
        self._icon.setText(_icons.get(ftype, "📄"))
        self._name.setText(d.get("name", Path(d["path"]).name))

        self._m_path.setText(d["path"])
        self._m_path.setToolTip(d["path"])
        if "ctime" in d: self._m_ctime.setText(_fmt_ts(d["ctime"]))
        if "mtime" in d: self._m_mtime.setText(_fmt_ts(d["mtime"]))
        if "size"  in d: self._m_size.setText(_fmt_size(d["size"]))
        self._m_opens.setText(f"{get_open_count(d['path'])} veces")

        if d.get("error"):
            self._unk_lbl.setText(d["error"])
            self._stack.setCurrentIndex(self._UNKNOWN)
            return

        if ftype == "image":   self._render_image(d)
        elif ftype == "pdf":   self._render_pdf(d)
        elif ftype in ("text", "code"): self._render_text(d)
        elif ftype == "video": self._render_video(d)
        elif ftype == "audio": self._render_audio(d)
        else:
            self._unk_lbl.setText(f"Sin vista previa\n{d.get('ext','').upper()}")
            self._stack.setCurrentIndex(self._UNKNOWN)

    # ── renderers ─────────────────────────────────────────────

    def _render_image(self, d: dict):
        px: QPixmap = d["pixmap"]
        max_w = max(self.width() - 28, 100)
        if px.width() > max_w:
            px = px.scaledToWidth(max_w, Qt.SmoothTransformation)
        self._img_lbl.setPixmap(px)
        ext = d.get("ext", "").upper().lstrip(".")
        self._m_extra.setText(
            f"{d.get('img_w',0)}×{d.get('img_h',0)} px · {ext}"
        )
        self._stack.setCurrentIndex(self._IMAGE)

    def _render_pdf(self, d: dict):
        px: QPixmap = d.get("pixmap")
        if px:
            max_w = max(self.width() - 28, 100)
            if px.width() > max_w:
                px = px.scaledToWidth(max_w, Qt.SmoothTransformation)
            self._pdf_lbl.setPixmap(px)
        else:
            self._pdf_lbl.setText(d.get("error", "Error"))
        self._m_extra.setText(f"{d.get('page_count','?')} páginas")
        self._stack.setCurrentIndex(self._PDF)

    def _render_text(self, d: dict):
        self._txt.setPlainText("".join(d.get("lines", [])))
        lang = d.get("lang", "generic")
        self._hl = _Highlighter(self._txt.document(), lang)
        lines = d.get("line_count", 0)
        words = d.get("word_count", 0)
        self._m_extra.setText(f"{lines} líneas · {words} palabras · {lang}")
        self._stack.setCurrentIndex(self._TEXT)

    def _render_video(self, d: dict):
        self._replace_media(d["path"], is_video=True)
        parts = []
        if "duration" in d:
            dur = int(d["duration"])
            parts.append(f"{dur//60}:{dur%60:02d}")
        if d.get("vid_w"):
            parts.append(f"{d['vid_w']}×{d['vid_h']}")
        self._m_extra.setText(" · ".join(parts) if parts else "—")
        self._stack.setCurrentIndex(self._MEDIA)

    def _render_audio(self, d: dict):
        self._replace_media(d["path"], is_video=False)
        ext = d.get("ext", "").upper().lstrip(".")
        parts = [ext]
        if "duration" in d:
            dur = int(d["duration"])
            parts.append(f"{dur//60}:{dur%60:02d}")
        self._m_extra.setText(" · ".join(parts))
        self._stack.setCurrentIndex(self._MEDIA)

    # ── media helpers ─────────────────────────────────────────

    def _replace_media(self, path: str, is_video: bool):
        self._stop_media()
        self._media_w = _MediaWidget(path, is_video=is_video, parent=self)
        old = self._stack.widget(self._MEDIA)
        self._stack.removeWidget(old)
        old.deleteLater()
        self._stack.insertWidget(self._MEDIA, self._media_w)

    def _stop_media(self):
        if self._media_w:
            try:
                self._media_w.stop()
            except Exception:
                pass
            self._media_w = None
