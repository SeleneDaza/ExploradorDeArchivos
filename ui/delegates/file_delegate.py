"""
Delegado visual que superpone color e insignia sobre cada ítem
del QListView sin reemplazar el ícono del sistema de archivos.
"""
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRect

from core.personalizer import Personalizer, COLORS, BADGES, _BADGE_COLORS


class FileItemDelegate(QStyledItemDelegate):
    def __init__(self, source_model, parent=None):
        super().__init__(parent)
        self._p          = Personalizer()
        self._src        = source_model   # QFileSystemModel original
        self._filter_color: str | None = None

    # ── filtro activo ─────────────────────────────────────────

    def set_filter(self, color_key: str | None):
        self._filter_color = color_key

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
