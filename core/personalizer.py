"""
Motor de personalización visual: colores y distintivos por ruta.
Persiste en ~/.explorador_cache/personalizations.json
"""
import json
from pathlib import Path

# Path.home() equivale a "echo $HOME" en Linux
# obtiene la carpeta del usuario para guardar la configuración
_CACHE_DIR = Path.home() / ".explorador_cache"
_FILE      = _CACHE_DIR / "personalizations.json"

# ── paleta de colores ─────────────────────────────────────────
COLORS: dict[str, tuple[str, str]] = {
    "red":    ("#e05252", "Rojo · Prioridad alta"),
    "orange": ("#e08520", "Naranja · Atención"),
    "yellow": ("#c9a800", "Amarillo · Pendiente"),
    "green":  ("#3aaa6e", "Verde · Completado"),
    "blue":   ("#4a8fe8", "Azul · Trabajo"),
    "purple": ("#8b5cf6", "Morado · Personal"),
    "pink":   ("#d85fa0", "Rosa"),
    "gray":   ("#7a8394", "Gris"),
}

# ── insignias ─────────────────────────────────────────────────
BADGES: dict[str, tuple[str, str]] = {
    "star":      ("★", "Favorito"),
    "important": ("◆", "Importante"),
    "private":   ("●", "Privado"),
    "progress":  ("◐", "En progreso"),
    "done":      ("✓", "Finalizado"),
}

_BADGE_COLORS: dict[str, str] = {
    "star":      "#c9a800",
    "important": "#e05252",
    "private":   "#7a8394",
    "progress":  "#4a8fe8",
    "done":      "#3aaa6e",
}


class Personalizer:
    """Singleton — un único gestor de personalizaciones por proceso."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._data: dict[str, dict] = {}
            inst._load()
            cls._instance = inst
        return cls._instance

    # ── persistencia ─────────────────────────────────────────

    def _load(self):
        try:
             # _FILE.exists() verifica si el archivo de configuración ya existe
            if _FILE.exists():
                # _FILE.read_text() lee el contenido del archivo JSON
                self._data = json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            self._data = {}

    def _save(self):
        try:
            # _CACHE_DIR.mkdir() equivale a "mkdir -p carpeta" en Linux
            # crea la carpeta de caché si no existe
            _CACHE_DIR.mkdir(parents=True, exist_ok=True)
            # _FILE.write_text() escribe/guarda el archivo JSON en disco
            _FILE.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ── lectura ───────────────────────────────────────────────

    def get(self, path: str) -> dict:
        return self._data.get(str(path), {})

    def has_any(self, path: str) -> bool:
        return bool(self._data.get(str(path)))

    def all_personalized(self) -> list[tuple[str, dict]]:
        return [(p, d.copy()) for p, d in self._data.items() if d]

    # ── escritura ─────────────────────────────────────────────

    def set_color(self, path: str, color_key: str | None):
        entry = self._data.setdefault(str(path), {})
        if color_key:
            entry["color"] = color_key
        else:
            entry.pop("color", None)
        if not entry:
            self._data.pop(str(path), None)
        self._save()

    def set_badge(self, path: str, badge_key: str | None):
        entry = self._data.setdefault(str(path), {})
        if badge_key:
            entry["badge"] = badge_key
        else:
            entry.pop("badge", None)
        if not entry:
            self._data.pop(str(path), None)
        self._save()

    def clear(self, path: str):
        self._data.pop(str(path), None)
        self._save()

    def move_path(self, old_path: str, new_path: str):
        """Actualiza la clave cuando el archivo se mueve dentro del explorador."""
        key = str(old_path)
        if key in self._data:
            self._data[str(new_path)] = self._data.pop(key)
            self._save()
