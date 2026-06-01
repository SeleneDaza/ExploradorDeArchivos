"""
Delegado visual que superpone color e insignia sobre cada ítem
del QListView sin reemplazar el ícono del sistema de archivos.
"""
from PyQt5.QtWidgets import QStyledItemDelegate, QToolTip, QStyle
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRect, QEvent

from core.personalizer import Personalizer, COLORS, BADGES, _BADGE_COLORS

# ── heat map ──────────────────────────────────────────────────

_HEAT = [
    (0.00, (100, 210, 120)),
    (0.40, (230, 215,  75)),
    (0.70, (240, 148,  54)),
    (1.00, (228,  82,  82)),
]


def _heat_color(t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    for i in range(len(_HEAT) - 1):
        t0, c0 = _HEAT[i]
        t1, c1 = _HEAT[i + 1]
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return QColor(
                int(c0[0] + f * (c1[0] - c0[0])),
                int(c0[1] + f * (c1[1] - c0[1])),
                int(c0[2] + f * (c1[2] - c0[2])),
            )
    return QColor(*_HEAT[-1][1])


def _fmt_size(b: int) -> str:
    if b < 1024:       return f"{b} B"
    b /= 1024
    if b < 1024:       return f"{b:.1f} KB"
    b /= 1024
    if b < 1024:       return f"{b:.1f} MB"
    b /= 1024
    if b < 1024:       return f"{b:.2f} GB"
    return f"{b / 1024:.2f} TB"


class FileItemDelegate(QStyledItemDelegate):
    def __init__(self, source_model, parent=None):
        super().__init__(parent)
        self._p          = Personalizer()
        self._src        = source_model   # QFileSystemModel original
        self._filter_color: str | None = None
        self._min_size: int = 0
        self._max_size: int = 0

    # ── filtro activo ─────────────────────────────────────────

    def set_filter(self, color_key: str | None):
        self._filter_color = color_key

    # ── heat map: rango de tamaños ────────────────────────────

    def set_size_range(self, min_size: int, max_size: int):
        self._min_size = min_size
        self._max_size = max_size

    def _size_bytes(self, index) -> int:
        try:
            col0 = index.sibling(index.row(), 0)
            m = index.model()
            if hasattr(m, "fileInfo"):
                info = m.fileInfo(col0)
            elif hasattr(m, "mapToSource"):
                info = self._src.fileInfo(m.mapToSource(col0))
            else:
                return -1
            return info.size() if info.isFile() else -1
        except Exception:
            return -1

    # ── path desde índice (soporta proxy) ─────────────────────

    def _path(self, index) -> str:
        try:
            m = index.model()
            if hasattr(m, "filePath"):
                return m.filePath(index)
            if hasattr(m, "mapToSource"):
                return self._src.filePath(m.mapToSource(index))
        except Exception:
            pass
        return ""

    # ── paint principal ───────────────────────────────────────

    def paint(self, painter: QPainter, option, index):
        if index.column() == 1:
            self._paint_size_cell(painter, option, index)
            return

        # solo dibujar indicadores en la columna del nombre
        if index.column() != 0:
            super().paint(painter, option, index)
            return

        path   = self._path(index)
        p_data = self._p.get(path) if path else {}

        # Filtro de color activo → difuminar no-coincidentes
        if self._filter_color:
            if p_data.get("color") != self._filter_color:
                painter.save()
                painter.setOpacity(0.25)
                super().paint(painter, option, index)
                painter.restore()
                return

        super().paint(painter, option, index)

        if not p_data:
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect       = option.rect
        icon_mode  = rect.height() > 50

        color_key = p_data.get("color")
        badge_key = p_data.get("badge")

        if icon_mode:
            self._draw_icon_mode(painter, rect, color_key, badge_key)
        else:
            self._draw_list_mode(painter, rect, color_key, badge_key)

        painter.restore()

    # ── vista lista ───────────────────────────────────────────

    def _draw_list_mode(self, painter, rect: QRect,
                        color_key: str | None, badge_key: str | None):
        # Banda de color: franja izquierda de 3 px
        if color_key and color_key in COLORS:
            hex_c, _ = COLORS[color_key]
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(hex_c))
            stripe = QRect(rect.left(), rect.top() + 3, 3, rect.height() - 6)
            painter.drawRoundedRect(stripe, 1, 1)

        # Insignia: círculo pequeño lado derecho
        if badge_key and badge_key in BADGES:
            sym, _ = BADGES[badge_key]
            r  = 10
            cx = rect.right() - r - 5
            cy = rect.center().y()
            col = _BADGE_COLORS.get(badge_key, "#7a8394")

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(col))
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

            f = QFont()
            f.setPointSize(7)
            f.setBold(True)
            painter.setFont(f)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(QRect(cx - r, cy - r, r * 2, r * 2),
                             Qt.AlignCenter, sym)

    # ── heat map: celda de tamaño ────────────────────────────

    def _paint_size_cell(self, painter: QPainter, option, index):
        size_b = self._size_bytes(index)
        selected = bool(option.state & QStyle.State_Selected)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = option.rect

        if selected:
            painter.fillRect(rect, option.palette.highlight())

        if size_b >= 0:
            if self._max_size > self._min_size:
                t = (size_b - self._min_size) / (self._max_size - self._min_size)
            else:
                t = 0.0
            color = _heat_color(t)
            # más translúcido y estilo 'pill' alrededor del texto
            color.setAlpha(100 if selected else 140)
            painter.setPen(Qt.NoPen)

            # texto (usa el texto ya formateado si existe)
            text = index.data(Qt.DisplayRole) or _fmt_size(size_b)
            f = QFont(option.font)
            f.setPointSize(max(8, f.pointSize()))
            painter.setFont(f)
            fm = painter.fontMetrics()
            pad_x = 10
            pad_y = 4
            tw = fm.horizontalAdvance(text)
            th = fm.height()

            badge_w = tw + pad_x * 2
            badge_h = th + pad_y
            bx = rect.center().x() - badge_w // 2
            by = rect.center().y() - badge_h // 2
            badge = QRect(bx, by, badge_w, badge_h)

            # fondo semi-transparente redondeado
            painter.setBrush(color)
            painter.drawRoundedRect(badge, badge_h // 2, badge_h // 2)

            # borde sutil (oscurecer ligeramente el color)
            edge = QColor(color)
            edge.setAlpha(80)
            pen = QPen(edge, 1)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(badge.adjusted(0, 0, -1, -1), badge_h // 2, badge_h // 2)

        # dibujar texto centrado en la pill si hay tamaño, sino text normal
        if size_b >= 0:
            # contraste del texto según luminancia del color
            r, g, b, _a = color.red(), color.green(), color.blue(), color.alpha()
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            text_col = option.palette.highlightedText().color() if selected else (
                QColor("#1a1a2e") if lum > 180 else QColor("#ffffff")
            )
            painter.setPen(text_col)
            painter.drawText(badge, Qt.AlignCenter, text)
        else:
            text = index.data(Qt.DisplayRole) or ""
            painter.setPen(QColor("#707090"))
            f = QFont(option.font)
            f.setPointSize(max(8, f.pointSize()))
            painter.setFont(f)
            painter.drawText(rect, Qt.AlignCenter, text)
        painter.restore()

    def helpEvent(self, event, view, option, index):
        if index.column() == 1 and event.type() == QEvent.ToolTip:
            size_b = self._size_bytes(index)
            if size_b >= 0 and self._max_size > 0:
                pct = int(size_b / self._max_size * 100)
                QToolTip.showText(
                    event.globalPos(),
                    f"Tamaño: {_fmt_size(size_b)}\n{pct}% del máximo de esta carpeta",
                    view,
                )
                return True
        return super().helpEvent(event, view, option, index)

    # ── vista iconos ──────────────────────────────────────────

    def _draw_icon_mode(self, painter, rect: QRect,
                        color_key: str | None, badge_key: str | None):
        # El ícono ocupa aprox. el 65 % superior de la celda
        icon_h = int(rect.height() * 0.63)
        cx = rect.center().x()

        # Punto de color: esquina inferior izquierda del ícono
        if color_key and color_key in COLORS:
            hex_c, _ = COLORS[color_key]
            r  = 6
            bx = cx - 28
            by = rect.top() + icon_h - r * 2 - 2
            painter.setPen(QPen(QColor("#00000033"), 1))
            painter.setBrush(QColor(hex_c))
            painter.drawEllipse(bx, by, r * 2, r * 2)

        # Insignia: esquina inferior derecha del ícono
        if badge_key and badge_key in BADGES:
            sym, _ = BADGES[badge_key]
            r  = 8
            bx = cx + 16
            by = rect.top() + icon_h - r * 2 - 2
            col = _BADGE_COLORS.get(badge_key, "#7a8394")

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(col))
            painter.drawEllipse(bx, by, r * 2, r * 2)

            f = QFont()
            f.setPointSize(6)
            f.setBold(True)
            painter.setFont(f)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(QRect(bx, by, r * 2, r * 2), Qt.AlignCenter, sym)
