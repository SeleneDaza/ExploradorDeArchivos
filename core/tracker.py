import os
import hashlib
import time
import pickle
from pathlib import Path
from typing import List, Dict, Optional
import fnmatch
import re

# Simple in-memory cache: key -> (timestamp, result)
_cache = {}
CACHE_TTL = 60 * 5  # 5 minutes

# disk cache
CACHE_DIR = Path.home() / ".explorador_cache"
CACHE_FILE = CACHE_DIR / "tracker_cache.pickle"
SETTINGS_FILE = CACHE_DIR / "settings.json"
SETTINGS = {}


def _load_settings():
    global SETTINGS
    try:
        if SETTINGS_FILE.exists():
            import json
            with SETTINGS_FILE.open('r', encoding='utf-8') as f:
                SETTINGS = json.load(f)
        else:
            SETTINGS = {}
    except Exception:
        SETTINGS = {}


def save_settings(new: dict):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        import json
        with SETTINGS_FILE.open('w', encoding='utf-8') as f:
            json.dump(new, f, indent=2, ensure_ascii=False)
        _load_settings()
    except Exception:
        pass


def get_settings() -> dict:
    return dict(SETTINGS)


# load settings on import
_load_settings()


def _load_cache():
    global _cache
    try:
        if CACHE_FILE.exists():
            with CACHE_FILE.open("rb") as f:
                _cache = pickle.load(f)
    except Exception:
        _cache = {}


def _save_cache():
    try:
        # only persist if settings allow it (default True)
        persist = SETTINGS.get('persist_cache', True) if isinstance(SETTINGS, dict) else True
        if persist:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with CACHE_FILE.open("wb") as f:
                pickle.dump(_cache, f)
    except Exception:
        pass


# load persisted cache on import
_load_cache()


def _file_info(path: Path) -> Dict:
    st = path.stat()
    return {
        "path": str(path),
        "size": st.st_size,
        "mtime": st.st_mtime,
    }


