"""
Cargador y tintador de íconos PNG de la carpeta assets/icons/.
Uso:  from ui.icons import icon, tinted_icon
"""
from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt5.QtCore import Qt, QSize

_DIR = Path(__file__).parent.parent / "assets" / "icons"


def _load(name: str) -> QPixmap:
    path = _DIR / f"{name}.png"
    if path.exists():
        return QPixmap(str(path))
    return QPixmap()


def icon(name: str) -> QIcon:
    """Ícono sin tintar (usa el color original del PNG)."""
    px = _load(name)
    return QIcon(px) if not px.isNull() else QIcon()


def tinted_icon(name: str, color: str) -> QIcon:
    """Ícono re-coloreado: preserva el canal alpha, aplica `color` como tinte."""
    px = _load(name)
    if px.isNull():
        return QIcon()
    result = QPixmap(px.size())
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.drawPixmap(0, 0, px)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), QColor(color))
    painter.end()
    return QIcon(result)


def app_icon() -> QIcon:
    return icon("logo")