def compute_hash(path: str, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    p = Path(path)
    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(target_path: str, roots: Optional[List[str]] = None,
                    exclude_dirs: Optional[List[str]] = None,
                    exclude_file_patterns: Optional[List[str]] = None) -> List[Dict]:
    target = Path(target_path)
    if not target.exists() or not target.is_file():
        return []

    exclude_dirs = exclude_dirs or []
    exclude_file_patterns = exclude_file_patterns or []

    key = ("dup", str(target.resolve()), tuple(sorted(roots or [])), tuple(sorted(exclude_dirs)), tuple(sorted(exclude_file_patterns)))
    now = time.time()
    if key in _cache:
        ts, val = _cache[key]
        if now - ts < CACHE_TTL:
            return val

    target_size = target.stat().st_size
    target_hash = compute_hash(str(target))

    if roots is None:
        # default to user's home folder
        roots = [str(Path.home())]

    results = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            # prune dirnames according to exclude_dirs patterns/names
            dirnames[:] = [d for d in dirnames if not any(d == ex or fnmatch.fnmatch(d, ex) for ex in exclude_dirs)]
            for fname in filenames:
                try:
                    # skip file patterns
                    if any(fnmatch.fnmatch(fname, pat) for pat in exclude_file_patterns):
                        continue
                    fpath = Path(dirpath) / fname
                    # skip the same file
                    if fpath.resolve() == target.resolve():
                        continue
                    if not fpath.is_file():
                        continue
                    if fpath.stat().st_size != target_size:
                        continue
                    # compute hash
                    try:
                        h = compute_hash(str(fpath))
                    except Exception:
                        continue
                    if h == target_hash:
                        results.append(_file_info(fpath))
                except Exception:
                    continue

    # include target as original at top
    final = [
        {
            "path": str(target),
            "size": target_size,
            "mtime": target.stat().st_mtime,
            "is_original": True,
        }
    ]
    for r in results:
        r["is_original"] = False
        final.append(r)

    _cache[key] = (now, final)
    _save_cache()
    return final


def is_text_file(path: str) -> bool:
    # rudimentary check: try opening as text
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read(1024)
        return True
    except Exception:
        return False


def _resolve_reference_path(ref: str, base_dir: Path, roots: List[str]) -> Optional[Path]:
    # clean ref
    ref = ref.strip().strip('"\'')
    if not ref:
        return None
    p = Path(ref)
    # absolute-like (starts with /): try under each root
    if ref.startswith('/'):
        for r in roots:
            candidate = Path(r) / ref.lstrip('/')
            if candidate.exists():
                return candidate.resolve()
        return None
    # relative path
    candidate = (base_dir / ref).resolve()
    if candidate.exists():
        return candidate
    # try joining and normalizing (remove query strings or anchors)
    clean = ref.split('?')[0].split('#')[0]
    candidate = (base_dir / clean).resolve()
    if candidate.exists():
        return candidate
    return None


def _parse_html_for_refs(fpath: Path, target: Path, roots: List[str]):
    results = []
    try:
        with fpath.open('r', encoding='utf-8', errors='ignore') as fh:
            for i, line in enumerate(fh, start=1):
                # find src/href attributes
                for m in re.findall(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', line, flags=re.IGNORECASE):
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
                        break
                # also check <img srcset=> (comma separated)
                for m in re.findall(r'srcset\s*=\s*["\']([^"\']+)["\']', line, flags=re.IGNORECASE):
                    parts = [p.split()[0] for p in m.split(',') if p.strip()]
                    for part in parts:
                        resolved = _resolve_reference_path(part, fpath.parent, roots)
                        if resolved and resolved == target:
                            results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
                            break
    except Exception:
        pass
    return results


def _parse_css_for_refs(fpath: Path, target: Path, roots: List[str]):
    results = []
    try:
        with fpath.open('r', encoding='utf-8', errors='ignore') as fh:
            for i, line in enumerate(fh, start=1):
                for m in re.findall(r'url\(([^)]+)\)', line, flags=re.IGNORECASE):
                    m = m.strip().strip('"\'')
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
                for m in re.findall(r'@import\s+["\']([^"\']+)["\']', line, flags=re.IGNORECASE):
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
    except Exception:
        pass
    return results


def _parse_js_for_refs(fpath: Path, target: Path, roots: List[str]):
    results = []
    try:
        with fpath.open('r', encoding='utf-8', errors='ignore') as fh:
            for i, line in enumerate(fh, start=1):
                # import ... from '...'
                for m in re.findall(r'import[^;]*from\s+["\']([^"\']+)["\']', line):
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
                # require('...')
                for m in re.findall(r'require\(\s*["\']([^"\']+)["\']\s*\)', line):
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
    except Exception:
        pass
    return results


def _parse_py_for_refs(fpath: Path, target: Path, roots: List[str]):
    results = []
    try:
        with fpath.open('r', encoding='utf-8', errors='ignore') as fh:
            for i, line in enumerate(fh, start=1):
                # look for open('path') or Path('...') or literal filename
                for m in re.findall(r"open\(\s*[\"']([^\"']+)[\"']", line):
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
                for m in re.findall(r"Path\(\s*[\"']([^\"']+)[\"']\s*\)", line):
                    resolved = _resolve_reference_path(m, fpath.parent, roots)
                    if resolved and resolved == target:
                        results.append({'path': str(fpath), 'line': i, 'excerpt': line.strip()})
    except Exception:
        pass
    return results


def find_references(target_path: str, roots: Optional[List[str]] = None,
                    max_files: Optional[int] = None,
                    exclude_dirs: Optional[List[str]] = None,
                    exclude_file_patterns: Optional[List[str]] = None) -> List[Dict]:
    target = Path(target_path)
    if not target.exists() or not target.is_file():
        return []
    exclude_dirs = exclude_dirs or []
    exclude_file_patterns = exclude_file_patterns or []

    key = ("ref", str(target.resolve()), tuple(sorted(roots or [])), tuple(sorted(exclude_dirs)), tuple(sorted(exclude_file_patterns)), max_files)
    now = time.time()
    if key in _cache:
        ts, val = _cache[key]
        if now - ts < CACHE_TTL:
            return val

    needle_basename = target.name
    needle_full = str(target.resolve())

    if roots is None:
        roots = [str(Path.home())]

    results = []
    files_scanned = 0
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            # prune directories
            dirnames[:] = [d for d in dirnames if not any(d == ex or fnmatch.fnmatch(d, ex) for ex in exclude_dirs)]
            for fname in filenames:
                # skip file patterns
                if any(fnmatch.fnmatch(fname, pat) for pat in exclude_file_patterns):
                    continue
                fpath = Path(dirpath) / fname
                try:
                    if not fpath.is_file():
                        continue
                    # optional limit
                    files_scanned += 1
                    if max_files and files_scanned > max_files:
                        break
                    if not is_text_file(str(fpath)):
                        continue
                    # try specialized parsers by extension
                    ext = fpath.suffix.lower()
                    parsed = []
                    if ext in ['.html', '.htm']:
                        parsed = _parse_html_for_refs(fpath, Path(target), roots)
                    elif ext in ['.css']:
                        parsed = _parse_css_for_refs(fpath, Path(target), roots)
                    elif ext in ['.js', '.jsx', '.mjs']:
                        parsed = _parse_js_for_refs(fpath, Path(target), roots)
                    elif ext in ['.py']:
                        parsed = _parse_py_for_refs(fpath, Path(target), roots)

                    if parsed:
                        results.extend(parsed)
                        continue

                    try:
                        with open(str(fpath), "r", encoding="utf-8", errors="ignore") as fh:
                            for i, line in enumerate(fh, start=1):
                                if needle_basename in line or needle_full in line:
                                    results.append({
                                        "path": str(fpath),
                                        "line": i,
                                        "excerpt": line.strip(),
                                    })
                                    break
                    except Exception:
                        continue
                except Exception:
                    continue
            else:
                continue
            break

    _cache[key] = (now, results)
    _save_cache()
    return results


def clear_cache():
    _cache.clear()
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    # quick local test
    import sys
    t = sys.argv[1]
    print("hash:", compute_hash(t))
    print("dups:", find_duplicates(t, roots=[str(Path.home())]))
    print("refs:", find_references(t, roots=[str(Path.home())], max_files=1000))
